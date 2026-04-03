from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor


def sign(number: float) -> int:
    """Get sign of a number

    Parameters
    ----------
    number: float
        the number from who to get the sign
    """
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0


def refined_SL_values(SL: LineSensor) -> list:
    """Change the line sensor's values in 1 or 0 based on their value

    Parameters
    ----------
    SL: LineSensor (object)
        the number from who to get the sign
    """
    values = SL.readCalibrated()  # Get values from sensor

    refinedValues = []

    for value in values:
        if value > 500.0:
            refinedValues.append(1)

        elif value <= 500.0:
            refinedValues.append(0)

    return refinedValues
