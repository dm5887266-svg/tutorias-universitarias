"""Ventana principal y navegación entre vistas."""
import tkinter as tk

from src.data.database import Database
from src.services.auth_service import AuthService
from src.services.tutoria_service import TutoriaService
from src.ui import base, tema
from src.ui.admin_view import AdminView
from src.ui.estudiante_view import EstudianteView
from src.ui.login_view import LoginView
from src.ui.registro_view import RegistroView
from src.ui.tema import F, px
from src.ui.tutor_view import TutorView

DASHBOARDS = {"estudiante": EstudianteView, "tutor": TutorView, "admin": AdminView}

# tipo de aviso -> (fondo, borde, texto)
_AVISOS = {
    "info": (tema.BLANCO, tema.BORDE, tema.TINTA),
    "exito": (tema.VERDE_FONDO, tema.VERDE, tema.VERDE),
    "error": (tema.ROJO_FONDO, tema.ROJO, tema.ROJO),
}


class App(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.title("Tutorías universitarias")
        tema.aplicar(self)
        ancho, alto = px(1040), px(660)
        self.geometry(f"{ancho}x{alto}+{max((self.winfo_screenwidth() - ancho) // 2, 0)}"
                      f"+{max((self.winfo_screenheight() - alto) // 3, 0)}")
        self.minsize(px(920), px(600))

        self.auth, self.tutorias = AuthService(db), TutoriaService(db)
        self.contenedor = tk.Frame(self, bg=tema.FONDO)
        self.contenedor.pack(fill="both", expand=True)
        self._vista = None
        self._aviso_id = None

        # Aviso flotante: se crea después del contenedor para quedar por encima de él.
        self._aviso = tk.Frame(self, highlightthickness=1)
        self._aviso_texto = tk.Label(self._aviso, font=F.base, justify="left", wraplength=px(560),
                                     padx=px(16), pady=px(10))
        self._aviso_texto.pack()
        self._aviso.bind("<Button-1>", lambda _e: self._ocultar_aviso())
        self._aviso_texto.bind("<Button-1>", lambda _e: self._ocultar_aviso())
        base.registrar_avisador(self.avisar)

        self.mostrar("login")

    def avisar(self, texto, tipo="info"):
        fondo, borde, color = _AVISOS.get(tipo, _AVISOS["info"])
        self._aviso.configure(bg=fondo, highlightbackground=borde)
        self._aviso_texto.configure(text=texto, bg=fondo, fg=color)
        self._aviso.place(relx=0.5, rely=1.0, y=-px(28), anchor="s")
        self._aviso.lift()
        if self._aviso_id:
            self.after_cancel(self._aviso_id)
        self._aviso_id = self.after(6000 if tipo == "error" else 3500, self._ocultar_aviso)

    def _ocultar_aviso(self):
        self._aviso.place_forget()
        if self._aviso_id:
            self.after_cancel(self._aviso_id)
            self._aviso_id = None

    def _reemplazar(self, vista):
        if self._vista is not None:
            self._vista.destroy()
        self._vista = vista
        vista.pack(fill="both", expand=True)

    def mostrar(self, nombre: str, **opciones):
        vistas = {"login": LoginView, "registro": RegistroView}
        self._reemplazar(vistas[nombre](self, **opciones))

    def abrir_dashboard(self, usuario):
        self._ocultar_aviso()
        self._reemplazar(DASHBOARDS[usuario.rol](self, usuario))

    def cerrar_sesion(self):
        self.mostrar("login")
