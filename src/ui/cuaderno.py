"""Pantalla de acceso: hoja de cuaderno rayado a la izquierda y formulario a la derecha."""
import tkinter as tk

from src.ui import tema
from src.ui.tema import fuente_px, px


class Cuaderno(tk.Canvas):
    """Hoja rayada con margen rojo. El texto se escribe apoyado en las líneas.

    entradas: lista de (principal, secundario, derecha). Cada una ocupa dos líneas.
    """

    PASO = 34  # separación entre líneas, en píxeles base

    def __init__(self, padre, subtitulo, entradas, vacio=""):
        super().__init__(padre, width=px(410), bg=tema.PAPEL, highlightthickness=0)
        self.subtitulo, self.entradas, self.vacio = subtitulo, entradas, vacio
        self._fuentes = {}
        self.bind("<Configure>", lambda _e: self._dibujar())

    def _fuente(self, familia, tam, estilo=""):
        clave = (familia, tam, estilo)
        if clave not in self._fuentes:
            self._fuentes[clave] = fuente_px(familia, tam, estilo)
        return self._fuentes[clave]

    def _escribir(self, linea, x, texto, fuente, color, ancla="sw"):
        """Escribe con la base del texto 3 px por encima de la línea indicada."""
        y = linea * px(self.PASO) - px(3) + fuente.metrics("descent")
        self.create_text(x, y, text=texto, font=fuente, fill=color, anchor=ancla)

    def _dibujar(self):
        self.delete("all")
        ancho, alto = self.winfo_width(), self.winfo_height()
        paso, margen = px(self.PASO), px(64)
        lineas = alto // paso
        for n in range(1, lineas + 1):
            self.create_line(0, n * paso, ancho, n * paso, fill=tema.LINEA_CUADERNO)
        self.create_line(margen, 0, margen, alto, fill=tema.MARGEN, width=max(1, px(1)))

        x = margen + px(22)
        derecha = ancho - px(22)
        self._escribir(2, x, "Tutorías", self._fuente(tema.SERIF, 38), tema.TINTA)
        self._escribir(3, x, "universitarias", self._fuente(tema.SERIF, 24, "italic"), tema.TENUE)
        self._escribir(5, x, self.subtitulo, self._fuente(tema.SANS, 13), tema.TENUE)

        linea = 7
        if not self.entradas:
            self._escribir(linea, x, self.vacio, self._fuente(tema.SANS, 14), tema.TENUE)
            return
        for principal, secundario, lado in self.entradas:
            if linea + 1 >= lineas:  # no dejar texto pegado al borde inferior
                break
            self._escribir(linea, x, principal, self._fuente(tema.SANS, 16, "bold"), tema.TINTA)
            if secundario:
                self._escribir(linea + 1, x, secundario, self._fuente(tema.SANS, 13), tema.TENUE)
            if lado:
                self._escribir(linea + 1, derecha, lado, self._fuente(tema.SANS, 13), tema.TENUE, "se")
            linea += 2


class PantallaAcceso(tk.Frame):
    """Estructura común de inicio de sesión y registro. El formulario va en self.columna."""

    def __init__(self, app, subtitulo, entradas, vacio=""):
        super().__init__(app.contenedor, bg=tema.FONDO)
        self.app = app
        Cuaderno(self, subtitulo, entradas, vacio).pack(side="left", fill="y")
        lado = tk.Frame(self, bg=tema.FONDO)
        lado.pack(side="left", fill="both", expand=True)
        self.columna = tk.Frame(lado, bg=tema.FONDO)
        self.columna.place(relx=0.5, rely=0.5, anchor="center")
