from Alphabot_lib.AlphaBotLineSensor import AlphaBotLineSensor as LineSensor


def sign(number: float) -> int:
    """Get sign of a number

    Parameters
    ----------
    number: float
        the number from who to get the sign

    >>sign(-2.5)
    -1
    >>sign(57)
    1
    >>sign(0)
    0
    """
    if number > 0:
        return 1
    elif number < 0:
        return -1
    else:
        return 0

def grille_pix(px:int, py:int, ecart:int, nb:int):
    offset = (nb // 2) * ecart
    
    pix = []
    for x in range(nb):
        for y in range(nb):
            pix.append((px - offset + x * ecart,
                        py - offset + y * ecart))
    return pix
