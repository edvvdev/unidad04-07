# Correcciones sobre el proyecto base del profesor

Proyecto base: `INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv`. No se modificaron `pyproject.toml` ni
`uv.lock`.

## 1. `scripts/lab11_impact.py` y `scripts/simulate_incident.py` no compilaban

**Síntoma:**

```
SyntaxError: unterminated string literal      (lab11_impact.py, línea 11)
SyntaxError: unterminated f-string literal     (simulate_incident.py, línea 3)
```

**Causa:** en el ZIP del profesor los literales de cadena multilínea llegaron con saltos de línea
reales en lugar de `\n` escapados, de modo que el archivo no es Python válido.

**Corrección:** se re-escribieron los dos literales con `\n` escapados. No cambia la lógica: el
primer script sigue generando `reports/lab11/risk_register_scored.csv`, `stakeholders.csv`,
`rmf_summary.json` y la plantilla del registro de decisión; el segundo sigue escribiendo el
postmortem del incidente simulado.

## 2. `scripts/lab11_impact.py` ya no sobrescribe el registro de decisión

**Síntoma:** cada ejecución del script reescribía `reports/lab11/DECISION_RECORD.md` con la plantilla
de marcadores sin resolver, borrando el registro redactado por el estudiante.

**Corrección:** el script solo escribe la plantilla si el archivo no existe o si todavía contiene el
marcador. Verificado: tras escribir el registro, una nueva ejecución lo conserva.

## 3. `uv.lock` generado

El ZIP del profesor no incluye `uv.lock`, y el manual indica `uv sync --frozen`, que exige un lock
existente. Se generó con `uv lock` sobre el `pyproject.toml` del profesor; `pyproject.toml` no se tocó.

## 4. Dependencia de trabajo para las figuras

El proyecto base declara `plotly`; el notebook del Ejercicio 07 exporta las figuras en PNG porque el
PDF de entrega las necesita, y para eso usa `matplotlib`. Se instala como dependencia de trabajo
(`uv pip install matplotlib`, documentada en `requirements-dev.txt` y en `scripts/run_all.sh`), sin
modificar `pyproject.toml` ni el lock.

## 5. Notebook: directorio de trabajo

El kernel de Jupyter arranca en `notebooks/`, y los scripts del base resuelven el dataset con rutas
relativas a la raíz del proyecto. La primera celda del notebook hace `os.chdir(ROOT)` y lo documenta.

---

# Revisión de coherencia de la entrega (2026-11-05)

Defectos corregidos tras la auditoría de la entrega publicada. Cada punto indica el antes y el
después.

## 6. D1 · La decisión era incoherente en cuatro artefactos

**Antes:** con los umbrales base de `configs/governance.yml` (`min_recall 0.68`, `max_recall_gap
0.16`, `max_fpr_gap 0.16`), `deployment_decision` devolvía **GO**; el README decía **LIMITAR**, el
registro de decisión decía **REVIEW** y el YAML prometía **STOP**, un estado que el código no
implementaba.

**Corrección (aditiva, el base no cambia de comportamiento):**

| Fichero | Cambio |
|---|---|
| `configs/governance.yml` | Se declaran `min_worst_group_recall: 0.70`, `max_recall_gap_pilot: 0.10`, `min_intersectional_support: 15` y los umbrales de escalamiento `stop_recall_gap: 0.15` y `stop_worst_group_recall: 0.60` |
| `src/inf8239_u04/governance.py` | `deployment_decision` evalúa las tres puertas nuevas **solo si están declaradas** en la configuración y añade el estado **STOP** cuando se incumple un umbral `stop_*`; con los umbrales base el resultado sigue siendo GO/REVIEW |
| `src/inf8239_u04/pipeline.py` | Calcula `worst_group_recall`, `worst_group` y `min_intersectional_support` (referencia de estilo: el Ejercicio 08 resuelve lo mismo) |
| `README.md`, `reports/lab11/DECISION_RECORD.md`, `student_inputs/lab12_decision.yml` (`tolerance` y `recommendation`), PDF | Se unifica la redacción: **decisión documentada LIMITAR** (piloto en modo REVIEW, revisión humana obligatoria, baseline sin modelo como camino seguro), **estado del pipeline REVIEW** (fallan `worst_group_recall` 0,6531 < 0,70, `recall_gap_pilot` 0,1376 > 0,10 e `intersectional_support` 8 < 15) y **escalamiento a STOP** (brecha > 0,15 o peor grupo < 0,60 ⇒ retirada al baseline sin modelo) |

