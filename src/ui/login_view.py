import tkinter as tk

from src.ui import tema
from src.ui.base import boton, campo, ejecutar, enlace, fecha_legible
from src.ui.cuaderno import PantallaAcceso
from src.ui.tema import F, px

CUENTAS_PRUEBA = {
    "Estudiante": ("santiago@tutorias.com", "estudiante123"),
    "Tutor": ("laura@tutorias.com", "tutor123"),
    "Administrador": ("admin@tutorias.com", "admin123"),
}


def _proximos_horarios(app, maximo=8):
    """Horarios libres para escribirlos en la hoja del cuaderno."""
    filas = app.tutorias.listar_horarios_disponibles()[:maximo]
    return [(f["materia"], f["tutor"], f"{fecha_legible(f['fecha'])}, {f['hora']}") for f in filas]


class LoginView(PantallaAcceso):
    def __init__(self, app, correo=""):
        super().__init__(app, "Horarios libres para agendar", _proximos_horarios(app),
                         vacio="Todavía no hay horarios publicados.")
        self.correo = tk.StringVar(value=correo)
        self.password = tk.StringVar()
        col = self.columna

        tk.Label(col, text="Inicia sesión", font=(tema.SERIF, 24), bg=tema.FONDO, fg=tema.TINTA
                 ).pack(anchor="w")
        tk.Label(col, text="Ingresa con tu correo y contraseña.", font=F.base, bg=tema.FONDO,
                 fg=tema.TENUE).pack(anchor="w", pady=(px(2), px(22)))

        marco, entrada_correo = campo(col, "Correo", self.correo)
        marco.pack(fill="x")
        marco, entrada_pass = campo(col, "Contraseña", self.password, mostrar="•")
        marco.pack(fill="x", pady=(px(14), 0))
        entrada_correo.bind("<Return>", lambda _e: entrada_pass.focus_set())
        entrada_pass.bind("<Return>", lambda _e: self.ingresar())

        boton(col, "Ingresar", self.ingresar, "Primario").pack(fill="x", pady=(px(22), px(14)))
        fila = tk.Frame(col, bg=tema.FONDO)
        fila.pack(anchor="w")
        tk.Label(fila, text="¿Todavía no tienes cuenta?", font=F.base, bg=tema.FONDO, fg=tema.TENUE
                 ).pack(side="left")
        enlace(fila, "Crear cuenta", lambda: app.mostrar("registro")).pack(side="left", padx=(px(6), 0))

        tk.Frame(col, bg=tema.BORDE, height=1).pack(fill="x", pady=(px(26), px(14)))
        tk.Label(col, text="Cuentas de prueba (rellenan el formulario)", font=F.pequena, bg=tema.FONDO,
                 fg=tema.TENUE).pack(anchor="w", pady=(0, px(6)))
        botones = tk.Frame(col, bg=tema.FONDO)
        botones.pack(anchor="w")
        for nombre in CUENTAS_PRUEBA:
            boton(botones, nombre, lambda n=nombre: self._rellenar(n), "Chico").pack(
                side="left", padx=(0, px(8)))

        self.after(50, entrada_correo.focus_set)

    def _rellenar(self, nombre):
        self.correo.set(CUENTAS_PRUEBA[nombre][0])
        self.password.set(CUENTAS_PRUEBA[nombre][1])

    def ingresar(self):
        ok, usuario = ejecutar(self.app.auth.iniciar_sesion, self.correo.get(), self.password.get())
        if ok:
            self.app.abrir_dashboard(usuario)
