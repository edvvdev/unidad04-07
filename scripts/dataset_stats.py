"""Distribucion del dataset y tasas base de positivos, calculadas desde los datos.

Genera `reports/dataset_stats.json` (corte temporal, distribucion del objetivo, recuentos por
grupo, banda de edad y zona, y tasas de positivos en los datos completos y en la prueba) y
actualiza los bloques marcados de `docs/DATASET_CARD.md` y `README.md`. Asi ninguna de esas cifras
queda escrita a mano y no puede desincronizarse de `data/territorial_risk_synthetic.csv`.

Uso: `uv run python scripts/dataset_stats.py`
"""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

import pandas as pd

from inf8239_u04.data import load_data, temporal_split

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SALIDA = REPORTS / "dataset_stats.json"

# Orden de presentacion de las categorias (las cifras se calculan, el orden es de lectura).
BANDAS_ORDEN = ["18-29", "30-44", "45-59", "60+"]
ZONAS_ORDEN = ["Norte", "Oeste", "Sur", "Este"]

ANCHO_LINEA = 100


def porcentaje(valor: float) -> str:
    """0.497474 -> '49,7 %' (coma decimal, como en el resto de la documentacion)."""
    return f"{valor * 100:.1f} %".replace(".", ",")


def envolver(texto: str, ancho: int = ANCHO_LINEA) -> str:
    """Ajusta el texto a un ancho de linea sin partir los tramos en negrita.

    Los tramos en negrita se sustituyen por un marcador de la misma longitud, para que el ajuste de
    linea mida el texto final y no el marcador.
    """
    tramos: list[str] = []

    def guardar(marco: re.Match[str]) -> str:
        original = marco.group(0)
        indice = len(tramos)
        tramos.append(original)
        base = f"\x00{indice}\x00"
        return base + "\x01" * (len(original) - len(base))

    protegido = re.sub(r"\*\*[^*]+\*\*", guardar, texto)
    lineas = []
    for parrafo in protegido.strip().split("\n"):
        lineas.append(textwrap.fill(parrafo, width=ancho, break_long_words=False))
    salida = "\n".join(lineas)
    for indice, tramo in enumerate(tramos):
        base = f"\x00{indice}\x00"
        salida = salida.replace(base + "\x01" * (len(tramo) - len(base)), tramo)
    return salida + "\n"


def tasas_por_grupo(frame: pd.DataFrame) -> dict:
    """n, positivos y tasa de positivos de cada grupo protegido."""
    salida = {}
    for grupo, bloque in frame.groupby("protected_group"):
        positivos = int(bloque["target"].sum())
        total = len(bloque)
        salida[str(grupo)] = {
            "n": total,
            "positivos": positivos,
            "tasa": positivos / total if total else 0.0,
        }
    return dict(sorted(salida.items()))


def conteos(frame: pd.DataFrame, columna: str, orden: list[str]) -> dict:
    """Recuento de filas por categoria, en el orden de presentacion."""
    return {categoria: int((frame[columna] == categoria).sum()) for categoria in orden}


def calcular() -> dict:
    """Calcula todas las cifras del dataset a partir del CSV sintetico."""
    df = load_data()
    train, test = temporal_split(df)
    positivos = int(df["target"].sum())
    return {
        "ruta": "data/territorial_risk_synthetic.csv",
        "filas": len(df),
        "columnas": len(df.columns),
        "corte_temporal": {
            "entrenamiento_hasta": str(train["received_date"].max().date()),
            "prueba_desde": str(test["received_date"].min().date()),
            "filas_entrenamiento": len(train),
            "filas_prueba": len(test),
        },
        "objetivo": {
            "positivos": positivos,
            "negativos": int(len(df) - positivos),
            "tasa_positivos": positivos / len(df),
            "tasa_negativos": 1.0 - positivos / len(df),
        },
        "grupos": tasas_por_grupo(df),
        "grupos_prueba": tasas_por_grupo(test),
        "bandas_edad": conteos(df, "age_band", BANDAS_ORDEN),
        "zonas": conteos(df, "zone", ZONAS_ORDEN),
    }


