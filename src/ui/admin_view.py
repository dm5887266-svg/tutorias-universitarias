import tkinter as tk
from tkinter import ttk

from src.ui import tema
from src.ui.base import Panel, VistaDashboard, avisar, boton, crear_tabla, ejecutar, llenar_tabla
from src.ui.tema import F, px

PLURALES = {"pendiente": "Pendientes", "aceptada": "Aceptadas", "realizada": "Realizadas",
            "rechazada": "Rechazadas", "cancelada": "Canceladas"}


class AdminView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._por_estado = {}
        self._construir_stats()
        self._construir_materias()
        self.refrescar()
        self.ir_a("stats")

    # --- Estadísticas ---
    def _construir_stats(self):
        p = self.agregar_pagina("stats", "Estadísticas", "Cómo se está usando la plataforma.")
        boton(p.acciones, "Actualizar", self.refrescar, "Suave").pack()

        arriba = tk.Frame(p.cuerpo, bg=tema.FONDO)
        arriba.pack(fill="x")
        arriba.columnconfigure(1, weight=1)

        usuarios = Panel(arriba, "Usuarios")
        usuarios.grid(row=0, column=0, sticky="nsew", padx=(0, px(16)))
        self.lbl_usuarios = {}
        for i, (rol, texto) in enumerate((("estudiante", "Estudiantes"), ("tutor", "Tutores"),
                                          ("admin", "Administradores"))):
            tk.Label(usuarios.interior, text=texto, font=F.base, bg=tema.BLANCO, fg=tema.TENUE
                     ).grid(row=i, column=0, sticky="w", pady=px(3))
            lbl = tk.Label(usuarios.interior, text="0", font=(tema.SERIF, 16), bg=tema.BLANCO, fg=tema.TINTA)
            lbl.grid(row=i, column=1, sticky="e", padx=(px(40), 0))
            self.lbl_usuarios[rol] = lbl
        usuarios.interior.columnconfigure(1, weight=1)

        citas = Panel(arriba, "Citas por estado")
        citas.grid(row=0, column=1, sticky="nsew")
        self.barras = tk.Canvas(citas.interior, height=px(26) * 6, bg=tema.BLANCO, highlightthickness=0)
        self.barras.pack(fill="x")
        self.barras.bind("<Configure>", lambda _e: self._dibujar_barras())

        tk.Label(p.cuerpo, text="Ranking de tutores", font=F.subtitulo, bg=tema.FONDO, fg=tema.TINTA
                 ).pack(anchor="w", pady=(px(22), px(8)))
        marco, self.tabla_r = crear_tabla(
            p.cuerpo, [("tutor", "Tutor", 240, True), ("citas", "Tutorías realizadas", 170),
                       ("promedio", "Promedio", 120)],
            vacio="Todavía no hay tutores con horarios.", alto=5)
        marco.pack(fill="both", expand=True)

    def _dibujar_barras(self):
        c = self.barras
        c.delete("all")
        ancho = c.winfo_width()
        alto_fila, etiqueta_w, numero_w = px(26), px(100), px(36)
        mayor = max(self._por_estado.values(), default=0)
        largo = max(ancho - etiqueta_w - numero_w - px(8), 1)
        for i, estado in enumerate(PLURALES):
            y = i * alto_fila + alto_fila // 2
            n = self._por_estado.get(estado, 0)
            c.create_text(0, y, text=PLURALES[estado], anchor="w", font=F.base, fill=tema.TENUE)
            if n:
                c.create_rectangle(etiqueta_w, y - px(7), etiqueta_w + max(px(4), largo * n / mayor), y + px(7),
                                   fill=tema.COLOR_BARRA[estado], width=0)
            c.create_text(etiqueta_w + max(px(4), largo * n / mayor if mayor else 0) + px(8), y, text=str(n),
                          anchor="w", font=F.negrita, fill=tema.TINTA)
        total = sum(self._por_estado.values())
        c.create_text(ancho, 5 * alto_fila + alto_fila // 2, text=f"{total} en total", anchor="e",
                      font=F.pequena, fill=tema.TENUE)

    # --- Materias ---
    def _construir_materias(self):
        p = self.agregar_pagina("materias", "Materias", "Las materias sobre las que los tutores publican horarios.")
        self.nueva = tk.StringVar()
        entrada = ttk.Entry(p.acciones, textvariable=self.nueva, width=26)
        entrada.pack(side="left", padx=(0, px(8)))
        entrada.bind("<Return>", lambda _e: self.agregar())
        boton(p.acciones, "Agregar materia", self.agregar, "Primario").pack(side="left")
        marco, self.tabla_m = crear_tabla(p.cuerpo, [("nombre", "Materia", 300, True)],
                                          vacio="Aún no hay materias.\nEscribe un nombre arriba para crear la primera.")
        marco.pack(fill="both", expand=True)

    def refrescar(self):
        s = self.svc.estadisticas()
        for rol, lbl in self.lbl_usuarios.items():
            lbl.configure(text=str(s["usuarios_por_rol"].get(rol, 0)))
        self._por_estado = s["citas_por_estado"]
        self._dibujar_barras()
        filas = [{"id": i, "tutor": r["tutor"], "citas": r["citas"],
                  "promedio": f"★ {r['promedio']}" if r["promedio"] else "Sin notas"}
                 for i, r in enumerate(s["ranking_tutores"])]
        llenar_tabla(self.tabla_r, filas, ["tutor", "citas", "promedio"])
        llenar_tabla(self.tabla_m, self.svc.listar_materias(), ["nombre"])

    def agregar(self):
        nombre = self.nueva.get().strip()
        if ejecutar(self.svc.crear_materia, self.nueva.get())[0]:
            self.nueva.set("")
            self.refrescar()
            avisar(f"Materia agregada: {nombre}.", "exito")
