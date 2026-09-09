"""Plain-language field labels for catalog columns."""

from src.api_server import _slider_for
from src.feature_labels import description_for, label_for


def test_wisconsin_perimeter_and_radius_labels() -> None:
    assert "perimeter" in label_for("mean perimeter").lower()
    assert "nuclei" in label_for("worst radius").lower()
    assert "FNA" in description_for("mean perimeter") or "fine-needle" in description_for(
        "mean perimeter"
    ).lower()


def test_cp_full_form() -> None:
    assert label_for("cp") == "Chest Pain type (CP)"
    assert "typical angina" in description_for("cp")
    assert "headache" in description_for("cp").lower()


def test_slider_payload_includes_label() -> None:
    slider = _slider_for("worst perimeter")
    assert slider["name"] == "worst perimeter"
    assert slider["label"]
    assert slider["description"]
