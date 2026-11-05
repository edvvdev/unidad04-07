"""Quita las marcas de tiempo de ejecución del notebook ejecutado.

Jupyter escribe en cada celda un bloque `metadata.execution` con las horas de ejecución. Son marcas
de entorno, no de resultado: sin ellas el notebook versionado es idéntico byte a byte al que genera
otra máquina y el árbol de trabajo no se ensucia al reejecutar `scripts/run_all.sh`.
"""

from __future__ import annotations

import json
from pathlib import Path

RUTA = Path("notebooks/01_ejercicio07_impacto_equidad.ipynb")


def main() -> None:
    if not RUTA.exists():
        print("No existe:", RUTA)
        return
    cuaderno = json.loads(RUTA.read_text(encoding="utf-8"))
    for celda in cuaderno.get("cells", []):
        celda.get("metadata", {}).pop("execution", None)
        for salida in celda.get("outputs", []):
            salida.get("metadata", {}).pop("execution", None)
    RUTA.write_text(json.dumps(cuaderno, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Marcas de tiempo eliminadas:", RUTA)


if __name__ == "__main__":
    main()
