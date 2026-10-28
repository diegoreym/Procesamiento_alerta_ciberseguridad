
from gestor import GestorAlerta
from ui_alertas import MenuAlertas


def main() -> None:
    gestor = GestorAlerta()
    menu = MenuAlertas(gestor)
    menu.ejecutar()


if __name__ == "__main__":
    main()

