"""Punto de entrada: python main.py"""
from src.data.database import Database
from src.data.seed import cargar_datos_ejemplo
from src.ui.app import App


def _pantalla_nitida():
    """En Windows evita que el sistema estire la ventana (se ve borrosa en pantallas con escala)."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass


def main():
    _pantalla_nitida()
    db = Database()
    cargar_datos_ejemplo(db)
    App(db).mainloop()
    db.cerrar()


if __name__ == "__main__":
    main()
