from statistics import mean, stdev


def calculate_z_score(
    values: list[float],
    current_value: float,
) -> tuple[float, float, float]:
    """
    Calculate mean, standard deviation and Z-score.

    Returns:
        (mean_value, standard_deviation, z_score)
    """

    if not values:
        raise ValueError("At least one historical value is required.")

    if len(values) == 1:
        return values[0], 0.0, 0.0

    average = mean(values)
    standard_deviation = stdev(values)

    if standard_deviation == 0:
        return average, 0.0, 0.0

    z_score = (
        (current_value - average)
        / standard_deviation
    )

    return (
        average,
        standard_deviation,
        z_score,
    )


def is_anomaly(
    z_score: float,
    threshold: float = 3.0,
) -> bool:
    """Return True when the absolute Z-score exceeds the threshold."""

    return abs(z_score) >= threshold


def get_severity(z_score: float) -> str:
    """Determine anomaly severity from the absolute Z-score."""

    score = abs(z_score)

    if score >= 5:
        return "CRITICAL"

    if score >= 4:
        return "HIGH"

    if score >= 3:
        return "MEDIUM"

    return "LOW"