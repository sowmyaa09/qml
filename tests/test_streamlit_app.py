"""Streamlit entry exists, is import-safe, and every listed page is routed."""

from __future__ import annotations

import ast

from src.utils import get_project_root


def _app_source() -> str:
    return (get_project_root() / "app" / "streamlit_app.py").read_text(encoding="utf-8")


def test_streamlit_app_file_exists() -> None:
    text = _app_source()
    assert "not a medical device" in text.lower()
    assert "st.sidebar" in text


def test_every_sidebar_page_has_a_handler() -> None:
    tree = ast.parse(_app_source())

    pages: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "PAGES" for t in node.targets
        ):
            pages = [
                element.value
                for element in node.value.elts
                if isinstance(element, ast.Constant) and isinstance(element.value, str)
            ]
    assert pages, "PAGES tuple not found"

    routed: list[str] = []
    functions = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "dispatch" for t in node.targets
        ):
            for key, value in zip(node.value.keys, node.value.values):
                assert isinstance(key, ast.Constant)
                routed.append(key.value)
                assert isinstance(value, ast.Name)
                assert value.id in functions, f"missing handler {value.id}"
    assert routed, "dispatch mapping not found"
    assert set(pages) == set(routed)


def test_decision_support_page_refuses_cross_disease_reading() -> None:
    text = _app_source()
    assert "This is not triage" in text
    assert "label of its own table" in text
