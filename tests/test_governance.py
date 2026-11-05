import pandas as pd
import pytest

from inf8239_u04.governance import deployment_decision, validate_raci

PUERTAS_BASE={"min_recall":.68,"max_recall_gap":.16,"max_fpr_gap":.16,"max_latency_ms":500,"max_model_kb":1024}
PUERTAS_LAB12={**PUERTAS_BASE,"min_worst_group_recall":.70,"max_recall_gap_pilot":.10,"min_intersectional_support":15,"stop_recall_gap":.15,"stop_worst_group_recall":.60}
def test_failed_gate_requires_review():
    d=deployment_decision({"recall":.5},{"recall_gap":.1,"fpr_gap":.1},{"latency_ms":1,"model_kb":5},{"min_recall":.7,"max_recall_gap":.2,"max_fpr_gap":.2,"max_latency_ms":10,"max_model_kb":20}); assert d["status"]=="REVIEW"
def test_raci_requires_accountable():
    with pytest.raises(ValueError): validate_raci(pd.DataFrame([{"activity":"deploy","R":"ML","A":"","C":"DS","I":"Users"}]))
def test_base_gates_alone_keep_go():
    d=deployment_decision({"recall":.7174},{"recall_gap":.1376,"fpr_gap":.125},{"latency_ms":1,"model_kb":3.56},PUERTAS_BASE); assert d["status"]=="GO"
def test_all_gates_pass_is_go():
    d=deployment_decision({"recall":.9,"worst_group_recall":.85},{"recall_gap":.05,"fpr_gap":.05},{"latency_ms":1,"model_kb":5,"min_intersectional_support":30},PUERTAS_LAB12); assert d["status"]=="GO"; assert d["failed"]==[]
def test_lab12_gates_fail_and_state_is_review():
    d=deployment_decision({"recall":.7174,"worst_group_recall":.6531},{"recall_gap":.1376,"fpr_gap":.125},{"latency_ms":1,"model_kb":3.56,"min_intersectional_support":8},PUERTAS_LAB12)
    assert d["status"]=="REVIEW"; assert d["failed"]==["worst_group_recall","recall_gap_pilot","intersectional_support"]; assert d["escalation_triggered"]==[]
def test_recall_gap_escalates_to_stop():
    d=deployment_decision({"recall":.9,"worst_group_recall":.85},{"recall_gap":.2,"fpr_gap":.05},{"latency_ms":1,"model_kb":5,"min_intersectional_support":30},PUERTAS_LAB12)
    assert d["status"]=="STOP"; assert d["escalation_triggered"]==["stop_recall_gap"]
def test_worst_group_recall_escalates_to_stop():
    d=deployment_decision({"recall":.9,"worst_group_recall":.55},{"recall_gap":.05,"fpr_gap":.05},{"latency_ms":1,"model_kb":5,"min_intersectional_support":30},PUERTAS_LAB12)
    assert d["status"]=="STOP"; assert d["escalation_triggered"]==["stop_worst_group_recall"]
