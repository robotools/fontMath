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
    return v1 - v2

def subPt(pt1, pt2):
    return pt1[0] - pt2[0], pt1[1] - pt2[1]

def mul(v, f):
    return v * f

def mulPt(pt1, f):
    (f1, f2) = f
    return pt1[0] * f1, pt1[1] * f2

def div(v, f):
    return v / f

def divPt(pt, f):
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
