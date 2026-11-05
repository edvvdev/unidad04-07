import argparse
import json
from pathlib import Path

from inf8239_u04.data import features, load_data, temporal_split
from inf8239_u04.fairness import audit, intersectional, soporte_insuficiente
from inf8239_u04.governance import load_config
from inf8239_u04.model import build_model, fit_measure_repeated

p=argparse.ArgumentParser(); p.add_argument("--model",choices=["logistic","tree"],default="logistic"); args=p.parse_args()
out=Path("reports/lab12")/args.model; out.mkdir(parents=True,exist_ok=True)
minimo=load_config()["gates"].get("min_intersectional_support",15)
df=load_data(); train,test=temporal_split(df); model=build_model(args.model); resources=fit_measure_repeated(model,features(train),train.target,f"models/{args.model}.joblib"); pred=model.predict(features(test))
overall,groups,diff=audit(test.target,pred,test.protected_group); _,inter,_=audit(test.target,pred,intersectional(test))
groups.to_csv(out/"fairness_by_group.csv"); soporte_insuficiente(inter,minimo).to_csv(out/"fairness_intersectional.csv")
(out/"global_metrics.json").write_text(json.dumps({"metrics":{k:float(v) for k,v in overall.items()},"differences":{k:float(v) for k,v in diff.items()},"resources":{"training_seconds_cota":resources["training_seconds_cota"],"model_kb":round(resources["model_kb"],2)}},indent=2),encoding="utf-8")
print(groups.round(3)); print(resources)
