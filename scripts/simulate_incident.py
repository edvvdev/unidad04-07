from datetime import datetime,timezone
from pathlib import Path
text = (
    "# Incident simulation\n\n"
    f"- detected_at: {datetime.now(timezone.utc).isoformat()}\n"
    "- signal: recall gap exceeded\n"
    "- containment: REVIEW and safe baseline\n"
    "- evidence: preserved report and model version\n"
    "- communication: REPLACE\n"
    "- corrective actions, owners and dates: REPLACE\n"
)
path=Path("reports/lab13/INCIDENT_POSTMORTEM.md"); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8"); print(path)
