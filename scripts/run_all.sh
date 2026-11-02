#!/usr/bin/env bash
# Ejecuta todo el flujo del Ejercicio 07 (evaluación de impacto y auditoría de equidad).
#
#   ./scripts/run_all.sh            # entorno → pruebas → LAB11 → LAB12 → notebook → PDF
#   SKIP_NOTEBOOK=1 ./scripts/run_all.sh   # omite el notebook (solo scripts y artefactos)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> 1/5. Entorno (uv)"
uv python install 3.12
uv sync --frozen
# Jupyter, reportlab y matplotlib no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab matplotlib

echo "==> 2/5. Pruebas (esperado: 10 passed)"
uv run pytest -q

echo "==> 3/5. LAB11 · evaluación de impacto y registro de riesgos"
uv run python scripts/lab11_impact.py

echo "==> 4/5. LAB12 · auditoría de equidad (dos alternativas)"
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py

echo "==> 5/5. Notebook del Ejercicio 07 y PDF de síntesis"
if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
  uv run python -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio07_impacto_equidad.ipynb
else
  echo "    OMITIDO por SKIP_NOTEBOOK=1"
fi
REPO_URL="${REPO_URL:-https://github.com/edvvdev/unidad04-07}" \
  uv run python scripts/build_ejercicio07_pdf.py

echo "Listo. Revisa 'git status' y completa los campos PENDIENTE del PDF (nombre y matrícula)."
