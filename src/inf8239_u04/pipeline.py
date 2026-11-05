import time

import pandas as pd
from sklearn.metrics import accuracy_score, recall_score

from .data import features, temporal_split
from .fairness import audit, gap, intersectional
from .governance import deployment_decision
from .model import build_model, fit_measure


def run(df, gates, kind="logistic"):
    train,test=temporal_split(df); model=build_model(kind); resources=fit_measure(model,features(train),train.target)
    start=time.perf_counter(); pred=model.predict(features(test)); resources["latency_ms"]=(time.perf_counter()-start)*1000/len(test)
    overall,by_group,_=audit(test.target,pred,test.protected_group)
    _,inter,_=audit(test.target,pred,intersectional(test))
    metrics={"accuracy":float(accuracy_score(test.target,pred)),"recall":float(recall_score(test.target,pred,zero_division=0))}
    recalls=pd.to_numeric(by_group["recall"],errors="coerce")
    metrics["worst_group_recall"]=float(recalls.min()); metrics["worst_group"]=str(recalls.idxmin())
    gaps={"recall_gap":gap(by_group,"recall"),"fpr_gap":gap(by_group,"fpr")}
    resources["min_intersectional_support"]=int(pd.to_numeric(inter["count"],errors="coerce").min())
    decision=deployment_decision(metrics,gaps,resources,gates)
    return {"model":model,"test":test,"pred":pred,"overall":overall,"by_group":by_group,"metrics":metrics,"gaps":gaps,"resources":resources,"decision":decision}
