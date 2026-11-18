"""Componentes de interfaz reutilizables."""
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk

from src.ui import tema
from src.ui.tema import F, px
from src.utils.errores import AppError

# ---------------------------------------------------------------- avisos
_avisador = None


def registrar_avisador(funcion):
    """La ventana principal registra aquí cómo mostrar los avisos."""
    global _avisador
    _avisador = funcion


def avisar(texto, tipo="info"):
    """Muestra un aviso breve. tipo: 'info', 'exito' o 'error'."""
    if _avisador:
        _avisador(texto, tipo)


def ejecutar(accion, *args, **kwargs):
    """Ejecuta una acción del servicio mostrando los errores al usuario.
    Devuelve (ok, resultado)."""
    try:
        return True, accion(*args, **kwargs)
    except AppError as e:
        avisar(str(e), "error")
    except Exception as e:  # error inesperado: no cerrar la app
        avisar(f"Ocurrió un error inesperado: {e}", "error")
    return False, None


# ---------------------------------------------------------------- formato
_DIAS = ("lun", "mar", "mié", "jue", "vie", "sáb", "dom")
_MESES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def fecha_legible(iso):
    """'2026-11-18' -> 'mié 18 nov' (con '(hoy)' o '(mañana)' cuando aplica)."""
    try:
        f = datetime.strptime(iso, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return iso or ""
    texto = f"{_DIAS[f.weekday()]} {f.day} {_MESES[f.month - 1]}"
    hoy = datetime.now().date()
    if f == hoy:
        texto += " (hoy)"
    elif f == hoy + timedelta(days=1):
        texto += " (mañana)"
    return texto


def estado_legible(estado):
    return tema.ESTADOS.get(estado, (str(estado).capitalize(), tema.TINTA))[0]


def nota_legible(nota):
    return f"★ {nota}" if nota else ""


# ---------------------------------------------------------------- widgets simples
def boton(padre, texto, comando, estilo="Suave", **kw):
    return ttk.Button(padre, text=texto, command=comando, style=f"{estilo}.TButton",
                      cursor="hand2", **kw)


def habilitar(widget, condicion):
    widget.state(["!disabled"] if condicion else ["disabled"])


def campo(padre, etiqueta, variable, mostrar="", ancho=34):
    """Etiqueta arriba y campo de texto debajo. Devuelve (marco, entry)."""
    marco = tk.Frame(padre, bg=tema.FONDO)
    tk.Label(marco, text=etiqueta, font=F.pequena, bg=tema.FONDO, fg=tema.TENUE).pack(anchor="w")
    entrada = ttk.Entry(marco, textvariable=variable, show=mostrar, width=ancho)
    entrada.pack(fill="x", pady=(px(4), 0))
    return marco, entrada


def enlace(padre, texto, comando, fondo=tema.FONDO):
    lbl = tk.Label(padre, text=texto, font=F.negrita, bg=fondo, fg=tema.TINTA, cursor="hand2",
                   takefocus=True)
    lbl.bind("<Button-1>", lambda _: comando())
    lbl.bind("<Return>", lambda _: comando())
    lbl.bind("<space>", lambda _: comando())
    lbl.bind("<Enter>", lambda _: lbl.configure(fg=tema.TINTA_HOVER))
    lbl.bind("<Leave>", lambda _: lbl.configure(fg=tema.TINTA))
    return lbl


class Panel(tk.Frame):
    """Recuadro blanco con borde fino y título opcional. El contenido va en .interior"""

    def __init__(self, padre, titulo=None):
        super().__init__(padre, bg=tema.BLANCO, highlightbackground=tema.BORDE, highlightthickness=1)
        if titulo:
            tk.Label(self, text=titulo, font=F.subtitulo, bg=tema.BLANCO, fg=tema.TINTA
                     ).pack(anchor="w", padx=px(18), pady=(px(14), px(4)))
        self.interior = tk.Frame(self, bg=tema.BLANCO)
        self.interior.pack(fill="both", expand=True, padx=px(18), pady=(px(6), px(16)))


class Fichas(tk.Frame):
    """Selector de una opción entre pocas, con título y detalle. Enlazado a un StringVar."""

    def __init__(self, padre, variable, opciones):
        super().__init__(padre, bg=tema.FONDO)
        self.var = variable
        self._fichas = {}
        for i, (valor, titulo, detalle) in enumerate(opciones):
            ficha = tk.Frame(self, bg=tema.BLANCO, highlightthickness=2, highlightbackground=tema.BORDE,
                             highlightcolor=tema.TINTA, cursor="hand2", takefocus=True)
            ficha.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else px(10), 0))
            self.columnconfigure(i, weight=1, uniform="fichas")
            t = tk.Label(ficha, text=titulo, font=F.negrita, bg=tema.BLANCO, fg=tema.TINTA, anchor="w")
            t.pack(fill="x", padx=px(12), pady=(px(10), 0))
            d = tk.Label(ficha, text=detalle, font=F.pequena, bg=tema.BLANCO, fg=tema.TENUE, anchor="w")
            d.pack(fill="x", padx=px(12), pady=(0, px(10)))
            for w in (ficha, t, d):
                w.bind("<Button-1>", lambda _e, v=valor, f=ficha: (f.focus_set(), variable.set(v)))
            ficha.bind("<space>", lambda _e, v=valor: variable.set(v))
            ficha.bind("<Return>", lambda _e, v=valor: variable.set(v))
            self._fichas[valor] = (ficha, t, d)
        self._traza = variable.trace_add("write", lambda *_: self._pintar())
        self.bind("<Destroy>", lambda _e: self._soltar(), add="+")
        self._pintar()

    def _soltar(self):
        try:
            self.var.trace_remove("write", self._traza)
        except tk.TclError:
            pass

    def _pintar(self):
        for valor, (ficha, t, d) in self._fichas.items():
            sel = self.var.get() == valor
            fondo = tema.RESALTADOR_SUAVE if sel else tema.BLANCO
            ficha.configure(bg=fondo, highlightbackground=tema.TINTA if sel else tema.BORDE)
            t.configure(bg=fondo)
            d.configure(bg=fondo, fg=tema.TINTA if sel else tema.TENUE)


