def pounds_to_grams(value: float) -> int:
    return int(value * 453.59237)


def kilograms_to_grams(value: float) -> int:
    return int(value * 1000)


def grams_to_pounds(value: float) -> float:
    return value / 453.59237


def grams_to_kilograms(value: float) -> float:
    return value / 1000

