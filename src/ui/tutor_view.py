import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk

from src.ui import tema
from src.ui.base import (Panel, VistaDashboard, avisar, boton, crear_tabla, ejecutar, estado_legible,
                         fecha_legible, fila_seleccionada, habilitar, llenar_tabla, nota_legible)
from src.ui.dialogos import confirmar
from src.ui.tema import F, px

HORAS = [f"{h:02d}:{m:02d}" for h in range(7, 22) for m in (0, 30)]
DIAS_VISIBLES = 21


class TutorView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._construir_horarios()
        self._construir_solicitudes()
        self.refrescar()
        self.ir_a("horarios")

    # --- Mis horarios ---
    def _construir_horarios(self):
        p = self.agregar_pagina("horarios", "Mis horarios",
                                "Publica los días y horas en que puedes dar tutoría.")
        self.btn_eliminar = boton(p.acciones, "Eliminar horario", self.eliminar, "Peligro")
        self.btn_eliminar.pack()

        form = Panel(p.cuerpo)
        form.pack(fill="x", pady=(0, px(16)))
        fila = form.interior
        hoy = datetime.now().date()
        self._dias = {fecha_legible((hoy + timedelta(days=i)).isoformat()): (hoy + timedelta(days=i)).isoformat()
                      for i in range(DIAS_VISIBLES)}
        self.materia = tk.StringVar()
        self.dia = tk.StringVar(value=fecha_legible((hoy + timedelta(days=1)).isoformat()))
        self.hora = tk.StringVar(value="10:00")

        def columna(i, etiqueta, widget_fn, pad=12):
            marco = tk.Frame(fila, bg=tema.BLANCO)
            marco.grid(row=0, column=i, sticky="w", padx=(0, px(pad)))
            tk.Label(marco, text=etiqueta, font=F.pequena, bg=tema.BLANCO, fg=tema.TENUE).pack(anchor="w")
            w = widget_fn(marco)
            w.pack(anchor="w", pady=(px(4), 0))
            return w

        self.combo = columna(0, "Materia", lambda m: ttk.Combobox(
            m, textvariable=self.materia, state="readonly", width=24))
        columna(1, "Día", lambda m: ttk.Combobox(
            m, textvariable=self.dia, state="readonly", width=18, values=list(self._dias)))
        columna(2, "Hora (24 h, HH:MM)", lambda m: ttk.Combobox(
            m, textvariable=self.hora, width=9, values=HORAS))
        envio = tk.Frame(fila, bg=tema.BLANCO)
        envio.grid(row=0, column=3, sticky="s")
        boton(envio, "Publicar horario", self.publicar, "Primario").pack()

        marco, self.tabla_h = crear_tabla(
            p.cuerpo, [("materia", "Materia", 240, True), ("fecha", "Fecha", 170),
                       ("hora", "Hora", 90), ("estado", "Estado", 120)],
            vacio="Todavía no publicaste horarios.\nElige materia, día y hora arriba.")
        marco.pack(fill="both", expand=True)
        self.tabla_h.bind("<<TreeviewSelect>>", self._botones)

    # --- Solicitudes ---
    def _construir_solicitudes(self):
        p = self.agregar_pagina("solicitudes", "Solicitudes",
                                "Estudiantes que pidieron tus horarios. Responde y marca las sesiones que ya ocurrieron.")
        self.btn_realizada = boton(p.acciones, "Marcar como realizada", lambda: self._cambiar("realizada"), "Suave")
        self.btn_realizada.pack(side="left", padx=(0, px(8)))
        self.btn_rechazar = boton(p.acciones, "Rechazar", lambda: self._cambiar("rechazar"), "Peligro")
        self.btn_rechazar.pack(side="left", padx=(0, px(8)))
        self.btn_aceptar = boton(p.acciones, "Aceptar", lambda: self._cambiar("aceptar"), "Primario")
        self.btn_aceptar.pack(side="left")

        marco, self.tabla_c = crear_tabla(
            p.cuerpo, [("estudiante", "Estudiante", 180, True), ("materia", "Materia", 180),
                       ("fecha", "Fecha", 150), ("hora", "Hora", 80), ("estado", "Estado", 110),
                       ("calificacion", "Nota", 70)],
            vacio="Aún no tienes solicitudes.\nAparecerán aquí cuando un estudiante pida uno de tus horarios.")
        marco.pack(fill="both", expand=True)
        self.tabla_c.bind("<<TreeviewSelect>>", self._botones)

    def _botones(self, _evento=None):
        h = fila_seleccionada(self.tabla_h)
        habilitar(self.btn_eliminar, bool(h) and h["estado"] == "Libre")
        c = fila_seleccionada(self.tabla_c)
        estado = c["estado"] if c else None
        habilitar(self.btn_aceptar, estado == "pendiente")
        habilitar(self.btn_rechazar, estado == "pendiente")
        habilitar(self.btn_realizada, estado == "aceptada")

    def refrescar(self):
        self._materias = {m["nombre"]: m["id"] for m in self.svc.listar_materias()}
        self.combo["values"] = list(self._materias)
        if self._materias and self.materia.get() not in self._materias:
            self.materia.set(next(iter(self._materias)))
        llenar_tabla(self.tabla_h, self.svc.listar_horarios_tutor(self.usuario.id),
                     ["materia", "fecha", "hora", "estado"], formato={"fecha": fecha_legible},
                     etiqueta=lambda h: h["estado"].lower())
        citas = self.svc.listar_citas_tutor(self.usuario.id)
        llenar_tabla(self.tabla_c, citas,
                     ["estudiante", "materia", "fecha", "hora", "estado", "calificacion"],
                     formato={"fecha": fecha_legible, "estado": estado_legible,
                              "calificacion": nota_legible},
                     etiqueta=lambda c: c["estado"])
        self.items["solicitudes"].poner_contador(sum(1 for c in citas if c["estado"] == "pendiente"))
        self._botones()

    # --- Acciones ---
    def publicar(self):
        ok, _ = ejecutar(self.svc.publicar_horario, self.usuario.id,
                         self._materias.get(self.materia.get()), self._dias.get(self.dia.get()),
                         self.hora.get().strip())
        if ok:
            self.refrescar()
            avisar(f"Horario publicado: {self.materia.get()}, {self.dia.get()} a las {self.hora.get().strip()}.",
                   "exito")

    def eliminar(self):
        h = fila_seleccionada(self.tabla_h)
        if not h:
            return
        if confirmar(self, "¿Eliminar el horario?",
                     f"{h['materia']}, {fecha_legible(h['fecha'])} a las {h['hora']}.",
                     ok="Eliminar", peligro=True):
            if ejecutar(self.svc.eliminar_horario, self.usuario.id, h["id"])[0]:
                self.refrescar()
                avisar("Horario eliminado.", "exito")

    def _cambiar(self, accion):
        c = fila_seleccionada(self.tabla_c)
        if not c:
            return
        if accion == "realizada":
            ok = ejecutar(self.svc.marcar_realizada, self.usuario.id, c["id"])[0]
            mensaje = f"Sesión con {c['estudiante']} marcada como realizada."
        else:
            aceptar = accion == "aceptar"
            ok = ejecutar(self.svc.responder_cita, self.usuario.id, c["id"], aceptar)[0]
            mensaje = (f"Aceptaste la solicitud de {c['estudiante']}." if aceptar
                       else f"Rechazaste la solicitud de {c['estudiante']}.")
        if ok:
            self.refrescar()
            avisar(mensaje, "exito")
