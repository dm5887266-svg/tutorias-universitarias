import tkinter as tk
from tkinter import ttk

from src.ui import tema
from src.ui.base import (VistaDashboard, avisar, boton, crear_tabla, ejecutar, estado_legible,
                         fecha_legible, fila_seleccionada, habilitar, llenar_tabla, nota_legible)
from src.ui.dialogos import confirmar, pedir_calificacion
from src.ui.tema import F, px


class EstudianteView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._construir_buscar()
        self._construir_citas()
        self.refrescar()
        self.ir_a("buscar")

    # --- Buscar tutorías ---
    def _construir_buscar(self):
        p = self.agregar_pagina("buscar", "Buscar tutorías",
                                "Horarios libres de los tutores. Filtra por materia y solicita el que te sirva.")
        tk.Label(p.acciones, text="Materia", font=F.pequena, bg=tema.FONDO, fg=tema.TENUE
                 ).pack(side="left", padx=(0, px(8)))
        self.filtro = tk.StringVar(value="Todas")
        self.combo = ttk.Combobox(p.acciones, textvariable=self.filtro, state="readonly", width=22)
        self.combo.pack(side="left", padx=(0, px(12)))
        self.combo.bind("<<ComboboxSelected>>", lambda _e: self.refrescar())
        self.btn_solicitar = boton(p.acciones, "Solicitar tutoría", self.solicitar, "Primario")
        self.btn_solicitar.pack(side="left")

        marco, self.tabla_disp = crear_tabla(
            p.cuerpo, [("materia", "Materia", 220, True), ("tutor", "Tutor", 200),
                       ("fecha", "Fecha", 160), ("hora", "Hora", 90)])
        marco.pack(fill="both", expand=True)
        self.tabla_disp.bind("<<TreeviewSelect>>", self._botones)

    # --- Mis citas ---
    def _construir_citas(self):
        p = self.agregar_pagina("citas", "Mis citas",
                                "Tus solicitudes y tutorías. Cuando una se realice, podrás calificarla.")
        self.btn_cancelar = boton(p.acciones, "Cancelar cita", self.cancelar, "Peligro")
        self.btn_cancelar.pack(side="left", padx=(0, px(8)))
        self.btn_calificar = boton(p.acciones, "Calificar tutoría", self.calificar, "Primario")
        self.btn_calificar.pack(side="left")

        marco, self.tabla_citas = crear_tabla(
            p.cuerpo, [("materia", "Materia", 200, True), ("tutor", "Tutor", 160),
                       ("fecha", "Fecha", 150), ("hora", "Hora", 80), ("estado", "Estado", 110),
                       ("calificacion", "Nota", 70)],
            vacio="Todavía no tienes citas.\nBusca un horario libre y solicítalo.")
        marco.pack(fill="both", expand=True)
        self.tabla_citas.bind("<<TreeviewSelect>>", self._botones)

    def _botones(self, _evento=None):
        habilitar(self.btn_solicitar, fila_seleccionada(self.tabla_disp) is not None)
        cita = fila_seleccionada(self.tabla_citas)
        habilitar(self.btn_cancelar, bool(cita) and cita["estado"] in ("pendiente", "aceptada"))
        habilitar(self.btn_calificar, bool(cita) and cita["estado"] == "realizada" and not cita["calificacion"])

    def refrescar(self):
        materias = self.svc.listar_materias()
        self._mapa = {m["nombre"]: m["id"] for m in materias}
        self.combo["values"] = ["Todas"] + list(self._mapa)
        materia_id = self._mapa.get(self.filtro.get())
        self.tabla_disp.vacio.configure(
            text="No hay horarios libres para esta materia.\nPrueba con otra o vuelve más tarde."
            if materia_id else "Todavía no hay horarios publicados.")
        llenar_tabla(self.tabla_disp, self.svc.listar_horarios_disponibles(materia_id),
                     ["materia", "tutor", "fecha", "hora"], formato={"fecha": fecha_legible})
        llenar_tabla(self.tabla_citas, self.svc.listar_citas_estudiante(self.usuario.id),
                     ["materia", "tutor", "fecha", "hora", "estado", "calificacion"],
                     formato={"fecha": fecha_legible, "estado": estado_legible,
                              "calificacion": nota_legible},
                     etiqueta=lambda c: c["estado"])
        self._botones()

    # --- Acciones ---
    def solicitar(self):
        h = fila_seleccionada(self.tabla_disp)
        if h and ejecutar(self.svc.agendar_cita, self.usuario.id, h["id"])[0]:
            self.refrescar()
            self.ir_a("citas")
            avisar(f"Solicitud enviada a {h['tutor']}. Falta que la acepte.", "exito")

    def cancelar(self):
        c = fila_seleccionada(self.tabla_citas)
        if not c:
            return
        if confirmar(self, "¿Cancelar la cita?",
                     f"{c['materia']} con {c['tutor']}, {fecha_legible(c['fecha'])} a las {c['hora']}. "
                     "El horario quedará libre para otros estudiantes.",
                     ok="Cancelar cita", peligro=True):
            if ejecutar(self.svc.cancelar_cita, self.usuario.id, c["id"])[0]:
                self.refrescar()
                avisar("Cita cancelada.", "exito")

    def calificar(self):
        c = fila_seleccionada(self.tabla_citas)
        if not c:
            return
        resultado = pedir_calificacion(self, c["materia"], c["tutor"])
        if resultado and ejecutar(self.svc.calificar, self.usuario.id, c["id"], *resultado)[0]:
            self.refrescar()
            avisar("Gracias, tu calificación quedó registrada.", "exito")