**Estado final de las puertas** (`reports/lab13/deployment_decision.json`): `recall` ✓, `recall_gap` ✓,
`fpr_gap` ✓, `latency` ✓, `model_size` ✓, `worst_group_recall` ✗, `recall_gap_pilot` ✗,
`intersectional_support` ✗ → **REVIEW**; ningún umbral de escalamiento se dispara.

## 7. D2 · `reports/lab13/deployment_decision.json` no existía

El riesgo R07 lo cita como evidencia. Ahora `scripts/lab13_governance.py` lo genera y queda
versionado, y `scripts/run_all.sh` (y `run_all.ps1`) lo ejecutan en la ruta documentada, junto con
`scripts/simulate_incident.py`. La figura `reports/lab13/puertas_calidad.png` se genera a partir de
ese artefacto.

## 8. D3 · Cifras erróneas en el PDF

**Antes:** «Tasa base de positivos en la prueba: **G1 23,9 %**» (real 48,5 %) y «datos completos:
49,6 %» (real 49,7 %).

**Corrección:** `scripts/build_ejercicio07_pdf.py` ya no contiene esos literales: las tasas se calculan
desde `data/territorial_risk_synthetic.csv` con el corte temporal del repo (`load_data` +
`temporal_split`) y se muestran en una tabla. Valores reales: prueba G1 **48,5 %** y G2 **72,9 %**;
datos completos G1 **49,7 %** y G2 **63,9 %**. El README y el registro de decisión se corrigen con los
mismos valores.

## 9. D4 · Celdas con soporte insuficiente sin marcar

**Antes:** los CSV interseccionales no marcaban nada y el conteo era 2 en README/YAML/registro frente
a 3 en el PDF y la figura.

**Corrección:** `src/inf8239_u04/fairness.py` añade `soporte_insuficiente(inter, minimo)`;
`scripts/lab12_audit.py` escribe la columna en `reports/lab12/*/fairness_intersectional.csv` con el
umbral 15 leído de `configs/governance.yml`, y la figura y el PDF leen esa columna. Todos los
artefactos cuentan **3 celdas**: `G2 | 45-59` (n=8), `G2 | 18-29` (n=11) y `G2 | 30-44` (n=14).

## 10. D5 · Dos tablas del PDF ilegibles

**Antes:** en la página 1, la tabla de interesados y la de riesgos tenían texto solapado y recortado
(celdas de texto plano en columnas estrechas).

**Corrección:** ambas tablas se reconstruyen con celdas `Paragraph` (ajuste de línea automático),
anchos de columna que suman el ancho útil (18,59 cm), `leading` y `wordWrap` definidos, y `repeatRows`
para el encabezado. Verificado renderizando la página a PNG (`pdftoppm -png -r 100`): no hay
solapamiento. El PDF pasa de 6 a 7 páginas al añadir la sección de puertas.

## 11. D6 · Marcadores `REPLACE` de las plantillas del LAB13

`docs/MODEL_CARD.md` y `docs/RUNBOOK.md` son las plantillas del LAB13 (Ejercicio 08) que trae el base
y **no aplican** a este ejercicio. Se añade al inicio de cada una una línea que lo dice
explícitamente y se apunta a la documentación de entrega real del Ejercicio 07; no se inventa
contenido. Los únicos `REPLACE` que quedan en el repositorio son los de esas dos plantillas.

## 12. D7 · `docs/AI_USE_DECLARATION.md`

Se marcan las casillas de verificación con el comando y el **resultado real** (17 pruebas, ruff en
verde, `dataset_status: valid`, 9 riesgos, 3 celdas con soporte insuficiente, estado REVIEW con las
tres puertas, 7 figuras, contraste de cifras y comprobación del PDF). Se corrigen las afirmaciones
que la evidencia contradecía: ya no se afirma que no se tocara `governance.py` (ni `fairness.py` ni
`pipeline.py`) y se documenta la nueva ronda de correcciones.

