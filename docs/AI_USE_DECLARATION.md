# Declaración de uso de IA · Unidad 04 (LAB11–LAB12 · Ejercicio 07)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02 · Revisión de coherencia: 2026-11-05

## Herramienta

Asistente de IA en modo CLI (Kilo, modelo MiniMax-M3) con acceso a esta máquina. Se usaron además
Python 3.12 con `uv`, Fairlearn 0.12, scikit-learn 1.9 y las librerías del proyecto base del
profesor. **No** se usaron servicios en la nube, APIs externas ni datos generados por IA: el corpus
es el caso sintético que acompaña al proyecto base.

## Finalidad y alcance

| Uso | Detalle |
|---|---|
| Estructura | Traducir la rúbrica del Ejercicio 07 en artefactos editables: ficha de impacto, registro de riesgos, tabla de interesados, decisión de equidad y expediente |
| Código | Corrección de dos scripts del proyecto base que **no compilaban** (ver «Correcciones»), una modificación menor para no sobrescribir el registro de decisión del estudiante y, en la revisión de 2026-11-05, la extensión aditiva de las puertas de gobernanza (`governance.py`, `pipeline.py`, `fairness.py`) y de los scripts que generan la evidencia |
| Redacción | Estructura de los documentos (Dataset Card, registro de decisión, esta declaración) y unificación del lenguaje de la decisión entre README, registro de decisión, YAML y PDF |
| Verificación | Comprobación de que las cifras de los informes coinciden con los CSV/JSON generados por los scripts del profesor (contraste ejecutado; ver «Verificaciones ejecutadas») |

**Lo que la IA no hizo (y no puede hacer por mandato):** los **valores del análisis** —finalidad,
interesados, probabilidad e impacto de cada riesgo, tolerancia de brecha, métrica principal y
recomendación— los decidió el estudiante con la evidencia del manual y de las ejecuciones; y ninguna
referencia, cifra o evidencia fue inventada: todas provienen de `reports/lab11/`, `reports/lab12/` y
`reports/lab13/`.

## Prompts relevantes

1. «Del propósito a un registro de decisión verificable: distingue finalidad, usuario, persona
   afectada y propietario; evalúa necesidad, proporcionalidad y alternativa no predictiva; prioriza
   riesgos con control, responsable y evidencia; y escribe la decisión con su incertidumbre, su
   responsable y su condición de retiro.»
2. «Audita el clasificador por grupos sin convertir una métrica de equidad en una declaración
   automática de justicia: separa desempeño global, por grupo e interseccional, declara el soporte
   mínimo y no interpretes las celdas con pocas observaciones.»
3. «Compara las dos alternativas con utilidad, brechas, tiempo de entrenamiento y tamaño serializado,
   y justifica la recomendación en términos del daño priorizado, no de la métrica más vistosa.»
4. «Distingue obligación legal, marco voluntario y recomendación ética; una puntuación no sustituye el
   juicio profesional.»
5. «No inventes evidencia: toda cifra debe salir de un archivo de `reports/` y toda referencia debe
   poder verificarse.»
6. «La decisión es incoherente en cuatro artefactos: unifica el lenguaje de la decisión, del estado del
   pipeline y del escalamiento, con la misma redacción en todos ellos.»
7. «Las cifras del PDF y del informe están desfasadas respecto de los datos: calcúlalas desde el
   dataset en lugar de mantener literales, y marca las celdas con soporte insuficiente por código.»

## Verificaciones ejecutadas (2026-11-05, con el resultado real)

- [x] `uv sync --frozen` → `Checked 54 packages` (entorno reproducible con el lock del base).
- [x] `uv run pytest -q` → **20 passed**.
- [x] `uv run ruff check .` → **All checks passed!**
- [x] `uv run python scripts/check_environment.py` → `{'python_project': 'ok', 'dataset_status': 'valid', 'rows': 640, 'columns': 9}`.
- [x] `uv run python scripts/lab11_impact.py` → `reports/lab11/risk_register_scored.csv` con 9 riesgos
      (prioridades 9, 8, 8, 8, 6, 6, 6, 4, 4) y `rmf_summary.json`.
