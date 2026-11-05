"""Genera el PDF de síntesis del Ejercicio 07 (impacto y equidad)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from inf8239_u04.data import load_data, temporal_split

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-07")
# Fecha fija de la entrega: reportlab respeta SOURCE_DATE_EPOCH, asi que el PDF sale byte a byte
# identico en cada ejecucion y su metadato de creacion es siempre el mismo.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1793620800")

logistic = json.loads((REPORTS / "lab12/logistic/global_metrics.json").read_text(encoding="utf-8"))
tree = json.loads((REPORTS / "lab12/tree/global_metrics.json").read_text(encoding="utf-8"))
grupos_log = pd.read_csv(REPORTS / "lab12/logistic/fairness_by_group.csv", index_col=0)
grupos_tree = pd.read_csv(REPORTS / "lab12/tree/fairness_by_group.csv", index_col=0)
inter = pd.read_csv(REPORTS / "lab12/logistic/fairness_intersectional.csv", index_col=0)
riesgos = pd.read_csv(REPORTS / "lab11/risk_register_scored.csv")
stake = pd.read_csv(REPORTS / "lab11/stakeholders.csv")
decision = yaml.safe_load((ROOT / "student_inputs/lab12_decision.yml").read_text(encoding="utf-8"))
impacto = yaml.safe_load((ROOT / "student_inputs/lab11_impact.yml").read_text(encoding="utf-8"))
gates = yaml.safe_load((ROOT / "configs/governance.yml").read_text(encoding="utf-8"))["gates"]

ANCHO = 18.59
RUTA_DECISION = REPORTS / "lab13/deployment_decision.json"
if not RUTA_DECISION.exists():
    raise SystemExit(
        "Falta reports/lab13/deployment_decision.json: ejecuta "
        "`uv run python scripts/lab13_governance.py` antes de construir el PDF."
    )
despliegue = json.loads(RUTA_DECISION.read_text(encoding="utf-8"))

datos = load_data()
_, prueba = temporal_split(datos)


def tasa_base(frame, grupo):
    return 100.0 * float(frame.loc[frame.protected_group == grupo, "target"].mean())


tasa_prueba = {grupo: tasa_base(prueba, grupo) for grupo in ("G1", "G2")}
tasa_completo = {grupo: tasa_base(datos, grupo) for grupo in ("G1", "G2")}
celdas_insuficientes = inter[inter["soporte_insuficiente"].astype(str).str.lower().eq("true")]
insuficientes = [f"{etiqueta} (n={int(fila['count'])})" for etiqueta, fila in celdas_insuficientes.iterrows()]


def negritas(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def prosa(texto) -> str:
    return negritas(escape(str(texto)).replace("\n", "<br/>"))


def es(valor, decimales: int = 4) -> str:
    return f"{float(valor):.{decimales}f}".replace(".", ",")


def imagen_segura(ruta, ancho_cm, alto_cm):
    """Añade la imagen si existe; si no, una nota para que no se rompa la generación del PDF."""
    if Path(ruta).exists():
        return Image(str(ruta), width=ancho_cm * cm, height=alto_cm * cm)
    return Paragraph(f"[Figura no generada: {Path(ruta).name}. Se produce con scripts/make_figures.py]",
                      styles["Small"])


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12, spaceBefore=9, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13, fontSize=9.2))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.0, leading=10.2))
styles.add(ParagraphStyle(name="TablaCab", parent=styles["BodyText"], fontSize=7.4, leading=9.4,
                          textColor=colors.white))
styles.add(ParagraphStyle(name="TablaCelda", parent=styles["BodyText"], fontSize=7.2, leading=9.2))
styles.add(ParagraphStyle(name="TablaDato", parent=styles["BodyText"], fontSize=7.8, leading=10.0,
                          alignment=2))
styles.add(ParagraphStyle(name="TablaEtiqueta", parent=styles["BodyText"], fontSize=8.2, leading=10.2,
                          fontName="Helvetica-Bold"))


def celda(texto, estilo="TablaCelda"):
    return Paragraph(escape(str(texto)).replace("\n", "<br/>"), styles[estilo])


def cabecera(texto):
    return Paragraph(escape(str(texto)), styles["TablaCab"])


def tabla(filas, anchos, alineadas=(), fuente=7.2):
    tabla_ = Table(filas, colWidths=anchos, repeatRows=1)
    tabla_.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ] + [("ALIGN", c[0], c[1], c[2]) for c in alineadas]))
    return tabla_


story = []
story.append(Paragraph("Ejercicio 07 · Evaluación de impacto y auditoría de equidad", styles["Title2"]))
story.append(Paragraph(
    "INF-8239 Ciencia de Datos II (UASD) · Unidad 04 · Integración de LAB11 y LAB12", styles["Small"]))
story.append(Spacer(1, 5))

identificacion = [
        ["Estudiante", "Edwing Perez"],
        ["Profesor", "Edwin Ramón José Nolasco"],
        ["Repositorio", REPO_URL],
        ["Caso", "Riesgo territorial SINTÉTICO (640 registros) · no representa personas ni estadísticas reales de RD"],
        ["Decisión", "LIMITAR · piloto en modo REVIEW con revisión humana obligatoria y baseline sin modelo como camino operativo seguro"],
        ["Estado del pipeline", f"{despliegue['decision']['status']} · fallan {len(despliegue['decision']['failed'])} puertas (ver sección 4)"],
]
tabla_id = Table([[Paragraph(escape(filas[0]), styles["TablaEtiqueta"]), celda(filas[1])]
                  for filas in identificacion],
                 colWidths=[4.0 * cm, (ANCHO - 4.0) * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 8))

story.append(Paragraph("1. Finalidad, interesados y proporcionalidad", styles["H1s"]))
story.append(Paragraph(prosa(impacto["purpose"]) + "<br/><br/>"
                        + prosa(impacto["non_predictive_alternative"]) + "<br/><br/>"
                        + "<b>Prohibido:</b> " + prosa(impacto["out_of_scope_use"]), styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [[cabecera("Interesado"), cabecera("Beneficio"), cabecera("Daño posible"), cabecera("Poder"),
          cabecera("Participación")]]
for _, fila in stake.iterrows():
    filas.append([celda(fila["stakeholder"]), celda(fila["benefit"]), celda(fila["harm"]),
                  celda(fila["power"]), celda(fila["participation"])])
story.append(tabla(filas, [2.7 * cm, 4.5 * cm, 4.6 * cm, 1.5 * cm, 5.29 * cm]))
story.append(Spacer(1, 8))

story.append(Paragraph("2. Registro de riesgos y NIST AI RMF", styles["H1s"]))
story.append(Paragraph(
    "Nueve riesgos con control, responsable, evidencia y riesgo residual. La prioridad es "
    "probabilidad × impacto: ordena la atención, <b>no</b> convierte el daño humano en una verdad "
    "matemática. Marco: <b>NIST AI RMF 1.0</b> (DOI 10.6028/NIST.AI.100-1) — GOVERN (responsable y "
    "política), MAP (riesgos documentados), MEASURE (auditoría del LAB12) y MANAGE (condición de retiro y "
    "recurso de apelación).", styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [[cabecera("ID"), cabecera("Escenario"), cabecera("L"), cabecera("I"), cabecera("Prioridad"),
          cabecera("Control"), cabecera("Responsable"), cabecera("Residual")]]
for _, fila in riesgos.sort_values("priority", ascending=False).iterrows():
    filas.append([celda(fila["id"]), celda(fila["scenario"]), celda(fila["likelihood_1_4"]),
                  celda(fila["impact_1_4"]), celda(fila["priority"]), celda(fila["control"]),
                  celda(fila["owner"]), celda(fila["residual"])])
story.append(tabla(filas, [0.95 * cm, 4.7 * cm, 0.6 * cm, 0.6 * cm, 1.7 * cm, 3.9 * cm, 3.75 * cm,
                           2.39 * cm],
                   alineadas=[((2, 1), (4, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab11/riesgos_priorizados.png", 13.5, 6.9))
story.append(PageBreak())

story.append(Paragraph("3. Auditoría global, por grupo e interseccional", styles["H1s"]))
m = logistic["metrics"]
d = logistic["differences"]
filas = [[cabecera("Métrica"), cabecera("Global"), cabecera("G1 (n=101)"), cabecera("G2 (n=59)"),
          cabecera("Brecha")]]
for clave, etiqueta in [("accuracy", "Accuracy"), ("recall", "Recall (TPR)"), ("fpr", "FPR"),
                        ("selection_rate", "Tasa de selección"), ("precision", "Precisión")]:
    g1 = float(grupos_log.loc["G1", clave]) if clave in grupos_log.columns else float("nan")
    g2 = float(grupos_log.loc["G2", clave]) if clave in grupos_log.columns else float("nan")
    filas.append([celda(etiqueta), celda(f"{m[clave]:.4f}"), celda(f"{g1:.4f}"), celda(f"{g2:.4f}"),
                  celda(f"{d[clave]:.4f}")])
story.append(tabla(filas, [4.0 * cm, 3.4 * cm, 3.6 * cm, 3.6 * cm, 3.99 * cm],
                   alineadas=[((1, 1), (-1, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "La diferencia de recall entre grupos (0,1376) refleja en parte la distinta prevalencia del target, "
    "no una decisión discriminatoria demostrada: el atributo sensible no entra al modelo. Tasas base de "
    "positivos calculadas desde <font face='Courier'>data/territorial_risk_synthetic.csv</font> con el "
    "corte temporal del repo:", styles["Small"]))
story.append(Spacer(1, 2))
filas = [[cabecera("Grupo"), cabecera("Tasa base de positivos en la prueba"),
          cabecera("Tasa base de positivos en los datos completos")]]
for grupo in ("G1", "G2"):
    filas.append([celda(grupo), celda(f"{es(tasa_prueba[grupo], 1)} %"), celda(f"{es(tasa_completo[grupo], 1)} %")])
story.append(tabla(filas, [3.0 * cm, 7.8 * cm, 7.79 * cm],
                   alineadas=[((1, 1), (-1, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/tasas_base_positivos.png", 13.5, 7.0))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/metricas_por_grupo.png", 15.5, 5.7))
story.append(Spacer(1, 4))

story.append(PageBreak())
story.append(Paragraph("Celdas interseccionales (grupo | banda de edad, modelo logística). "
                        f"Soporte insuficiente en {len(insuficientes)} celdas: "
                        + ", ".join(insuficientes) + ".", styles["Small"]))
filas = [[cabecera("Celda"), cabecera("n"), cabecera("Recall"), cabecera("FPR"), cabecera("Soporte")]]
for etiqueta, fila in inter.iterrows():
    insuficiente = str(fila["soporte_insuficiente"]).strip().lower() == "true"
    filas.append([celda(etiqueta), celda(int(fila["count"])), celda(f"{fila['recall']:.4f}"),
                  celda(f"{fila['fpr']:.4f}"), celda("INSUFICIENTE" if insuficiente else "aceptable")])
story.append(tabla(filas, [4.6 * cm, 2.0 * cm, 3.6 * cm, 3.6 * cm, 4.79 * cm],
                   alineadas=[((1, 1), (3, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/recall_interseccional.png", 16.0, 8.0))
story.append(PageBreak())

story.append(Paragraph("4. Decisión y puertas de calidad", styles["H1s"]))
story.append(Paragraph(
    "<b>Decisión documentada: LIMITAR</b> — no hay despliegue autónomo; se autoriza un piloto en modo "
    "<b>REVIEW</b> con revisión humana obligatoria y el baseline sin modelo como camino operativo "
    "seguro.", styles["BodyJ"]))
story.append(Spacer(1, 2))
story.append(Paragraph(
    "<b>Estado del pipeline: REVIEW</b> — fallan tres puertas: <font face='Courier'>worst_group_recall"
    "</font> (" + es(despliegue["metrics"]["worst_group_recall"]) + " &lt; "
    + es(gates["min_worst_group_recall"], 2) + "), <font face='Courier'>recall_gap_pilot</font> ("
    + es(despliegue["gaps"]["recall_gap"]) + " &gt; " + es(gates["max_recall_gap_pilot"], 2)
    + ") e <font face='Courier'>intersectional_support</font> ("
    + str(despliegue["resources"]["min_intersectional_support"]) + " &lt; "
    + str(gates["min_intersectional_support"]) + ").", styles["BodyJ"]))
story.append(Spacer(1, 2))
story.append(Paragraph(
    "<b>Escalamiento a STOP</b>: si la brecha de recall supera " + es(gates["stop_recall_gap"], 2)
    + " o el recall del peor grupo baja de " + es(gates["stop_worst_group_recall"], 2)
    + ", el sistema se retira al baseline sin modelo.", styles["BodyJ"]))
story.append(Spacer(1, 4))

observado = {
    "recall": es(despliegue["metrics"]["recall"]),
    "recall_gap": es(despliegue["gaps"]["recall_gap"]),
    "fpr_gap": es(despliegue["gaps"]["fpr_gap"]),
    "latency": "verificado en la ejecución",
    "model_size": es(despliegue["resources"]["model_kb"], 2),
    "worst_group_recall": es(despliegue["metrics"]["worst_group_recall"])
    + " (" + str(despliegue["metrics"]["worst_group"]) + ")",
    "recall_gap_pilot": es(despliegue["gaps"]["recall_gap"]),
    "intersectional_support": str(despliegue["resources"]["min_intersectional_support"]),
}
umbrales = {
    "recall": "&ge; " + es(gates["min_recall"], 2),
    "recall_gap": "&le; " + es(gates["max_recall_gap"], 2),
    "fpr_gap": "&le; " + es(gates["max_fpr_gap"], 2),
    "latency": "&le; " + str(gates["max_latency_ms"]) + " ms",
    "model_size": "&le; " + str(gates["max_model_kb"]) + " KB",
    "worst_group_recall": "&ge; " + es(gates["min_worst_group_recall"], 2),
    "recall_gap_pilot": "&le; " + es(gates["max_recall_gap_pilot"], 2),
    "intersectional_support": "&ge; " + str(gates["min_intersectional_support"]),
}
filas = [[cabecera("Puerta"), cabecera("Umbral"), cabecera("Observado"), cabecera("Resultado")]]
for nombre, cumple in despliegue["decision"]["checks"].items():
    filas.append([celda(nombre), celda(umbrales[nombre]), celda(observado[nombre]),
                  celda("cumple" if cumple else "FALLA")])
story.append(tabla(filas, [5.4 * cm, 4.2 * cm, 4.4 * cm, 4.59 * cm],
                   alineadas=[((1, 1), (-1, -1), "CENTER")]))
story.append(Spacer(1, 4))
filas = [[cabecera("Condición de escalamiento"), cabecera("Umbral"), cabecera("Observado"),
          cabecera("Estado")]]
filas.append([celda("stop_recall_gap (brecha de recall)"), celda("> " + es(gates["stop_recall_gap"], 2)),
              celda(es(despliegue["gaps"]["recall_gap"])),
              celda("no escala" if not despliegue["decision"]["escalations"]["stop_recall_gap"] else "ESCALA")])
filas.append([celda("stop_worst_group_recall (peor grupo)"),
              celda("< " + es(gates["stop_worst_group_recall"], 2)),
              celda(es(despliegue["metrics"]["worst_group_recall"])),
              celda("no escala" if not despliegue["decision"]["escalations"]["stop_worst_group_recall"] else "ESCALA")])
story.append(tabla(filas, [5.4 * cm, 4.2 * cm, 4.4 * cm, 4.59 * cm],
                   alineadas=[((1, 1), (-1, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab13/puertas_calidad.png", 13.5, 6.6))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "La evidencia de esta sección es <font face='Courier'>reports/lab13/deployment_decision.json</font>, "
    "generada por <font face='Courier'>scripts/lab13_governance.py</font> a partir de "
    "<font face='Courier'>configs/governance.yml</font>.", styles["Small"]))
story.append(PageBreak())

story.append(Paragraph("5. Mitigación, trade-offs y decisión", styles["H1s"]))
filas = [[cabecera("Alternativa"), cabecera("Accuracy"), cabecera("Recall"), cabecera("FPR"),
          cabecera("Brecha recall"), cabecera("Brecha FPR"), cabecera("Entreno (s, cota)"), cabecera("Modelo (KB)")]]
for nombre, datos_, grupos in [("Logística", logistic, grupos_log), ("Árbol", tree, grupos_tree)]:
    filas.append([celda(nombre), celda(f"{datos_['metrics']['accuracy']:.4f}"),
                  celda(f"{datos_['metrics']['recall']:.4f}"), celda(f"{datos_['metrics']['fpr']:.4f}"),
                  celda(f"{datos_['differences']['recall']:.4f}"),
                  celda(f"{datos_['differences']['fpr']:.4f}"),
                  celda(f"\u2264 {es(datos_['resources']['training_seconds_cota'], 2)}"),
                  celda(f"{datos_['resources']['model_kb']:.2f}")])
story.append(tabla(filas, [2.4 * cm, 2.1 * cm, 2.1 * cm, 2.0 * cm, 2.6 * cm, 2.4 * cm, 2.4 * cm,
                            2.59 * cm],
                   alineadas=[((1, 1), (-1, -1), "CENTER")]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/utilidad_vs_brecha.png", 13.5, 7.3))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "El árbol alcanza la <b>misma utilidad global</b> (recall 0,7174) con <b>brechas mayores</b> "
    "(recall 0,1813 frente a 0,1376; FPR 0,1683 frente a 0,1250) y el <b>doble de tamaño</b> "
    "(7,90 KB frente a 3,56 KB): el costo adicional no se justifica.", styles["Small"]))
story.append(Spacer(1, 4))

for clave, titulo in [("priority_harm", "Daño priorizado"), ("primary_metric", "Métrica principal"),
                      ("tolerance", "Tolerancia y puerta"), ("limitation", "Limitaciones"),
                      ("recommendation", "Recomendación")]:
    story.append(Paragraph(titulo, styles["H1s"]))
    story.append(Paragraph(prosa(decision[clave]), styles["BodyJ"]))
    story.append(Spacer(1, 2))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Obligación legal, marco voluntario y recomendación ética.</b> En este caso sintético no hay "
    "una obligación legal específica que se pueda verificar (no hay datos personales ni decisiones "
    "reales), y esa ausencia se documenta en lugar de suplirse con el marco técnico: el <b>NIST AI "
    "RMF 1.0</b> (marco voluntario) organiza el control —GOVERN, MAP, MEASURE, MANAGE— y la "
    "<b>recomendación ética</b> (alternativa no predictiva, recurso de apelación, condición de retiro) "
    "sostiene la decisión. Ninguna de las dos sustituye a la revisión jurídica que cualquier uso con "
    "datos reales exigiría.", styles["BodyJ"]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Uso responsable de IA.</b> El asistente de IA (Kilo, modelo MiniMax-M3) apoyó la estructura de "
    "los artefactos, la redacción de las tarjetas y la corrección de dos scripts del proyecto base que "
    "no compilaban (<font face='Courier'>lab11_impact.py</font> y "
    "<font face='Courier'>simulate_incident.py</font>, por saltos de línea reales dentro de literales), "
    "y después una revisión de coherencia de la entrega: unificar la decisión (LIMITAR) con el estado "
    "real del pipeline (REVIEW), derivar las tasas base de positivos de los datos, marcar las celdas "
    "con soporte insuficiente y reconstruir las tablas ilegibles de la página 1. Los <b>valores del "
    "análisis</b> —finalidad, interesados, probabilidad e impacto de cada riesgo, tolerancia, métrica "
    "principal y recomendación— los decidió el estudiante con la evidencia del manual y de las "
    "ejecuciones; el asistente no inventó ninguna cifra ni referencia. Detalle en "
    "<font face='Courier'>docs/AI_USE_DECLARATION.md</font>.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Referencias.</b> NIST, <i>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</i>, "
    "DOI 10.6028/NIST.AI.100-1 · OECD, <i>Recommendation of the Council on Artificial "
    "Intelligence</i>, DOI 10.1787/cc2e1d3e-en · Fairlearn Contributors, <i>Performing a Fairness "
    "Assessment</i> (documentación oficial).", styles["Small"]))

target = ROOT / "docs/EJERCICIO_07_PDF_SINTESIS.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 07 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm,
                              invariant=1)
document.build(story)
print("PDF generado:", target)
