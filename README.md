# INF-8239 · Ejercicio 07 · Evaluación de impacto y auditoría de equidad

Autor académico: Edwin Ramón José Nolasco · Repositorio: https://github.com/edvvdev/unidad04-07

Expediente reproducible que integra **LAB11** (evaluación de impacto ético) y **LAB12** (auditoría de
equidad con Fairlearn) sobre el caso territorial **sintético** del proyecto base del profesor. El
dataset no representa personas, zonas ni estadísticas reales de República Dominicana.

## Inicio

```bash
uv python install 3.12
uv sync --frozen
uv run pytest -q                                  # 20 passed
uv run python scripts/check_environment.py        # dataset_status: valid · 640 filas
```

## Ejecución completa (un solo comando)

```bash
./scripts/run_all.sh          # macOS / Linux
```
```powershell
.\scripts\run_all.ps1        # Windows
```

El script hace: entorno → pruebas → LAB11 → LAB12 (logística y árbol) → **LAB13 (puertas de
gobernanza y decisión de despliegue)** → **simulacro de incidente** → **cifras del dataset** →
notebook ejecutado → figuras → PDF de síntesis. Instala además Jupyter, `reportlab` y `matplotlib`, que **no** vienen en el grupo
de desarrollo del proyecto base (`uv sync` solo instala pytest, pytest-cov y ruff).

## Entrega del Ejercicio 07

| Elemento | Dónde está |
|---|---|
| Notebook ejecutado | `notebooks/01_ejercicio07_impacto_equidad.ipynb` (16 celdas, con salidas, 0 errores) |
| Artefactos editables | `student_inputs/lab11_impact.yml`, `stakeholders.csv`, `risk_register.csv`, `lab12_decision.yml` |
| Evidencia generada | `reports/lab11/` (riesgos priorizados, RMF, registro de decisión), `reports/lab12/` (métricas por grupo, interseccionales, figuras) y `reports/lab13/` (decisión de despliegue, puertas de calidad) |
| Decisión de despliegue | `reports/lab13/deployment_decision.json` (generada por `scripts/lab13_governance.py`) |
| Cifras del dataset | `reports/dataset_stats.json` (generada por `scripts/dataset_stats.py`): las tasas y los recuentos de la Dataset Card y del README **se calculan**, no están escritos a mano |
| Pruebas | `tests/` (`uv run pytest -q` → 20 passed) |
| Requisitos | `requirements.txt` y `requirements-dev.txt` (exportados con `uv export`) |
| PDF de síntesis | `docs/EJERCICIO_07_PDF_SINTESIS.pdf` (7 páginas) |
| Declaración de IA | `docs/AI_USE_DECLARATION.md` |
| Correcciones al base | `CAMBIOS_AL_BASE.md` |

## Resultados de referencia (2026-11-02, corte temporal 2026-09-24/25, semilla 42)

**LAB11 · registro de riesgos** (9 riesgos, prioridad = probabilidad × impacto):

| ID | Riesgo | Prioridad | Riesgo residual |
|---|---|---|---|
| R03 | Brecha de recall entre grupos | 9 | medium |
| R01 | Falso positivo que desplaza verificación | 8 | medium |
| R02 | Falso negativo (daño priorizado) | 8 | medium |
| R07 | Presión para decidir sin revisión humana | 8 | **high** |

**LAB12 · auditoría de equidad (modelo logística)**:

| Métrica | Global | G1 (n=101) | G2 (n=59) | Brecha |
|---|---|---|---|---|
| Accuracy | 0,7188 | 0,703 | 0,746 | 0,0428 |
| Recall (TPR) | 0,7174 | 0,653 | 0,791 | **0,1376** |
| FPR | 0,2794 | 0,250 | 0,375 | 0,1250 |
| Tasa de selección | 0,5313 | 0,446 | 0,678 | 0,2324 |

Soporte interseccional: ocho celdas con n entre 8 y 35; **soporte insuficiente en 3 celdas** —
`G2 | 45-59` (n=8), `G2 | 18-29` (n=11) y `G2 | 30-44` (n=14)—, cuyas cifras no se interpretan como
evidencia de brecha. La marca viaja calculada por código en la columna `soporte_insuficiente` de
`reports/lab12/*/fairness_intersectional.csv` (umbral 15, el mismo de la puerta de despliegue).

<!-- stats:inicio rates -->
Tasa base de positivos (calculada desde `data/territorial_risk_synthetic.csv` con el corte temporal
del repo): G1 **49,7 %** frente a G2 **63,9 %** en los datos completos, y G1 **48,5 %** frente a G2
**72,9 %** en la prueba de 160 registros.

<!-- stats:fin rates -->

**Comparación de alternativas**: la logística y el árbol obtienen la **misma utilidad global**
(recall 0,7174), pero la logística tiene **brechas menores** (recall 0,1376 frente a 0,1813; FPR
0,1250 frente a 0,1683) y ocupa **menos de la mitad** (3,56 KB frente a 7,90 KB).

## Decisión documentada: LIMITAR

No hay despliegue autónomo; se autoriza un piloto en modo **REVIEW** con revisión humana obligatoria
y el baseline sin modelo como camino operativo seguro.

## Estado del pipeline: REVIEW

Fallan tres puertas: `worst_group_recall` (0,6531 < 0,70), `recall_gap_pilot` (0,1376 > 0,10) e
`intersectional_support` (8 < 15). Las ocho puertas evaluadas y su resultado están en
`reports/lab13/deployment_decision.json` y en la figura `reports/lab13/puertas_calidad.png`.

## Escalamiento a STOP

Si la brecha de recall supera 0,15 o el recall del peor grupo baja de 0,60, el sistema se retira al
baseline sin modelo. Los dos umbrales están declarados en `configs/governance.yml`
(`stop_recall_gap`, `stop_worst_group_recall`) y los evalúa `deployment_decision`; con la evidencia
actual no se dispara ninguno, porque el estado es REVIEW, no STOP.

La brecha observada **no prueba discriminación causal** (el atributo sensible no entra al modelo y
parte de la diferencia es la tasa base de positivos: <!-- stats:inicio rates_decision -->G2 63,9 % frente a G1 49,7 %<!-- stats:fin rates_decision -->), pero tampoco puede
descartarse: zona y banda de edad pueden portar el mismo sesgo de forma indirecta.

## Capas que no se confunden

| Capa | En este caso |
|---|---|
| Obligación legal | Ninguna verificable sobre un caso sintético; se documenta la ausencia y se prohíbe el uso con datos reales sin revisión jurídica |
| Marco voluntario | NIST AI RMF 1.0 (GOVERN, MAP, MEASURE, MANAGE) |
| Recomendación ética | Alternativa no predictiva, recurso de apelación y condición de retiro |

## Interpretación

La auditoría no convierte una métrica en una declaración de justicia: la evidencia es de un caso
sintético, con una sola partición temporal y una sola semilla, sin intervalos de confianza, y con
soporte insuficiente en tres celdas interseccionales. La decisión se apoya en el daño priorizado
(falso negativo) y en la evidencia de costo, no en la métrica más vistosa.