## 13. Ejecución reproducible: `scripts/run_all.sh`

El flujo pasa de 5 a 7 pasos y añade LAB13 y el simulacro de incidente:

```
entorno → pruebas → LAB11 → LAB12 (logística y árbol) → LAB13 (puertas y decisión)
       → simulacro de incidente → notebook ejecutado → figuras → PDF de síntesis
```

Se añade `reports/lab12/tasas_base_positivos.png` (tasa base de positivos por grupo, calculada desde
los datos) y se genera la figura de puertas a partir del artefacto del LAB13. La figura
`reports/lab13/inventario_retencion.png` se retira de este ejercicio: el inventario y la retención son
del LAB13 del Ejercicio 08 y `configs/governance.yml` de este repositorio no los define (el script
base tampoco la generaba aquí).

## 14. Tiempos de ejecución no deterministas en los artefactos versionados

`training_seconds` y `latency_ms` dependen de la máquina: al reejecutar el flujo cambiaban de valor
(0,00 s / 0,01 s / 0,08 s) y dejaban el árbol de trabajo sucio. Solución:

- `src/inf8239_u04/model.py` añade `fit_measure_repeated` (mínimo de 5 repeticiones, estimador
  habitual del tiempo sin interferencias) y `cota_tiempo` (cota superior por escalera fija:
  0,02 s / 0,2 s / 2 s …). `fit_measure` del base no cambia.
- Los JSON versionados guardan `training_seconds_cota` (≤ 0,02 s para ambos modelos) y `model_kb`;
  no guardan tiempos crudos.
- La latencia por registro **no** se versiona: la puerta `latency` se verifica en cada ejecución y su
  resultado queda en `decision.checks.latency`.
- `scripts/limpiar_marcas_tiempo_notebook.py` elimina las marcas de tiempo de ejecución que Jupyter
  escribe en el notebook, de modo que el notebook versionado es idéntico al que genera otra máquina.

Con estos cambios, dos ejecuciones consecutivas de `scripts/run_all.sh` dejan el árbol de trabajo
sin diferencias.

## 15. `uv run ruff check .` en verde

El base arrastraba 29 hallazgos (orden de imports, imports sin uso, expresión inútil en el notebook,
`except Exception` ciego). Como `pyproject.toml` no se toca, los hallazgos se corrigen en el código:
se reordenan los imports, se eliminan los no usados (`pandas` en `governance.py` e `impact.py`), el
notebook deja de dejar `comparativa` como expresión suelta y `make_figures.py` captura excepciones
concretas en lugar de `Exception`. Resultado: `All checks passed!`.

## 16. Pruebas

`tests/` pasa de 10 a 17 pruebas: se cubren el estado GO con todas las puertas, el estado REVIEW con
las tres puertas del LAB12 fallidas, el escalamiento a STOP por brecha de recall y por recall del
peor grupo, el comportamiento con solo las puertas base, la marca de soporte insuficiente
(3 celdas) y los nuevos campos del pipeline (`worst_group`, `worst_group_recall`,
`min_intersectional_support`).

## 17. Notebook

Se ejecuta de nuevo (16 celdas, 0 errores) y se corrige: una palabra corrupta en la celda de
encuadre, la expresión suelta que ruff señalaba, la figura por grupo (etiquetas con `n`), el marcado
de soporte insuficiente por código (misma función y mismo umbral que los scripts), el redondeo de los
tiempos de entrenamiento y la conclusión (tasa base 49,7 %, tres celdas con soporte insuficiente y la
decisión unificada LIMITAR / REVIEW / STOP).

## Verificación

```bash
uv sync --frozen && uv run pytest -q      # 17 passed
uv run ruff check .                        # All checks passed!
uv run python scripts/check_environment.py # dataset_status: valid · 640 filas
uv run python scripts/lab11_impact.py
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
uv run python scripts/lab13_governance.py   # status REVIEW · 3 puertas fallidas
uv run python scripts/simulate_incident.py
uv run python scripts/make_figures.py       # 7 figuras OK
bash scripts/run_all.sh                     # flujo completo sin errores
```
