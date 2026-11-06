# Ejecuta todo el flujo del Ejercicio 07 (evaluación de impacto y auditoría de equidad).
#   .\scripts\run_all.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> 1/8. Entorno (uv)" -ForegroundColor Cyan
uv python install 3.12
uv sync --frozen
# Jupyter, reportlab y matplotlib no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab matplotlib

Write-Host "==> 2/8. Pruebas" -ForegroundColor Cyan
uv run pytest -q

Write-Host "==> 3/8. LAB11 · evaluación de impacto y registro de riesgos" -ForegroundColor Cyan
uv run python scripts/lab11_impact.py

Write-Host "==> 4/8. LAB12 · auditoría de equidad (dos alternativas)" -ForegroundColor Cyan
uv run python scripts/lab12_audit.py --model logistic
uv run python scripts/lab12_audit.py --model tree
uv run python scripts/validate_lab12_decision.py
uv run pytest -q tests/test_impact.py tests/test_privacy.py tests/test_fairness.py tests/test_model.py

Write-Host "==> 5/8. LAB13 · puertas de gobernanza y decisión de despliegue" -ForegroundColor Cyan
uv run python scripts/lab13_governance.py

Write-Host "==> 6/8. Simulacro de incidente (postmortem)" -ForegroundColor Cyan
uv run python scripts/simulate_incident.py

Write-Host "==> 7/8. Cifras del dataset (tasas calculadas y bloques de la documentación)" -ForegroundColor Cyan
uv run python scripts/dataset_stats.py

Write-Host "==> 8/8. Notebook del Ejercicio 07, figuras y PDF de síntesis" -ForegroundColor Cyan
if ($env:SKIP_NOTEBOOK -ne "1") {
    uv run python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio07_impacto_equidad.ipynb
    uv run python scripts/limpiar_marcas_tiempo_notebook.py
} else {
    Write-Host "    OMITIDO por SKIP_NOTEBOOK=1" -ForegroundColor DarkGray
}
if (-not $env:REPO_URL) { $env:REPO_URL = "https://github.com/edvvdev/unidad04-07" }
uv run python scripts/make_figures.py
uv run python scripts/build_ejercicio07_pdf.py

Write-Host "Listo. Revisa 'git status' y el estado de las puertas en reports/lab13/deployment_decision.json." -ForegroundColor Green
