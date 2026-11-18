"""Paleta, tipografías y estilos ttk.

Idea visual: un cuaderno de apuntes. Tinta azul de bolígrafo para texto y
botones, hoja rayada con margen rojo en el acceso y resaltador amarillo para
lo que está seleccionado o activo.
"""
import tkinter.font as tkfont
from tkinter import ttk

# --- Paleta -----------------------------------------------------------------
TINTA = "#1D2B4F"          # texto principal, barra lateral, botón primario
TINTA_HOVER = "#2D4075"
TENUE = "#5B6784"          # texto secundario
FONDO = "#F1F3F6"          # fondo de las pantallas
BLANCO = "#FFFFFF"
BORDE = "#D5DAE3"
PAPEL = "#FDFDFB"          # hoja del cuaderno
LINEA_CUADERNO = "#CFE0F1"
MARGEN = "#E58A8A"         # línea de margen del cuaderno
RESALTADOR = "#FFE066"
RESALTADOR_SUAVE = "#FFF3B8"
ROJO = "#B3372D"
ROJO_FONDO = "#FBE4E1"
VERDE = "#23704F"
VERDE_FONDO = "#DDF1E6"
AMBAR = "#7A4B00"
NAV_TEXTO = "#AEB9D6"      # texto de la barra lateral
NAV_ACTIVO = "#2A3C70"
NAV_HOVER = "#243563"
INACTIVO = "#B9C0CF"

# Estado de una cita -> (texto visible, color)
ESTADOS = {
    "pendiente": ("Pendiente", AMBAR),
    "aceptada": ("Aceptada", VERDE),
    "realizada": ("Realizada", TINTA),
    "rechazada": ("Rechazada", ROJO),
    "cancelada": ("Cancelada", TENUE),
}
COLOR_BARRA = {
    "pendiente": "#E8A33D",
    "aceptada": VERDE,
    "realizada": TINTA,
    "rechazada": ROJO,
    "cancelada": "#9AA3B8",
}

# Se rellenan en aplicar(), cuando ya existe la ventana raíz.
K = 1.0
SERIF = "Georgia"
SANS = "Segoe UI"


class F:
    """Fuentes de la aplicación (tkfont.Font) disponibles tras aplicar()."""
    base = pequena = negrita = pequena_negrita = subtitulo = titulo = marca = None


def px(n):
    """Escala un tamaño en píxeles según la densidad de la pantalla."""
    return max(1, int(round(n * K)))


def _elegir(familias, defecto):
    disponibles = {f.lower() for f in tkfont.families()}
    for familia in familias:
        if familia.lower() in disponibles:
            return familia
    return defecto


def fuente_px(familia, tam, estilo=""):
    """Fuente con tamaño en píxeles (para el lienzo del cuaderno)."""
    return tkfont.Font(family=familia, size=-px(tam), weight="bold" if "bold" in estilo else "normal",
                       slant="italic" if "italic" in estilo else "roman")


