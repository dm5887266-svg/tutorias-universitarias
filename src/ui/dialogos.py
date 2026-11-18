"""Diálogos modales propios (reemplazan a messagebox y simpledialog para mantener el estilo)."""
import tkinter as tk

from src.ui import tema
from src.ui.base import boton
from src.ui.tema import F, px


class _Dialogo(tk.Toplevel):
    def __init__(self, maestro, titulo):
        super().__init__(maestro, bg=tema.BLANCO)
        self.title(titulo)
        self.resizable(False, False)
        self.transient(maestro.winfo_toplevel())
        self.resultado = None
        self.cuerpo = tk.Frame(self, bg=tema.BLANCO)
        self.cuerpo.pack(fill="both", expand=True, padx=px(28), pady=px(24))
        self.bind("<Escape>", lambda _e: self.destroy())

    def mostrar(self):
        """Centra el diálogo sobre la ventana, lo bloquea y devuelve el resultado."""
        self.update_idletasks()
        raiz = self.master.winfo_toplevel()
        x = raiz.winfo_rootx() + (raiz.winfo_width() - self.winfo_reqwidth()) // 2
        y = raiz.winfo_rooty() + (raiz.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass
        self.wait_window()
        return self.resultado


def _filas_botones(d):
    fila = tk.Frame(d.cuerpo, bg=tema.BLANCO)
    fila.pack(anchor="e", pady=(px(22), 0))
    return fila


def confirmar(maestro, titulo, texto, ok="Confirmar", peligro=False):
    """Pide confirmación. Devuelve True si la persona acepta."""
    d = _Dialogo(maestro, titulo)
    tk.Label(d.cuerpo, text=titulo, font=F.subtitulo, bg=tema.BLANCO, fg=tema.TINTA, anchor="w"
             ).pack(anchor="w")
    tk.Label(d.cuerpo, text=texto, font=F.base, bg=tema.BLANCO, fg=tema.TENUE, justify="left",
             wraplength=px(340)).pack(anchor="w", pady=(px(8), 0))
    fila = _filas_botones(d)
    boton(fila, "Volver", d.destroy, "Suave").pack(side="left", padx=(0, px(8)))

    def aceptar():
        d.resultado = True
        d.destroy()

    principal = boton(fila, ok, aceptar, "PeligroSolido" if peligro else "Primario")
    principal.pack(side="left")
    principal.focus_set()
    d.bind("<Return>", lambda _e: aceptar())
    return bool(d.mostrar())


_LEYENDAS = {1: "Mala", 2: "Regular", 3: "Buena", 4: "Muy buena", 5: "Excelente"}
_ORO = "#D99A00"


def pedir_calificacion(maestro, materia, tutor):
    """Pide puntaje (1 a 5) y comentario. Devuelve (puntaje, comentario) o None."""
    d = _Dialogo(maestro, "Calificar tutoría")
    tk.Label(d.cuerpo, text=f"¿Cómo te fue en {materia}?", font=F.subtitulo, bg=tema.BLANCO,
             fg=tema.TINTA, anchor="w", wraplength=px(340), justify="left").pack(anchor="w")
    tk.Label(d.cuerpo, text=f"Tutoría con {tutor}", font=F.base, bg=tema.BLANCO, fg=tema.TENUE
             ).pack(anchor="w", pady=(px(2), px(16)))

    estado = {"puntaje": 0}
    fila_estrellas = tk.Frame(d.cuerpo, bg=tema.BLANCO, takefocus=True, highlightthickness=1,
                              highlightbackground=tema.BLANCO, highlightcolor=tema.TINTA)
    fila_estrellas.pack(anchor="w")
    leyenda = tk.Label(d.cuerpo, text="Toca una estrella para elegir", font=F.pequena,
                       bg=tema.BLANCO, fg=tema.TENUE)
    leyenda.pack(anchor="w", pady=(px(4), px(14)))
    estrellas = []

    def pintar(n):
        for i, lbl in enumerate(estrellas, start=1):
            lbl.configure(text="★" if i <= n else "☆", fg=_ORO if i <= n else tema.INACTIVO)

    def mostrar_leyenda(n):
        leyenda.configure(text=f"{n} de 5: {_LEYENDAS[n]}" if n else "Toca una estrella para elegir")

    def elegir(n):
        estado["puntaje"] = max(1, min(5, n))
        pintar(estado["puntaje"])
        mostrar_leyenda(estado["puntaje"])
        enviar.state(["!disabled"])

    def sobre(n):
        pintar(n)
        mostrar_leyenda(n)

    def fuera():
        pintar(estado["puntaje"])
        mostrar_leyenda(estado["puntaje"])

    for n in range(1, 6):
        lbl = tk.Label(fila_estrellas, text="☆", font=(tema.SANS, 24), bg=tema.BLANCO, fg=tema.INACTIVO,
                       cursor="hand2", padx=px(2))
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda _e, n=n: (fila_estrellas.focus_set(), elegir(n)))
        lbl.bind("<Enter>", lambda _e, n=n: sobre(n))
        lbl.bind("<Leave>", lambda _e: fuera())
        estrellas.append(lbl)
    fila_estrellas.bind("<Right>", lambda _e: elegir(estado["puntaje"] + 1))
    fila_estrellas.bind("<Left>", lambda _e: elegir(estado["puntaje"] - 1))
    for n in range(1, 6):
        fila_estrellas.bind(str(n), lambda _e, n=n: elegir(n))

    tk.Label(d.cuerpo, text="Comentario (opcional)", font=F.pequena, bg=tema.BLANCO, fg=tema.TENUE
             ).pack(anchor="w")
    comentario = tk.Text(d.cuerpo, width=42, height=4, font=F.base, wrap="word", relief="flat",
                         bg=tema.BLANCO, fg=tema.TINTA, insertbackground=tema.TINTA,
                         highlightthickness=1, highlightbackground=tema.BORDE,
                         highlightcolor=tema.TINTA, padx=px(8), pady=px(6))
    comentario.pack(anchor="w", pady=(px(4), 0))

    fila = _filas_botones(d)
    boton(fila, "Cancelar", d.destroy, "Suave").pack(side="left", padx=(0, px(8)))

    def enviar_ahora():
        d.resultado = (estado["puntaje"], comentario.get("1.0", "end").strip())
        d.destroy()

    enviar = boton(fila, "Enviar calificación", enviar_ahora, "Primario")
    enviar.pack(side="left")
    enviar.state(["disabled"])
    fila_estrellas.focus_set()
    return d.mostrar()