# ---------------------------------------------------------------- tablas
def crear_tabla(padre, columnas, vacio="Sin resultados.", alto=8):
    """Tabla con borde fino y mensaje para cuando no hay filas.

    columnas: lista de (clave, título, ancho[, estirar]). Devuelve (marco, tabla).
    """
    marco = tk.Frame(padre, bg=tema.BLANCO, highlightbackground=tema.BORDE, highlightthickness=1)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="tree headings",
                         height=alto, selectmode="browse")
    # La columna "#0" queda vacía y estrecha: funciona como margen izquierdo de las filas.
    tabla.column("#0", width=px(14), minwidth=px(14), stretch=False)
    tabla.heading("#0", text="")
    for clave, titulo, ancho, *resto in columnas:
        tabla.heading(clave, text=titulo, anchor="w")
        tabla.column(clave, width=px(ancho), minwidth=px(50), anchor="w", stretch=bool(resto and resto[0]))
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    tabla.pack(side="left", fill="both", expand=True)
    for estado, (_, color) in tema.ESTADOS.items():
        tabla.tag_configure(estado, foreground=color)
    tabla.tag_configure("libre", foreground=tema.VERDE)
    tabla.tag_configure("reservado", foreground=tema.AMBAR)
    tabla.vacio = tk.Label(marco, text=vacio, bg=tema.BLANCO, fg=tema.TENUE, font=F.base,
                           justify="center", wraplength=px(360))
    tabla.filas = {}
    return marco, tabla


def llenar_tabla(tabla, filas, claves, formato=None, etiqueta=None):
    """Carga las filas (dicts con 'id'). formato: {clave: función} para mostrar un valor;
    etiqueta: función(fila) -> nombre de tag (color de la fila)."""
    formato = formato or {}
    tabla.delete(*tabla.get_children())
    tabla.filas = {}
    for fila in filas:
        fila = dict(fila)
        iid = str(fila["id"])
        tabla.filas[iid] = fila
        valores = []
        for k in claves:
            v = formato[k](fila[k]) if k in formato else fila[k]
            valores.append("" if v is None else v)
        tag = etiqueta(fila) if etiqueta else ""
        tabla.insert("", "end", iid=iid, values=valores, tags=(tag,) if tag else ())
    if tabla.filas:
        tabla.vacio.place_forget()
    else:
        tabla.vacio.place(relx=0.5, rely=0.55, anchor="center")


def fila_seleccionada(tabla):
    """Devuelve el dict de la fila seleccionada o None."""
    sel = tabla.selection()
    return tabla.filas.get(sel[0]) if sel else None


# ---------------------------------------------------------------- estructura de pantallas
class Pagina(tk.Frame):
    """Una sección del panel: título, descripción, acciones a la derecha y cuerpo."""

    def __init__(self, padre, titulo, detalle):
        super().__init__(padre, bg=tema.FONDO)
        cab = tk.Frame(self, bg=tema.FONDO)
        cab.pack(fill="x", padx=px(32), pady=(px(28), px(18)))
        izq = tk.Frame(cab, bg=tema.FONDO)
        izq.pack(side="left", fill="x", expand=True)
        tk.Label(izq, text=titulo, font=F.titulo, bg=tema.FONDO, fg=tema.TINTA, anchor="w").pack(anchor="w")
        tk.Label(izq, text=detalle, font=F.base, bg=tema.FONDO, fg=tema.TENUE, anchor="w",
                 justify="left", wraplength=px(430)).pack(anchor="w", pady=(px(2), 0))
        self.acciones = tk.Frame(cab, bg=tema.FONDO)
        self.acciones.pack(side="right", anchor="s")
        self.cuerpo = tk.Frame(self, bg=tema.FONDO)
        self.cuerpo.pack(fill="both", expand=True, padx=px(32), pady=(0, px(28)))


