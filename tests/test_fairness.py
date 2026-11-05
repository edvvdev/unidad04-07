from inf8239_u04.data import features, load_data, temporal_split
from inf8239_u04.fairness import audit, gap, intersectional, soporte_insuficiente
from inf8239_u04.model import build_model


def test_fairness_metrics_are_bounded():
    tr,te=temporal_split(load_data()); m=build_model().fit(features(tr),tr.target); _,g,_=audit(te.target,m.predict(features(te)),te.protected_group)
    assert 0<=gap(g,"recall")<=1; assert set(g.index)=={"G1","G2"}
def test_intersectional_support_flag_marks_small_cells():
    tr,te=temporal_split(load_data()); m=build_model().fit(features(tr),tr.target); _,inter,_=audit(te.target,m.predict(features(te)),intersectional(te))
    tabla=soporte_insuficiente(inter,15); assert "soporte_insuficiente" in tabla.columns
    assert int(tabla["soporte_insuficiente"].sum())==3
    assert list(tabla.loc[tabla["soporte_insuficiente"],"count"])==[11.0,14.0,8.0]
