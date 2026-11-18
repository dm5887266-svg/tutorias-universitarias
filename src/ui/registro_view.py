import tkinter as tk

from src.ui import tema
from src.ui.base import Fichas, boton, campo, ejecutar, enlace
from src.ui.cuaderno import PantallaAcceso
from src.ui.tema import F, px

PASOS = [
    ("1. El tutor publica horarios", "Elige materia, día y hora", ""),
    ("2. Tú pides la tutoría", "Filtra por materia y solicita", ""),
    ("3. El tutor responde", "Acepta o rechaza tu solicitud", ""),
    ("4. Después de la sesión", "Tú la calificas de 1 a 5", ""),
]


class RegistroView(PantallaAcceso):
    def __init__(self, app):
        super().__init__(app, "Así funciona", PASOS)
        self.nombre, self.correo = tk.StringVar(), tk.StringVar()
        self.password, self.rol = tk.StringVar(), tk.StringVar(value="estudiante")
        col = self.columna

        tk.Label(col, text="Crea tu cuenta", font=(tema.SERIF, 24), bg=tema.FONDO, fg=tema.TINTA
                 ).pack(anchor="w", pady=(0, px(20)))

        marco, entrada_nombre = campo(col, "Nombre completo", self.nombre)
        marco.pack(fill="x")
        marco, _ = campo(col, "Correo", self.correo)
        marco.pack(fill="x", pady=(px(14), 0))
        marco, entrada_pass = campo(col, "Contraseña (mínimo 6 caracteres)", self.password, mostrar="•")
        marco.pack(fill="x", pady=(px(14), 0))
        entrada_pass.bind("<Return>", lambda _e: self.registrar())

        tk.Label(col, text="Quiero usar la plataforma como", font=F.pequena, bg=tema.FONDO,
                 fg=tema.TENUE).pack(anchor="w", pady=(px(16), px(4)))
        Fichas(col, self.rol, [("estudiante", "Estudiante", "Busco tutorías"),
                               ("tutor", "Tutor", "Ofrezco tutorías")]).pack(fill="x")

        boton(col, "Crear cuenta", self.registrar, "Primario").pack(fill="x", pady=(px(22), px(14)))
        fila = tk.Frame(col, bg=tema.FONDO)
        fila.pack(anchor="w")
        tk.Label(fila, text="¿Ya tienes cuenta?", font=F.base, bg=tema.FONDO, fg=tema.TENUE
                 ).pack(side="left")
        enlace(fila, "Inicia sesión", lambda: app.mostrar("login")).pack(side="left", padx=(px(6), 0))

        self.after(50, entrada_nombre.focus_set)

    def registrar(self):
        correo = self.correo.get().strip()
        ok, _ = ejecutar(self.app.auth.registrar, self.nombre.get(), self.correo.get(),
                         self.password.get(), self.rol.get())
        if ok:
            self.app.mostrar("login", correo=correo)
            self.app.avisar("Cuenta creada. Ya puedes iniciar sesión.", "exito")