class ItemNav(tk.Frame):
    """Entrada de la barra lateral. La activa lleva una marca amarilla a la izquierda."""

    def __init__(self, padre, texto, comando):
        super().__init__(padre, bg=tema.TINTA, cursor="hand2", takefocus=True, highlightthickness=0)
        self.comando, self.activo, self.hover = comando, False, False
        self.marca = tk.Frame(self, width=px(4), bg=tema.TINTA)
        self.marca.pack(side="left", fill="y")
        self.texto = tk.Label(self, text=texto, bg=tema.TINTA, fg=tema.NAV_TEXTO, font=F.base, anchor="w")
        self.texto.pack(side="left", padx=(px(20), 0), pady=px(11))
        self.contador = tk.Label(self, text="", bg=tema.RESALTADOR, fg=tema.TINTA,
                                 font=F.pequena_negrita, padx=px(7))
        for w in (self, self.marca, self.texto, self.contador):
            w.bind("<Button-1>", lambda _e: self.comando())
            w.bind("<Enter>", lambda _e: self._sobre(True))
            w.bind("<Leave>", lambda _e: self.after(20, self._revisar))
        for evento in ("<Return>", "<space>"):
            self.bind(evento, lambda _e: self.comando())
        self.bind("<FocusIn>", lambda _e: self._sobre(True))
        self.bind("<FocusOut>", lambda _e: self._sobre(False))

    def _revisar(self):
        try:
            bajo = self.winfo_containing(*self.winfo_pointerxy())
        except (tk.TclError, KeyError):
            bajo = None
        dentro = bajo is not None and str(bajo).startswith(str(self))
        self._sobre(dentro or self.focus_get() is self)

    def _sobre(self, valor):
        self.hover = valor
        self._pintar()

    def activar(self, valor):
        self.activo = valor
        self._pintar()

    def poner_contador(self, n):
        if n:
            self.contador.configure(text=str(n))
            self.contador.pack(side="right", padx=px(16))
        else:
            self.contador.pack_forget()

    def _pintar(self):
        fondo = tema.NAV_ACTIVO if self.activo else (tema.NAV_HOVER if self.hover else tema.TINTA)
        self.configure(bg=fondo)
        self.texto.configure(bg=fondo, fg=tema.BLANCO if self.activo else tema.NAV_TEXTO)
        self.marca.configure(bg=tema.RESALTADOR if self.activo else fondo)


class VistaDashboard(tk.Frame):
    """Base de los paneles por rol: barra lateral con secciones y usuario, y área de contenido."""

    def __init__(self, app, usuario):
        super().__init__(app.contenedor, bg=tema.FONDO)
        self.app, self.usuario = app, usuario
        self.paginas, self.items, self.actual = {}, {}, None

        lateral = tk.Frame(self, bg=tema.TINTA, width=px(236))
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        self.area = tk.Frame(self, bg=tema.FONDO)
        self.area.pack(side="left", fill="both", expand=True)

        tk.Label(lateral, text="Tutorías", font=F.marca, bg=tema.TINTA, fg=tema.BLANCO, anchor="w"
                 ).pack(fill="x", padx=px(24), pady=(px(28), 0))
        tk.Label(lateral, text="universitarias", font=F.pequena, bg=tema.TINTA, fg=tema.NAV_TEXTO,
                 anchor="w").pack(fill="x", padx=px(24), pady=(0, px(28)))
        self.nav = tk.Frame(lateral, bg=tema.TINTA)
        self.nav.pack(fill="x")

        pie = tk.Frame(lateral, bg=tema.TINTA)
        pie.pack(side="bottom", fill="x", padx=px(24), pady=px(24))
        tk.Label(pie, text=usuario.nombre, font=F.negrita, bg=tema.TINTA, fg=tema.BLANCO, anchor="w",
                 wraplength=px(190), justify="left").pack(fill="x")
        tk.Label(pie, text=usuario.descripcion_rol().split(":")[0], font=F.pequena, bg=tema.TINTA,
                 fg=tema.NAV_TEXTO, anchor="w").pack(fill="x", pady=(0, px(14)))
        salir = tk.Label(pie, text="Cerrar sesión", font=F.base, bg=tema.TINTA, fg=tema.RESALTADOR,
                         cursor="hand2", anchor="w", takefocus=True)
        salir.pack(fill="x")
        salir.bind("<Button-1>", lambda _e: app.cerrar_sesion())
        salir.bind("<Return>", lambda _e: app.cerrar_sesion())
        salir.bind("<Enter>", lambda _e: salir.configure(fg=tema.BLANCO))
        salir.bind("<Leave>", lambda _e: salir.configure(fg=tema.RESALTADOR))

    def agregar_pagina(self, clave, titulo, detalle):
        pagina = Pagina(self.area, titulo, detalle)
        item = ItemNav(self.nav, titulo, lambda: self.ir_a(clave))
        item.pack(fill="x")
        self.paginas[clave], self.items[clave] = pagina, item
        return pagina

    def ir_a(self, clave):
        if self.actual:
            self.paginas[self.actual].pack_forget()
            self.items[self.actual].activar(False)
        self.actual = clave
        self.paginas[clave].pack(fill="both", expand=True)
        self.items[clave].activar(True)
