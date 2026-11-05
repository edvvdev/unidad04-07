from datetime import UTC, datetime
from pathlib import Path

text = (
    "# Incident simulation\n\n"
    f"- detected_at: {datetime.now(UTC).isoformat()}\n"
    "- signal: brecha de recall por encima del umbral de piloto (0,10)\n"
    "- containment: REVIEW and safe baseline\n"
    "- evidence: preserved report and model version\n"
    "- communication: la Direccion del programa avisa a los analistas y al canal de apelacion; "
    "no hay decision automatizada sobre personas, asi que no se notifica a nadie por una "
    "priorizacion del modelo\n"
    "- corrective actions, owners and dates: repetir la auditoria de equidad sobre el periodo "
    "posterior (Responsable de equidad, 30 dias); cuantificar el coste del falso negativo "
    "(Coordinador de operacion, 30 dias); revisar la cola manual por severidad reportada "
    "(Analista de riesgo responsable de la jornada, 15 dias)\n"
)
path=Path("reports/lab13/INCIDENT_POSTMORTEM.md"); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); print(path)