def celdas_tasas(grupos: dict) -> str:
    """'G1 49,7 % · **G2 63,9 %**': en negrita el grupo con la tasa mas alta."""
    mayor = max(grupos, key=lambda grupo: grupos[grupo]["tasa"])
    partes = []
    for grupo, datos in grupos.items():
        texto = f"{grupo} {porcentaje(datos['tasa'])}"
        partes.append(f"**{texto}**" if grupo == mayor else texto)
    return " · ".join(partes)


def bloque_distribucion(stats: dict) -> str:
    """Tabla 'Distribucion y soporte' de la Dataset Card."""
    objetivo = stats["objetivo"]
    grupos = stats["grupos"]
    prueba = stats["grupos_prueba"]
    filas_prueba = stats["corte_temporal"]["filas_prueba"]
    conteo_grupos = " · ".join(f"{grupo} {datos['n']}" for grupo, datos in grupos.items())
    conteo_bandas = " · ".join(f"{banda}: {n}" for banda, n in stats["bandas_edad"].items())
    conteo_zonas = " · ".join(f"{zona} {n}" for zona, n in stats["zonas"].items())
    filas = [
        (
            f"| Target | {objetivo['positivos']} positivos ({porcentaje(objetivo['tasa_positivos'])}) · "
            f"{objetivo['negativos']} negativos ({porcentaje(objetivo['tasa_negativos'])}): desbalance "
            "moderado, `accuracy` no basta |"
        ),
        f"| Grupos | {conteo_grupos} |",
        f"| Bandas de edad | {conteo_bandas} |",
        f"| Zonas | {conteo_zonas} |",
        f"| Tasa de positivos por grupo (datos completos) | {celdas_tasas(grupos)} |",
        f"| Tasa de positivos por grupo (prueba, {filas_prueba} casos) | {celdas_tasas(prueba)} |",
    ]
    return "\n" + "\n".join(filas) + "\n"


def bloque_rates(stats: dict) -> str:
    """Parrafo del README con las tasas base de positivos."""
    completos = stats["grupos"]
    prueba = stats["grupos_prueba"]
    filas_prueba = stats["corte_temporal"]["filas_prueba"]
    texto = envolver(
        "Tasa base de positivos (calculada desde `data/territorial_risk_synthetic.csv` con el corte "
        f"temporal del repo): G1 **{porcentaje(completos['G1']['tasa'])}** frente a G2 "
        f"**{porcentaje(completos['G2']['tasa'])}** en los datos completos, y G1 "
        f"**{porcentaje(prueba['G1']['tasa'])}** frente a G2 **{porcentaje(prueba['G2']['tasa'])}** "
        f"en la prueba de {filas_prueba} registros."
    )
    return "\n" + texto + "\n"


def bloque_rates_decision(stats: dict) -> str:
    """Fragmento del README con las tasas que sostienen la decision (se inserta en linea)."""
    completos = stats["grupos"]
    return (
        f"G2 {porcentaje(completos['G2']['tasa'])} frente a G1 "
        f"{porcentaje(completos['G1']['tasa'])}"
    )


BLOQUES = {
    "docs/DATASET_CARD.md": {"distribucion": bloque_distribucion},
    "README.md": {"rates": bloque_rates, "rates_decision": bloque_rates_decision},
}


def actualizar_bloque(ruta: Path, nombre: str, contenido: str) -> None:
    """Reemplaza el contenido marcado con `nombre` por el contenido generado."""
    texto = ruta.read_text(encoding="utf-8")
    inicio = f"<!-- stats:inicio {nombre} -->"
    fin = f"<!-- stats:fin {nombre} -->"
    if inicio not in texto or fin not in texto:
        raise ValueError(f"Bloque '{nombre}' no encontrado en {ruta}")
    cabeza, _, resto = texto.partition(inicio)
    _, _, cola = resto.partition(fin)
    ruta.write_text(f"{cabeza}{inicio}{contenido}{fin}{cola}", encoding="utf-8")


def main() -> None:
    stats = calcular()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print("dataset_stats:", SALIDA)
    for relativo, bloques in BLOQUES.items():
        for nombre, generador in bloques.items():
            actualizar_bloque(ROOT / relativo, nombre, generador(stats))
            print("  bloque actualizado:", relativo, nombre)


if __name__ == "__main__":
    main()
