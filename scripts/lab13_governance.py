import json
from pathlib import Path

import pandas as pd

from inf8239_u04.data import load_data
from inf8239_u04.governance import load_config, validate_raci
from inf8239_u04.pipeline import run

cfg=load_config(); validate_raci(pd.read_csv("student_inputs/raci.csv")); result=run(load_data(),cfg["gates"])
out=Path("reports/lab13"); out.mkdir(parents=True,exist_ok=True)
payload={"gates":cfg["gates"],"metrics":result["metrics"],"gaps":result["gaps"],"resources":{"model_kb":round(result["resources"]["model_kb"],2),"min_intersectional_support":result["resources"]["min_intersectional_support"]},"decision":result["decision"],"nota":"Los tiempos de ejecucion (latencia y segundos de entrenamiento) no se versionan: son medidas no deterministas. La puerta de latencia se verifica en cada ejecucion y su resultado queda en decision.checks.latency."}
(out/"deployment_decision.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
result["by_group"].to_csv(out/"fairness_by_group.csv"); print(result["decision"])
