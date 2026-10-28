import json
from pathlib import Path
from random import Random

from modelos import Alerta


CARPETA_DATOS: Path = Path(__file__).resolve().parent.parent / "datos"


def cargar_alertas(ruta: str | Path | None = None) -> list[Alerta]:
    archivo = Path(ruta) if ruta is not None else CARPETA_DATOS / "alertas_iniciales.json"
    with archivo.open(encoding="utf-8") as entrada:
        registros = json.load(entrada)

    if not isinstance(registros, list):
        raise ValueError("El archivo debe contener una lista de alertas")

    campos = {"id", "sistema", "descripcion", "riesgo", "instante"}
    alertas: list[Alerta] = []
    ids: set[int] = set()

    for numero, registro in enumerate(registros, start=1):
        if not isinstance(registro, dict) or set(registro) != campos:
            raise ValueError(f"Campos incorrectos en el registro {numero}")

        alerta = Alerta(
            registro["id"], registro["sistema"], registro["descripcion"],
            registro["riesgo"], registro["instante"],
        )
        if alerta.id in ids:
            raise ValueError(f"Id repetido en los datos: {alerta.id}")
        ids.add(alerta.id)
        alertas.append(alerta)

    return alertas


def generar_alertas(n: int, semilla: int = 2026) -> list[Alerta]:
    if type(n) is not int:
        raise TypeError("La cantidad debe ser un entero")
    if n < 0:
        raise ValueError("La cantidad no puede ser negativa")
    if type(semilla) is not int:
        raise TypeError("La semilla debe ser un entero")

    generador = Random(semilla)
    sistemas = ("Correo", "ERP", "Web", "BD", "VPN", "Archivos")
    alertas: list[Alerta] = []

    # Los ids salen ordenados; el experimento decide si los permuta.
    for id in range(1, n + 1):
        alertas.append(Alerta(
            id, generador.choice(sistemas), f"Alerta simulada {id}",
            generador.randint(1, 10), id,
        ))

    return alertas


def generar_archivos(
    semilla: int = 2026, carpeta: str | Path | None = None
) -> list[Path]:
    destino = Path(carpeta) if carpeta is not None else CARPETA_DATOS
    destino.mkdir(parents=True, exist_ok=True)
    archivos: list[Path] = []

    for n in (100, 500, 1000):
        registros = [
            {
                "id": alerta.id,
                "sistema": alerta.sistema,
                "descripcion": alerta.descripcion,
                "riesgo": alerta.riesgo,
                "instante": alerta.instante,
            }
            for alerta in generar_alertas(n, semilla)
        ]
        archivo = destino / f"alertas_{n}.json"
        with archivo.open("w", encoding="utf-8") as salida:
            json.dump(registros, salida, ensure_ascii=False, indent=2)
        archivos.append(archivo)

    return archivos


if __name__ == "__main__":
    for archivo in generar_archivos():
        print(f"Generado: {archivo}")

