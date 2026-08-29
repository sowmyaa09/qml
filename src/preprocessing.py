"""Train/test split. Scaling for Logistic Regression lives in the Pipeline."""

from __future__ import annotations

from sklearn.model_selection import train_test_split

RANDOM_STATE = 42
TEST_SIZE = 0.20


def stratified_train_test_split(
    features,
    target,
    *,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    """Split rows into train (80%) and test (20%), keeping class balance.

    Stratify means both classes (malignant and benign) appear in train and
    test in similar proportions. ``random_state`` makes the split repeatable.

    We split **before** any scaling. The scaler must learn means and
    standard deviations from training data only (no test-set leakage).
    """
    if len(features) != len(target):
        raise ValueError(
            f"Features have {len(features)} rows but target has {len(target)}. "
            "They must match."
        )

    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )
