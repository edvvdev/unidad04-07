import time
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


def build_model(kind="logistic"):
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["zone","age_band"]),
        ("num", StandardScaler(), ["previous_incidents","infrastructure_score","exposure"]),
    ])
    estimator = LogisticRegression(max_iter=1200, class_weight="balanced", random_state=42) if kind=="logistic" else DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42)
    return make_pipeline(prep, estimator)

def fit_measure(model, X, y, output="models/model.joblib"):
    start=time.perf_counter(); model.fit(X,y); seconds=time.perf_counter()-start
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,path)
    return {"training_seconds":seconds,"model_kb":path.stat().st_size/1024}

ESCALERA_COTA=(0.02,0.2,2.0,20.0,200.0)

def cota_tiempo(segundos):
    """Cota superior del tiempo de ejecucion, estable entre maquinas.

    El tiempo de ajuste depende de la carga del equipo: redondearlo a centesimas lo hacia oscilar
    entre 0.00 y 0.02 s en cada ejecucion. La cota se toma de una escalera fija ("menos de 0,02 s",
    "menos de 0,2 s", ...) con los escalones lejos de las medidas observadas, de modo que el
    artefacto versionado no cambie entre ejecuciones.
    """
    if segundos<=0: return 0.0
    for cota in ESCALERA_COTA:
        if segundos<=cota: return cota
    return ESCALERA_COTA[-1]

def fit_measure_repeated(model, X, y, output="models/model.joblib", repeticiones=5):
    """Como fit_measure, pero con el minimo de varias repeticiones del tiempo de ajuste.

    El minimo de N repeticiones es el estimador habitual del tiempo sin interferencias. El modelo
    guardado y su tamano son los de la ultima repeticion (deterministas con semilla fija).
    """
    tiempos=[]; resources={}
    for _ in range(repeticiones):
        resources=fit_measure(model,X,y,output); tiempos.append(resources["training_seconds"])
    minimo=min(tiempos)
    resources["training_seconds"]=round(minimo,4)
    resources["training_seconds_cota"]=cota_tiempo(minimo)
    return resources