def aplicar(raiz):
    """Configura fuentes y estilos ttk. Llamar una vez, con la raíz ya creada."""
    global K, SERIF, SANS
    K = max(1.0, raiz.winfo_fpixels("1i") / 96)
    SERIF = _elegir(["Georgia", "Cambria", "Palatino Linotype", "Charter", "DejaVu Serif",
                     "Times New Roman"], "Times")
    SANS = _elegir(["Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Source Sans 3",
                    "DejaVu Sans", "Arial"], "Helvetica")

    F.base = tkfont.Font(family=SANS, size=10)
    F.pequena = tkfont.Font(family=SANS, size=9)
    F.negrita = tkfont.Font(family=SANS, size=10, weight="bold")
    F.pequena_negrita = tkfont.Font(family=SANS, size=9, weight="bold")
    F.subtitulo = tkfont.Font(family=SERIF, size=13)
    F.titulo = tkfont.Font(family=SERIF, size=22)
    F.marca = tkfont.Font(family=SERIF, size=19)

    raiz.configure(bg=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", F.base)
    raiz.option_add("*TCombobox*Listbox.background", BLANCO)
    raiz.option_add("*TCombobox*Listbox.foreground", TINTA)
    raiz.option_add("*TCombobox*Listbox.selectBackground", RESALTADOR)
    raiz.option_add("*TCombobox*Listbox.selectForeground", TINTA)

    s = ttk.Style(raiz)
    s.theme_use("clam")
    s.configure(".", background=FONDO, foreground=TINTA, font=F.base, bordercolor=BORDE)

    # Botones: planos, sin el relieve de clam. Se pintan todos los bordes del mismo color.
    def boton(nombre, fondo, texto, borde, hover, hover_texto=None, pad=(16, 9)):
        est = f"{nombre}.TButton"
        s.configure(est, background=fondo, foreground=texto, bordercolor=borde, lightcolor=fondo,
                    darkcolor=fondo, relief="flat", borderwidth=1, padding=(px(pad[0]), px(pad[1])),
                    font=F.negrita, focuscolor=fondo)
        s.map(est,
              background=[("disabled", FONDO), ("pressed", hover), ("active", hover)],
              foreground=[("disabled", INACTIVO), ("active", hover_texto or texto)],
              bordercolor=[("disabled", BORDE), ("focus", TINTA), ("active", borde)],
              lightcolor=[("disabled", FONDO), ("active", hover)],
              darkcolor=[("disabled", FONDO), ("active", hover)])

    boton("Primario", TINTA, BLANCO, TINTA, TINTA_HOVER)
    boton("Suave", BLANCO, TINTA, BORDE, RESALTADOR_SUAVE)
    boton("Peligro", BLANCO, ROJO, "#E4B4AE", ROJO_FONDO)
    boton("PeligroSolido", ROJO, BLANCO, ROJO, "#962B22")
    boton("Chico", BLANCO, TINTA, BORDE, RESALTADOR_SUAVE, pad=(10, 5))
    s.configure("Chico.TButton", font=F.pequena)

    # Campos de texto
    for nombre in ("TEntry", "TCombobox"):
        s.configure(nombre, fieldbackground=BLANCO, foreground=TINTA, bordercolor=BORDE,
                    lightcolor=BORDE, darkcolor=BORDE, padding=(px(10), px(8)), insertcolor=TINTA)
        s.map(nombre, bordercolor=[("focus", TINTA)], lightcolor=[("focus", TINTA)],
              darkcolor=[("focus", TINTA)])
    s.configure("TCombobox", background=FONDO, arrowcolor=TINTA, arrowsize=px(14))
    s.map("TCombobox", fieldbackground=[("readonly", BLANCO)],
          selectbackground=[("readonly", BLANCO)], selectforeground=[("readonly", TINTA)],
          background=[("active", RESALTADOR_SUAVE)])

    # Tabla
    s.configure("Treeview", background=BLANCO, fieldbackground=BLANCO, foreground=TINTA,
                rowheight=px(36), borderwidth=0, relief="flat", font=F.base)
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    s.map("Treeview", background=[("selected", RESALTADOR)], foreground=[("selected", TINTA)])
    s.configure("Treeview.Heading", background=FONDO, foreground=TENUE, font=F.pequena_negrita,
                relief="flat", borderwidth=0, padding=(px(8), px(9)))
    s.map("Treeview.Heading", background=[("active", FONDO)])

    # Barra de desplazamiento fina y sin flechas
    s.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {
        "sticky": "ns", "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
    s.configure("Vertical.TScrollbar", background=BORDE, troughcolor=BLANCO, bordercolor=BLANCO,
                lightcolor=BORDE, darkcolor=BORDE, width=px(10), arrowsize=px(10))
    s.map("Vertical.TScrollbar", background=[("active", INACTIVO)])
