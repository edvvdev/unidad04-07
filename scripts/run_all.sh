#!/usr/bin/env bash
# Ejecuta todo el flujo del Ejercicio 07 (evaluación de impacto y auditoría de equidad).
#
#   ./scripts/run_all.sh            # entorno → pruebas → LAB11 → LAB12 → LAB13 → notebook → PDF
#   SKIP_NOTEBOOK=1 ./scripts/run_all.sh   # omite el notebook (solo scripts y artefactos)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> 1/7. Entorno (uv)"
uv python install 3.12
uv sync --frozen
# Jupyter, reportlab y matplotlib no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab matplotlib

echo "==> 2/7. Pruebas"
uv run pytest -q

echo "==> 3/7. LAB11 · evaluación de impacto y registro de riesgos"
uv run python scripts/lab11_impact.py

echo "==> 4/7. LAB12 · auditoría de equidad (dos alternativas)"
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py

echo "==> 5/7. LAB13 · puertas de gobernanza y decisión de despliegue"
uv run python scripts/lab13_governance.py

echo "==> 6/7. Simulacro de incidente (postmortem)"
uv run python scripts/simulate_incident.py

echo "==> 7/7. Notebook del Ejercicio 07, figuras y PDF de síntesis"
if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
  uv run python -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio07_impacto_equidad.ipynb
  uv run python scripts/limpiar_marcas_tiempo_notebook.py
else
  echo "    OMITIDO por SKIP_NOTEBOOK=1"
fi
export REPO_URL="${REPO_URL:-https://github.com/edvvdev/unidad04-07}"
uv run python scripts/make_figures.py
uv run python scripts/build_ejercicio07_pdf.py

echo "Listo. Revisa 'git status' y el estado de las puertas en reports/lab13/deployment_decision.json."
