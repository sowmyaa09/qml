"""Field-name catalog detection. Not a diagnosis switcher."""

from src.catalog_schemas import auto_detect_schema_detailed


def test_detects_every_small_schema_from_its_own_columns() -> None:
    from src.catalog_schemas import SCHEMAS

    for key, schema in SCHEMAS.items():
        if len(schema.features) > 40:
            continue
        take = list(schema.features)[: max(schema.min_filled, 6)]
        text = "\n".join(f"{name}: 1" for name in take)
        found, _pct, _schema, confident, count = auto_detect_schema_detailed(text)
        assert confident, key
        assert count >= 3, key
        if key in {"heart_disease", "heart_uci_pooled"}:
            assert found in {"heart_disease", "heart_uci_pooled"}
        elif key == "wisconsin":
            assert found in {"wisconsin", "wisconsin_reduced"}
        else:
            assert found == key, (key, found)


def test_age_alone_is_not_a_disease_switch() -> None:
    _key, _pct, _schema, confident, _n = auto_detect_schema_detailed("age: 54")
    assert confident is False
