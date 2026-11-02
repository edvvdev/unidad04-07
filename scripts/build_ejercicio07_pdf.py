"""Genera el PDF de síntesis del Ejercicio 07 (impacto y equidad)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd
import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-07")

logistic = json.loads((REPORTS / "lab12/logistic/global_metrics.json").read_text(encoding="utf-8"))
tree = json.loads((REPORTS / "lab12/tree/global_metrics.json").read_text(encoding="utf-8"))
grupos_log = pd.read_csv(REPORTS / "lab12/logistic/fairness_by_group.csv", index_col=0)
grupos_tree = pd.read_csv(REPORTS / "lab12/tree/fairness_by_group.csv", index_col=0)
inter = pd.read_csv(REPORTS / "lab12/logistic/fairness_intersectional.csv", index_col=0)
riesgos = pd.read_csv(REPORTS / "lab11/risk_register_scored.csv")
stake = pd.read_csv(REPORTS / "lab11/stakeholders.csv")
decision = yaml.safe_load((ROOT / "student_inputs/lab12_decision.yml").read_text(encoding="utf-8"))
impacto = yaml.safe_load((ROOT / "student_inputs/lab11_impact.yml").read_text(encoding="utf-8"))


def negritas(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)



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
    ["Decisión", "LIMITAR · piloto en modo REVIEW con puerta de equidad trimestral y condiciones de retiro"],
]
tabla_id = Table(identificacion, colWidths=[4.2 * cm, 11.6 * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.2),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 8))

story.append(Paragraph("1. Finalidad, interesados y proporcionalidad", styles["H1s"]))
story.append(Paragraph(negritas(impacto["purpose"]) + "<br/><br/>"
                        + negritas(impacto["non_predictive_alternative"]) + "<br/><br/>"
                        + "<b>Prohibido:</b> " + negritas(impacto["out_of_scope_use"]), styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [["Interesado", "Beneficio", "Daño posible", "Poder", "Participación"]]
for _, fila in stake.iterrows():
    filas.append([fila["stakeholder"], str(fila["benefit"])[:70] + "…",
                  str(fila["harm"])[:70] + "…", fila["power"], str(fila["participation"])[:48] + "…"])
tabla_stake = Table(filas, colWidths=[2.6 * cm, 4.2 * cm, 4.2 * cm, 1.4 * cm, 3.4 * cm], repeatRows=1)
tabla_stake.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 6.8),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_stake)
story.append(Spacer(1, 8))

story.append(Paragraph("2. Registro de riesgos y NIST AI RMF", styles["H1s"]))
story.append(Paragraph(
    "Nueve riesgos con control, responsable, evidencia y riesgo residual. La prioridad es "
    "probabilidad × impacto: ordena la atención, <b>no</b> convierte el daño humano en una verdad "
    "matemática. Marco: <b>NIST AI RMF 1.0</b> (DOI 10.6028/NIST.AI.100-1) — GOVERN (responsable y "
    "política), MAP (riesgos documentados), MEASURE (auditoría del LAB12) y MANAGE (condición de retiro y "
    "recurso de apelación).", styles["BodyJ"]))
story.append(Spacer(1, 4))
filas = [["ID", "Escenario (resumen)", "L", "I", "Prioridad", "Control (resumen)", "Responsable", "Residual"]]
for _, fila in riesgos.sort_values("priority", ascending=False).iterrows():
    filas.append([fila["id"], str(fila["scenario"])[:58] + "…", str(fila["likelihood_1_4"]),
                  str(fila["impact_1_4"]), str(fila["priority"]), str(fila["control"])[:42] + "…",
                  str(fila["owner"])[:34] + "…", fila["residual"]])
tabla_riesgos = Table(filas, colWidths=[1.0 * cm, 4.6 * cm, 0.8 * cm, 0.8 * cm, 1.5 * cm, 3.2 * cm, 3.1 * cm, 1.5 * cm],
                      repeatRows=1)
tabla_riesgos.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 6.8),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ALIGN", (2, 1), (4, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_riesgos)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab11/riesgos_priorizados.png", 13.5, 6.9))
story.append(PageBreak())

story.append(Paragraph("3. Auditoría global, por grupo e interseccional", styles["H1s"]))
m = logistic["metrics"]
d = logistic["differences"]
filas = [["Métrica", "Global", "G1 (n=101)", "G2 (n=59)", "Brecha"]]
for clave, etiqueta in [("accuracy", "Accuracy"), ("recall", "Recall (TPR)"), ("fpr", "FPR"),
                        ("selection_rate", "Tasa de selección"), ("precision", "Precisión")]:
    g1 = float(grupos_log.loc["G1", clave]) if clave in grupos_log.columns else float("nan")
    g2 = float(grupos_log.loc["G2", clave]) if clave in grupos_log.columns else float("nan")
    filas.append([etiqueta, f"{m[clave]:.4f}", f"{g1:.4f}", f"{g2:.4f}", f"{d[clave]:.4f}"])
tabla_metricas = Table(filas, colWidths=[3.4 * cm, 2.6 * cm, 2.8 * cm, 2.8 * cm, 2.6 * cm], repeatRows=1)
tabla_metricas.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.0),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_metricas)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Tasa base de positivos en la prueba: G1 23,9 % frente a G2 72,9 % (datos completos: 49,6 % y "
    "63,9 %). La diferencia de recall refleja en parte esa prevalencia distinta, no una decisión "
    "discriminatoria demostrada: el atributo sensible no entra al modelo.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/metricas_por_grupo.png", 15.5, 5.7))
story.append(Spacer(1, 4))

story.append(Paragraph("Celdas interseccionales (grupo | banda de edad, modelo logística)", styles["Small"]))
filas = [["Celda", "n", "Recall", "FPR", "Soporte"]]
for etiqueta, fila in inter.iterrows():
    n = int(fila["count"])
    filas.append([etiqueta, str(n), f"{fila['recall']:.4f}", f"{fila['fpr']:.4f}",
                  "INSUFICIENTE" if n < 15 else "aceptable"])
tabla_inter = Table(filas, colWidths=[3.4 * cm, 1.6 * cm, 2.4 * cm, 2.4 * cm, 3.0 * cm], repeatRows=1)
tabla_inter.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.6),
    ("ALIGN", (1, 1), (3, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(tabla_inter)
story.append(Spacer(1, 4))
story.append(imagen_segura(REPORTS / "lab12/recall_interseccional.png", 15.5, 7.75))
story.append(PageBreak())

story.append(Paragraph("4. Mitigación, trade-offs y decisión", styles["H1s"]))
filas = [["Alternativa", "Accuracy", "Recall", "FPR", "Brecha recall", "Brecha FPR", "Entreno (s)", "Modelo (KB)"]]
for nombre, datos, grupos in [("Logística", logistic, grupos_log), ("Árbol", tree, grupos_tree)]:
    filas.append([nombre, f"{datos['metrics']['accuracy']:.4f}", f"{datos['metrics']['recall']:.4f}",
                  f"{datos['metrics']['fpr']:.4f}", f"{datos['differences']['recall']:.4f}",
                  f"{datos['differences']['fpr']:.4f}",
                  f"{datos['resources']['training_seconds']:.4f}",
                  f"{datos['resources']['model_kb']:.2f}"])
tabla_alt = Table(filas, colWidths=[2.6 * cm, 2.0 * cm, 1.9 * cm, 1.8 * cm, 2.2 * cm, 2.1 * cm, 2.1 * cm, 2.3 * cm],
                   repeatRows=1)
tabla_alt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.8),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_alt)
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
    story.append(Paragraph(negritas(str(decision[clave])), styles["BodyJ"]))
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
    "<font face='Courier'>simulate_incident.py</font>, por saltos de línea reales dentro de literales). "
    "Los <b>valores del análisis</b> —finalidad, interesados, probabilidad e impacto de cada riesgo, "
    "tolerancia, métrica principal y recomendación— los decidió el estudiante con la evidencia del "
    "manual y de las ejecuciones; el asistente no inventó ninguna cifra ni referencia. Detalle en "
    "<font face='Courier'>docs/AI_USE_DECLARATION.md</font>.", styles["Small"]))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Referencias.</b> NIST, <i>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</i>, "
    "DOI 10.6028/NIST.AI.100-1 · OECD, <i>Recommendation of the Council on Artificial "
    "Intelligence</i>, DOI 10.1787/cc2e1d3e-en · Fairlearn Contributors, <i>Performing a Fairness "
    "Assessment</i> (documentación oficial).", styles["Small"]))

target = ROOT / "docs/EJERCICIO_07_PDF_SINTESIS.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 07 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm)
document.build(story)
print("PDF generado:", target)
