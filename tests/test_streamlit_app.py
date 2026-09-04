"""Streamlit entry exists and is import-safe."""

from src.utils import get_project_root


def test_streamlit_app_file_exists() -> None:
    path = get_project_root() / "app" / "streamlit_app.py"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "not a medical device" in text.lower()
    assert "st.sidebar" in text
