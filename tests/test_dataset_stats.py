"""La Dataset Card y el README se calculan desde los datos: ninguna tasa va escrita a mano."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUTA_SCRIPT = ROOT / "scripts/dataset_stats.py"


def cargar_script():
    """Carga `scripts/dataset_stats.py` como modulo para reutilizar sus generadores."""
    spec = importlib.util.spec_from_file_location("dataset_stats", RUTA_SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_el_json_de_cifras_coincide_con_los_datos():
    stats = cargar_script().calcular()
    guardado = json.loads((ROOT / "reports/dataset_stats.json").read_text(encoding="utf-8"))
    assert guardado == stats


def test_los_bloques_de_los_documentos_coinciden_con_los_datos():
    modulo = cargar_script()
    stats = modulo.calcular()
    for relativo, bloques in modulo.BLOQUES.items():
        texto = (ROOT / relativo).read_text(encoding="utf-8")
        for nombre, generador in bloques.items():
            inicio = f"<!-- stats:inicio {nombre} -->"
            fin = f"<!-- stats:fin {nombre} -->"
            _, _, resto = texto.partition(inicio)
            contenido, _, _ = resto.partition(fin)
            assert contenido == generador(stats), f"{relativo}: bloque '{nombre}' desfasado"


def test_no_quedan_las_tasas_desfasadas_del_ejercicio_07_anterior():
    for relativo in ("README.md", "docs/DATASET_CARD.md"):
        texto = (ROOT / relativo).read_text(encoding="utf-8")
        assert "23,9 %" not in texto, f"{relativo}: sigue la tasa de prueba desfasada"
        assert "49,6 %" not in texto, f"{relativo}: sigue la tasa de datos completos desfasada"
