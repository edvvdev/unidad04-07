from inf8239_u04.data import features, load_data, temporal_split
from inf8239_u04.model import build_model
from inf8239_u04.pipeline import run


def test_predictions_are_binary():
    tr,te=temporal_split(load_data()); p=build_model().fit(features(tr),tr.target).predict(features(te)); assert set(p)<={0,1}
def test_pipeline_reports_worst_group_and_support():
    resultado=run(load_data(),{"min_recall":.68,"max_recall_gap":.16,"max_fpr_gap":.16,"max_latency_ms":500,"max_model_kb":1024,"min_worst_group_recall":.70,"max_recall_gap_pilot":.10,"min_intersectional_support":15,"stop_recall_gap":.15,"stop_worst_group_recall":.60})
    assert resultado["metrics"]["worst_group"]=="G1"; assert round(resultado["metrics"]["worst_group_recall"],4)==0.6531
    assert resultado["resources"]["min_intersectional_support"]==8; assert resultado["decision"]["status"]=="REVIEW"
