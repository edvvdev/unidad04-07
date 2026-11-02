# Declaración de uso de IA · Unidad 04 (LAB11–LAB12 · Ejercicio 07)

Proyecto: `INF8239_U04_Gobernanza_DSS` · Fecha: 2026-11-02

## Herramienta

Asistente de IA en modo CLI (Kilo, modelo MiniMax-M3) con acceso a esta máquina. Se usaron además
Python 3.12 con `uv`, Fairlearn 0.12, scikit-learn 1.9 y las librerías del proyecto base del
profesor. **No** se usaron servicios en la nube, APIs externas ni datos generados por IA: el corpus
es el caso sintético que acompaña al proyecto base.

## Finalidad y alcance

| Uso | Detalle |
|---|---|
| Estructura | Traducir la rúbrica del Ejercicio 07 en artefactos editables: ficha de impacto, registro de riesgos, tabla de interesados, decisión de equidad y expediente |
| Código | Corrección de dos scripts del proyecto base que **no compilaban** (ver «Correcciones») y una modificación menor para no sobrescribir el registro de decisión del estudiante |
| Redacción | Estructura de los documentos (Dataset Card, registro de decisión, esta declaración) |
| Verificación | Comprobación de que las cifras de los informes coinciden con los CSV/JSON generados por los scripts del profesor |

**Lo que la IA no hizo (y no puede hacer por mandato):** los **valores del análisis** —finalidad,
interesados, probabilidad e impacto de cada riesgo, tolerancia de brecha, métrica principal y
recomendación— los decidió el estudiante con la evidencia del manual y de las ejecuciones; y ninguna
referencia, cifra o evidencia fue inventada: todas provienen de `reports/lab11/` y `reports/lab12/`.

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

## Verificaciones que el estudiante debe repetir

- [ ] `uv sync --frozen` y `uv run pytest -q` → 10 passed.
- [ ] `uv run python scripts/check_environment.py` → `dataset_status: valid`, 640 filas.
- [ ] `uv run python scripts/lab11_impact.py` → `reports/lab11/risk_register_scored.csv` con 9 riesgos
      y `rmf_summary.json`.
- [ ] `uv run python scripts/lab12_audit.py --model logistic` y `--model tree` → métricas globales,
      por grupo e interseccionales.
- [ ] `uv run python scripts/validate_lab12_decision.py` → `decision_status: documented`.
- [ ] `uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py`.
- [ ] Revisar que las cifras del registro de decisión coinciden con los CSV y JSON.

## Correcciones realizadas

| Corrección | Causa | Verificación |
|---|---|---|
| `scripts/lab11_impact.py` no compilaba (`SyntaxError: unterminated string literal`) | El ZIP del profesor trae saltos de línea reales dentro de literales de cadena | El script se ejecuta y genera `reports/lab11/` |
| `scripts/simulate_incident.py` no compilaba (`SyntaxError: unterminated f-string literal`) | Misma causa en el archivo de texto del simulacro | Se reescribió la construcción del texto con `\n` escapados |
| El script de LAB11 ya no sobrescribe `DECISION_RECORD.md` si el estudiante ya lo redactó | El base lo regeneraba con el texto `REPLACE` en cada ejecución y borraba el trabajo del estudiante | Al reejecutar el script, el registro se conserva |

No se modificaron `pyproject.toml` ni `uv.lock` del proyecto base, ni la lógica de `data.py`,
`impact.py`, `fairness.py`, `model.py` o `governance.py`.

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
  brechas son(point estimates) y deben leerse con esa incertidumbre.
- El caso es sintético: ninguna conclusión describe poblaciones, zonas o personas reales.
- La interpretación normativa (qué obligations aplican y quién responde) es del estudiante y debe
  poder defenderse sin el apoyo de esta herramienta.
