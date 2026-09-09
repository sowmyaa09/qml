"""Cost/latency dashboard payload."""

from src.qml_cost_dashboard import build_cost_latency_payload


def test_payload_has_ablation_and_insight() -> None:
    payload = build_cost_latency_payload()
    assert payload["ablation_source"] in ("live", "fallback")
    assert any(row["model"] == "QSVC" for row in payload["ablation"])
    assert payload["insight"]["qsvc_f1"] is not None
    assert payload["insight"]["latency_ratio"] >= 1
