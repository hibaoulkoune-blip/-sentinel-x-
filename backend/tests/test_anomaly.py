import pytest

from app.anomaly.detector import (
    calculate_z_score,
    get_severity,
    is_anomaly,
)


def test_calculate_z_score():
    values = [
        100,
        102,
        98,
        101,
        99,
        100,
        102,
        97,
        101,
        100,
    ]

    mean_value, standard_deviation, z_score = calculate_z_score(
        values=values,
        current_value=150,
    )

    assert mean_value == 100
    assert standard_deviation == pytest.approx(1.63299, rel=1e-4)
    assert z_score == pytest.approx(30.6186, rel=1e-4)


def test_calculate_z_score_empty_values():
    with pytest.raises(
        ValueError,
        match="At least one historical value is required.",
    ):
        calculate_z_score(
            values=[],
            current_value=100,
        )


def test_calculate_z_score_single_value():
    mean_value, standard_deviation, z_score = calculate_z_score(
        values=[100],
        current_value=150,
    )

    assert mean_value == 100
    assert standard_deviation == 0.0
    assert z_score == 0.0


def test_calculate_z_score_zero_standard_deviation():
    mean_value, standard_deviation, z_score = calculate_z_score(
        values=[100, 100, 100, 100, 100],
        current_value=150,
    )

    assert mean_value == 100
    assert standard_deviation == 0.0
    assert z_score == 0.0


def test_detect_anomaly():
    assert is_anomaly(3.0) is True
    assert is_anomaly(4.5) is True
    assert is_anomaly(-4.0) is True
    assert is_anomaly(2.9) is False


def test_anomaly_severity():
    assert get_severity(2.9) == "LOW"
    assert get_severity(3.0) == "MEDIUM"
    assert get_severity(4.0) == "HIGH"
    assert get_severity(5.0) == "CRITICAL"