- [x] `uv run python scripts/lab12_audit.py --model logistic` y `--model tree` → métricas globales,
      por grupo e interseccionales; `fairness_intersectional.csv` con la columna `soporte_insuficiente`
      calculada por el propio script (umbral 15: 3 celdas marcadas, n=8, n=11 y n=14).
- [x] `uv run python scripts/validate_lab12_decision.py` → `decision_status: documented`.
- [x] `uv run python scripts/lab13_governance.py` → `{'status': 'REVIEW', …, 'failed':
      ['worst_group_recall', 'recall_gap_pilot', 'intersectional_support'], 'escalation_triggered': []}`
      y `reports/lab13/deployment_decision.json` versionado.
- [x] `uv run python scripts/dataset_stats.py` → `reports/dataset_stats.json` y los bloques
      calculados de `docs/DATASET_CARD.md` y `README.md` (tasas base de positivos de los datos
      completos y de la prueba temporal).
- [x] `uv run python scripts/make_figures.py` → 7 figuras `OK` (incluye
      `reports/lab13/puertas_calidad.png`).
- [x] `uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py`
      → **7 passed**.
- [x] `bash scripts/run_all.sh` → flujo completo sin errores (entorno → pruebas → LAB11 → LAB12 →
      LAB13 → incidente → cifras del dataset → notebook → figuras → PDF).
- [x] Contraste de cifras entre el informe y los CSV/JSON: recall 0,7174, brecha de recall 0,1376,
      FPR 0,1250, recall del peor grupo 0,6531 (G1), soporte interseccional mínimo 8 y tasas base de
      positivos 48,5 % / 72,9 % (prueba) y 49,7 % / 63,9 % (datos completos) coinciden con
      `reports/lab12/*` y `reports/lab13/deployment_decision.json`.
- [x] `pdftotext -layout docs/EJERCICIO_07_PDF_SINTESIS.pdf -` → contiene «Edwing Perez», la URL del
      repositorio, «LIMITAR», «REVIEW», «STOP» y las tasas 48,5 % / 72,9 % / 49,7 % / 63,9 %; no
      contiene «23,9 %» ni «49,6 %».

## Correcciones realizadas

| Corrección | Causa | Verificación |
|---|---|---|
| `scripts/lab11_impact.py` no compilaba (`SyntaxError: unterminated string literal`) | El ZIP del profesor trae saltos de línea reales dentro de literales de cadena | El script se ejecuta y genera `reports/lab11/` |
| `scripts/simulate_incident.py` no compilaba (`SyntaxError: unterminated f-string literal`) | Misma causa en el archivo de texto del simulacro | Se reescribió la construcción del texto con `\n` escapados |
| El script de LAB11 ya no sobrescribe `DECISION_RECORD.md` si el estudiante ya lo redactó | El base lo regeneraba con la plantilla de marcadores sin resolver en cada ejecución y borraba el trabajo del estudiante | Al reejecutar el script, el registro se conserva |
| La decisión decía cuatro cosas distintas (LIMITAR, REVIEW, STOP y GO) | Las puertas del LAB12 no existían en `configs/governance.yml`, así que el evaluador devolvía GO mientras la documentación afirmaba lo contrario | `configs/governance.yml` declara las tres puertas y los dos umbrales de escalamiento; `deployment_decision` los evalúa y devuelve REVIEW con las tres puertas fallidas |
| `reports/lab13/deployment_decision.json` no existía aunque el riesgo R07 lo cita como evidencia | El flujo no ejecutaba `scripts/lab13_governance.py` | `scripts/run_all.sh` lo ejecuta y el JSON queda versionado |
| El PDF afirmaba «G1 23,9 %» y «datos completos: 49,6 %», y la Dataset Card arrastraba las mismas dos cifras | Literales escritos a mano, desfasados respecto de los datos | Las tasas se calculan desde `data/territorial_risk_synthetic.csv` con el corte temporal del repo: 48,5 % / 72,9 % en la prueba y 49,7 % / 63,9 % en los datos completos; en la Dataset Card y en el README las cifras van en bloques generados por `scripts/dataset_stats.py` y `tests/test_dataset_stats.py` falla si se desincronizan |
| Las celdas con soporte insuficiente se contaban de dos formas (2 frente a 3) | El soporte se marcaba a mano en el PDF y sin marca en los CSV | `fairness_intersectional.csv` lleva la columna `soporte_insuficiente` calculada por código (umbral 15) y todos los artefactos cuentan 3 celdas (n=8, n=11 y n=14) |
| Dos tablas del PDF (interesados y riesgos) se solapaban | Celdas de texto plano sin ajuste de línea en columnas estrechas | Las tablas se reconstruyen con párrafos con `wordWrap` y anchos de columna; la página 1 renderizada a PNG no muestra solapamiento |
| `docs/MODEL_CARD.md` y `docs/RUNBOOK.md` con marcadores sin resolver | Son las plantillas del LAB13 (Ejercicio 08) que trae el base y no aplican aquí | **Se eliminan del repositorio**: no son parte de la entrega del Ejercicio 07 y su contenido no se inventa. La documentación de entrega es `docs/DATASET_CARD.md`, `docs/AI_USE_DECLARATION.md` y `docs/EJERCICIO_07_PDF_SINTESIS.pdf` |
| `uv run ruff check .` señalaba 29 hallazgos heredados | El base no fijó `[tool.ruff]` en `pyproject.toml` (que no se toca) | Hallazgos corregidos en el código (orden de imports, imports sin uso, expresión inútil del notebook, `except` ciego) |

No se modificaron `pyproject.toml` ni `uv.lock` del proyecto base. Se modificaron
`src/inf8239_u04/governance.py` (puertas del LAB12 y estado STOP, de forma aditiva: con los umbrales
base el resultado no cambia), `src/inf8239_u04/pipeline.py` (recall del peor grupo, peor grupo y
soporte interseccional mínimo) y `src/inf8239_u04/fairness.py` (marca de soporte insuficiente); en
`src/inf8239_u04/impact.py` solo se eliminó un `import pandas` sin uso. La lógica de `data.py` y
`model.py` no se tocó.

## Referencias utilizadas (verificables)

- NIST. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. DOI: 10.6028/NIST.AI.100-1
  (funciones GOVERN, MAP, MEASURE y MANAGE).
- OECD. *Recommendation of the Council on Artificial Intelligence*. DOI: 10.1787/cc2e1d3e-en
  (principios de proporcionalidad y responsabilidad).
- Fairlearn Contributors. *Performing a Fairness Assessment*, documentación oficial
  (`MetricFrame`, `count`, `selection_rate`, `true_positive_rate`, `false_positive_rate`).

## Límites

- Las cifras provienen de ejecuciones en esta máquina y deben reejecutarse en el entorno de entrega.
- La auditoría usa **una sola partición temporal y una sola semilla**, sin intervalos de confianza: las
  brechas son estimaciones puntuales y deben leerse con esa incertidumbre.
- El caso es sintético: ninguna conclusión describe poblaciones, zonas o personas reales.
- La interpretación normativa (qué obligaciones aplican y quién responde) es del estudiante y debe
  poder defendirse sin el apoyo de esta herramienta.
- Los tiempos de ejecución (entrenamiento y latencia) no se versionan como valores crudos:
  dependen de la máquina. Los artefactos guardan una cota superior del tiempo de ajuste
  (`training_seconds_cota`: ≤ 0,02 s para ambos modelos) y la puerta de latencia se verifica en
  cada ejecución, con su resultado en `decision.checks.latency`.
