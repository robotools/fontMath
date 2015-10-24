from __future__ import division
import math

__all__ = [
    "add",
    "addPt",
    "sub",
    "subPt",
    "mul",
    "mulPt",
    "div",
    "divPt",
    "factorAngle",
    "_roundNumber",

]

def add(v1, v2):
    return v1 + v2

def addPt(pt1, pt2):
    return pt1[0] + pt2[0], pt1[1] + pt2[1]

def sub(v1, v2):
    """
    >>> sub(10, 10)
    0
    >>> sub(10, -10)
    20
    >>> sub(-10, 10)
    -20
    """
    return v1 - v2

def subPt(pt1, pt2):
    """
    >>> pt1, pt2 = (20, 230), (50, 40)
    >>> subPt(pt1, pt2)
    (-30, 190)
    """
    return pt1[0] - pt2[0], pt1[1] - pt2[1]

def mul(v, f):
    return v * f

def mulPt(pt1, f):
    """
    >>> pt1, f1, f2 = (15, 25), 2, 3
    >>> mulPt(pt1, (f1, f2))
    (30, 75)
    """
    (f1, f2) = f
    return pt1[0] * f1, pt1[1] * f2

def div(v, f):
    """
    >>> div(4, 2) == 2
    True
    >>> div(4, 3) == 1.3333333333333333
    True
    """
    return v / f

def divPt(pt, f):
    """
    >>> pt1, f1, f2 = (15, 75), 2, 3
    >>> divPt(pt1, (f1, f2))
    (7.5, 25.0)
    """
    (f1, f2) = f
    return pt[0] / f1, pt[1] / f2

def factorAngle(angle, f, func):
    (f1, f2) = f
    rangle = math.radians(angle)
    x = math.cos(rangle)
    y = math.sin(rangle)
    return math.degrees(
        math.atan2(
            func(y, f2), func(x, f1)
        )
    )

def _roundNumber(n, digits=None):
    """
    round to integer:
    >>> _roundNumber(0)
    0
    >>> _roundNumber(0.1)
    0
    >>> _roundNumber(0.99)
    1
    >>> _roundNumber(0.499)
    0
    >>> _roundNumber(0.5)
    1
    >>> _roundNumber(-0.499)
    0
    >>> _roundNumber(-0.5)
    -1

    round to float with specified decimals:
    >>> _roundNumber(0.3333, None) == 0
    True
    >>> _roundNumber(0.3333, 0) == 0.0
    True
    >>> _roundNumber(0.3333, 1) == 0.3
    True
    >>> _roundNumber(0.3333, 2) == 0.33
    True
    >>> _roundNumber(0.3333, 3) == 0.333
    True
    """
    # Python3 rounds halves to nearest even integer but Python2 rounds
    # halves up in positives and down in negatives
    if round(0.5) != 1 and n % 1 == .5 and not int(n) % 2:
        if digits is None:
            return int((round(n) + (abs(n) / n) * 1))
        return int((round(n) + 1, digits))
    else:
        if digits is None:
            return int(round(n))
        return round(n, digits)

if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
