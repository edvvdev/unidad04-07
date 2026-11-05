"""Genera las figuras de los PDF de entrega a partir de los artefactos de reports/.

Así los PDF no dependen de que se haya ejecutado el notebook: las figuras se pueden
regenerar siempre, incluso con SKIP_NOTEBOOK=1.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from inf8239_u04.data import load_data, temporal_split

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def figura_riesgos() -> None:
    riesgos = pd.read_csv(REPORTS / "lab11/risk_register_scored.csv")
    colores = {"high": "#b91c1c", "medium": "#d97706", "low": "#65a30d"}
    figura, eje = plt.subplots(figsize=(9, 4.6))
    eje.barh(riesgos["id"], riesgos["priority"], color=[colores[r] for r in riesgos["residual"]])
    eje.set_xlabel("Prioridad (probabilidad x impacto)")
    eje.set_title("Riesgos priorizados · color = riesgo residual")
    eje.invert_yaxis()
    eje.grid(axis="x", alpha=0.3)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab11/riesgos_priorizados.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_metricas_grupo() -> None:
    log = pd.read_csv(REPORTS / "lab12/logistic/fairness_by_group.csv", index_col=0)
    tree = pd.read_csv(REPORTS / "lab12/tree/fairness_by_group.csv", index_col=0)
    figura, (eje1, eje2) = plt.subplots(1, 2, figsize=(13, 4.8))
    for eje, (nombre, tabla) in zip([eje1, eje2], [("Logística", log), ("Árbol", tree)]):
        x = np.arange(len(tabla))
        ancho = 0.35
        eje.bar(x - ancho / 2, tabla["recall"], ancho, label="recall", color="#0f7c7b")
        eje.bar(x + ancho / 2, tabla["fpr"], ancho, label="FPR", color="#b45309")
        for i, (r, f) in enumerate(zip(tabla["recall"], tabla["fpr"])):
            eje.text(i - ancho / 2, r + 0.02, f"{r:.2f}", ha="center", fontsize=8)
            eje.text(i + ancho / 2, f + 0.02, f"{f:.2f}", ha="center", fontsize=8)
        eje.set_xticks(x, [f"{nombre_grupo}\n(n={int(n)})" for nombre_grupo, n in zip(tabla.index, tabla["count"])])
        eje.set_ylim(0, 1)
        eje.set_ylabel("tasa")
        eje.set_title(f"{nombre} · recall y FPR por grupo")
        eje.legend(fontsize=8)
        eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab12/metricas_por_grupo.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_recall_interseccional() -> None:
    inter = pd.read_csv(REPORTS / "lab12/logistic/fairness_intersectional.csv", index_col=0)
    insuficiente = inter["soporte_insuficiente"].astype(str).str.lower().eq("true")
    figura, eje = plt.subplots(figsize=(10, 5))
    colores = ["#b91c1c" if s else "#0f7c7b" for s in insuficiente]
    eje.bar(inter.index, inter["recall"], color=colores)
    for i, (c, r) in enumerate(zip(inter["count"], inter["recall"])):
        eje.text(i, r + 0.02, f"n={int(c)}", ha="center", fontsize=8)
    eje.set_ylabel("recall")
    eje.set_title("Recall interseccional (grupo | banda de edad) · rojo = soporte insuficiente")
    eje.tick_params(axis="x", rotation=30)
    eje.set_ylim(0, 1.15)
    eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab12/recall_interseccional.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_utilidad_brecha() -> None:
    log = json.loads((REPORTS / "lab12/logistic/global_metrics.json").read_text(encoding="utf-8"))
    tree = json.loads((REPORTS / "lab12/tree/global_metrics.json").read_text(encoding="utf-8"))
    figura, eje = plt.subplots(figsize=(8.5, 4.6))
    for nombre, datos, color in [("Logística", log, "#0f7c7b"), ("Árbol", tree, "#b45309")]:
        eje.scatter(datos["differences"]["recall"], datos["metrics"]["recall"], s=170, color=color)
        eje.annotate(nombre, (datos["differences"]["recall"], datos["metrics"]["recall"]),
                     textcoords="offset points", xytext=(8, 6), fontsize=9)
    eje.set_xlabel("Brecha de recall entre grupos (menor es mejor)")
    eje.set_ylabel("Recall global (mayor es mejor)")
    eje.set_title("Utilidad frente a brecha: la logística domina al árbol")
    eje.grid(alpha=0.25)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab12/utilidad_vs_brecha.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_tasas_base() -> None:
    datos = load_data()
    _, prueba = temporal_split(datos)
    grupos = ["G1", "G2"]
    completos = [100.0 * datos.loc[datos.protected_group == g, "target"].mean() for g in grupos]
    prueba_pct = [100.0 * prueba.loc[prueba.protected_group == g, "target"].mean() for g in grupos]
    x = np.arange(len(grupos))
    ancho = 0.35
    figura, eje = plt.subplots(figsize=(8.5, 4.4))
    eje.bar(x - ancho / 2, completos, ancho, label=f"datos completos (n={len(datos)})", color="#94a3b8")
    eje.bar(x + ancho / 2, prueba_pct, ancho, label=f"prueba (corte temporal, n={len(prueba)})", color="#0f7c7b")
    for i, (completo, parcial) in enumerate(zip(completos, prueba_pct)):
        eje.text(i - ancho / 2, completo + 1, f"{completo:.1f} %", ha="center", fontsize=9)
        eje.text(i + ancho / 2, parcial + 1, f"{parcial:.1f} %", ha="center", fontsize=9)
    eje.set_xticks(x, grupos)
    eje.set_ylabel("tasa base de positivos (%)")
    eje.set_title("Tasa base de positivos por grupo (prevalencia del target)")
    eje.set_ylim(0, 100)
    eje.legend(fontsize=9)
    eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab12/tasas_base_positivos.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_raci() -> None:
    raci = pd.read_csv(ROOT / "student_inputs/raci.csv")
    conteo = raci["A"].value_counts()
    figura, eje = plt.subplots(figsize=(9, 4))
    eje.barh(conteo.index, conteo.values, color="#b45309")
    for y, v in enumerate(conteo.values):
        eje.text(v + 0.06, y, str(v), va="center", fontsize=9)
    eje.set_xlabel("Actividades con ese rol como responsable final (A)")
    eje.set_title("Distribución de responsabilidad final por rol")
    eje.set_xlim(0, conteo.max() + 0.8)
    eje.grid(axis="x", alpha=0.3)
    figura.tight_layout()
    figura.savefig(REPORTS / "lab13/raci_responsables.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def figura_puertas() -> None:
    decision = json.loads((REPORTS / "lab13/deployment_decision.json").read_text(encoding="utf-8"))
    puertas = decision["decision"]["checks"]
    figura, eje = plt.subplots(figsize=(9, 4.4))
    eje.barh(list(puertas), [1 if v else 0 for v in puertas.values()],
             color=["#15803d" if v else "#b91c1c" for v in puertas.values()])
    for y, (k, v) in enumerate(puertas.items()):
        eje.text(1.02, y, "correcta" if v else "FALLA", va="center", fontsize=9,
                 color="#15803d" if v else "#b91c1c")
    eje.set_xlim(0, 1.35)
    eje.set_xticks([])
    eje.set_title(f"Puertas de calidad del despliegue · estado {decision['decision']['status']}")
    eje.invert_yaxis()
    figura.tight_layout()
    figura.savefig(REPORTS / "lab13/puertas_calidad.png", dpi=170, bbox_inches="tight")
    plt.close(figura)


def main() -> None:
    generadores = [
        ("lab11/riesgos_priorizados.png", figura_riesgos),
        ("lab12/metricas_por_grupo.png", figura_metricas_grupo),
        ("lab12/recall_interseccional.png", figura_recall_interseccional),
        ("lab12/utilidad_vs_brecha.png", figura_utilidad_brecha),
        ("lab12/tasas_base_positivos.png", figura_tasas_base),
        ("lab13/raci_responsables.png", figura_raci),
        ("lab13/puertas_calidad.png", figura_puertas),
    ]
    for nombre, funcion in generadores:
        try:
            funcion()
            print("OK   ", nombre)
        except (OSError, KeyError, ValueError, TypeError, AttributeError) as error:
            print("FALTA", nombre, "->", type(error).__name__, error)


if __name__ == "__main__":
    main()
