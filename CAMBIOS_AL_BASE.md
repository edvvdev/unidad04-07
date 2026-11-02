# Correcciones sobre el proyecto base del profesor

Proyecto base: `INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv`. No se modificaron `pyproject.toml` ni
`uv.lock`, ni la lógica de `src/inf8239_u04/` (`data`, `impact`, `fairness`, `model`, `governance`,
`pipeline`).

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
`REPLACE`, borrando el registro redactado por el estudiante.

**Corrección:** el script solo escribe la plantilla si el archivo no existe o si todavía contiene el
marcador `REPLACE`. Verificado: tras escribir el registro, una nueva ejecución lo conserva.

## 3. `uv.lock` generado

El ZIP del profesor no incluye `uv.lock`, y el manual indica `uv sync --frozen`, que exige un lock
existente. Se generó con `uv lock` sobre el `pyproject.toml` del profesor (55 paquetes resueltos);
`pyproject.toml` no se tocó.

## 4. Dependencia de trabajo para las figuras

El proyecto base declara `plotly`; el notebook del Ejercicio 07 exporta las figuras en PNG porque el
PDF de entrega las necesita, y para eso usa `matplotlib`. Se instala como dependencia de trabajo
(`uv pip install matplotlib`, documentada en `requirements-dev.txt` y en `scripts/run_all.sh`), sin
modificar `pyproject.toml` ni el lock.

## 5. Notebook: directorio de trabajo

El kernel de Jupyter arranca en `notebooks/`, y los scripts del base resuelven el dataset con rutas
relativas a la raíz del proyecto. La primera celda del notebook hace `os.chdir(ROOT)` y lo documenta.

## Verificación

```bash
uv sync --frozen && uv run pytest -q      # 10 passed
uv run python scripts/check_environment.py # dataset_status: valid
uv run python scripts/lab11_impact.py
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
```
