from mathFunctions import *

__all__ = [
    "_expandGuideline",
    "_compressGuideline",
    "_pairGuidelines",
    "_processMathOneGuidelines",
    "_processMathTwoGuidelines",
    "_roundGuidelines"
]

def _expandGuideline(guideline):
    """
    >>> guideline = dict(x=100, y=None, angle=None)
    >>> sorted(_expandGuideline(guideline).items())
    [('angle', 90), ('x', 100), ('y', 0)]

    >>> guideline = dict(y=100, x=None, angle=None)
    >>> sorted(_expandGuideline(guideline).items())
    [('angle', 0), ('x', 0), ('y', 100)]
    """
    guideline = dict(guideline)
    x = guideline.get("x")
    y = guideline.get("y")
    # horizontal
    if x is None:
        guideline["x"] = 0
        guideline["angle"] = 0
    # vertical
    elif y is None:
        guideline["y"] = 0
        guideline["angle"] = 90
    return guideline

def _compressGuideline(guideline):
    """
    >>> guideline = dict(x=100, y=0, angle=90)
    >>> sorted(_compressGuideline(guideline).items())
    [('angle', None), ('x', 100), ('y', None)]

    >>> guideline = dict(x=100, y=0, angle=270)
    >>> sorted(_compressGuideline(guideline).items())
    [('angle', None), ('x', 100), ('y', None)]

    >>> guideline = dict(y=100, x=0, angle=0)
    >>> sorted(_compressGuideline(guideline).items())
    [('angle', None), ('x', None), ('y', 100)]

    >>> guideline = dict(y=100, x=0, angle=180)
    >>> sorted(_compressGuideline(guideline).items())
    [('angle', None), ('x', None), ('y', 100)]
    """
    guideline = dict(guideline)
    x = guideline["x"]
    y = guideline["y"]
    angle = guideline["angle"]
    # horizontal
    if x == 0 and angle in (0, 180):
        guideline["x"] = None
        guideline["angle"] = None
    # vertical
    elif y == 0 and angle in (90, 270):
        guideline["y"] = None
        guideline["angle"] = None
    return guideline

def _pairGuidelines(guidelines1, guidelines2):
    """
    name + identifier + (x, y, angle)
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="foo", identifier="2", x=3, y=4, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="foo", identifier="2", x=3, y=4, angle=2),
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1)
    ...     ),
    ...     (
    ...         dict(name="foo", identifier="2", x=3, y=4, angle=2),
    ...         dict(name="foo", identifier="2", x=3, y=4, angle=2)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True

    name + identifier
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="foo", identifier="2", x=1, y=2, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="foo", identifier="2", x=3, y=4, angle=3),
    ...     dict(name="foo", identifier="1", x=3, y=4, angle=4)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="foo", identifier="1", x=3, y=4, angle=4)
    ...     ),
    ...     (
    ...         dict(name="foo", identifier="2", x=1, y=2, angle=2),
    ...         dict(name="foo", identifier="2", x=3, y=4, angle=3)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True

    name + (x, y, angle)
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="foo", identifier="2", x=3, y=4, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="foo", identifier="3", x=3, y=4, angle=2),
    ...     dict(name="foo", identifier="4", x=1, y=2, angle=1)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="foo", identifier="4", x=1, y=2, angle=1)
    ...     ),
    ...     (
    ...         dict(name="foo", identifier="2", x=3, y=4, angle=2),
    ...         dict(name="foo", identifier="3", x=3, y=4, angle=2)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True

    identifier + (x, y, angle)
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="bar", identifier="2", x=3, y=4, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="xxx", identifier="2", x=3, y=4, angle=2),
    ...     dict(name="yyy", identifier="1", x=1, y=2, angle=1)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="yyy", identifier="1", x=1, y=2, angle=1)
    ...     ),
    ...     (
    ...         dict(name="bar", identifier="2", x=3, y=4, angle=2),
    ...         dict(name="xxx", identifier="2", x=3, y=4, angle=2)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True

    name
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="bar", identifier="2", x=1, y=2, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="bar", identifier="3", x=3, y=4, angle=3),
    ...     dict(name="foo", identifier="4", x=3, y=4, angle=4)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="foo", identifier="4", x=3, y=4, angle=4)
    ...     ),
    ...     (
    ...         dict(name="bar", identifier="2", x=1, y=2, angle=2),
    ...         dict(name="bar", identifier="3", x=3, y=4, angle=3)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True

    identifier
    >>> guidelines1 = [
    ...     dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...     dict(name="bar", identifier="2", x=1, y=2, angle=2),
    ... ]
    >>> guidelines2 = [
    ...     dict(name="xxx", identifier="2", x=3, y=4, angle=3),
    ...     dict(name="yyy", identifier="1", x=3, y=4, angle=4)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(name="foo", identifier="1", x=1, y=2, angle=1),
    ...         dict(name="yyy", identifier="1", x=3, y=4, angle=4)
    ...     ),
    ...     (
    ...         dict(name="bar", identifier="2", x=1, y=2, angle=2),
    ...         dict(name="xxx", identifier="2", x=3, y=4, angle=3)
    ...     )
    ... ]
    >>> _pairGuidelines(guidelines1, guidelines2) == expected
    True
    """
    guidelines1 = list(guidelines1)
    guidelines2 = list(guidelines2)
    pairs = []
    # name + identifier + (x, y, angle)
    _findPair(guidelines1, guidelines2, pairs, ("name", "identifier", "x", "y", "angle"))
    # name + identifier matches
    _findPair(guidelines1, guidelines2, pairs, ("name", "identifier"))
    # name + (x, y, angle)
    _findPair(guidelines1, guidelines2, pairs, ("name", "x", "y", "angle"))
    # identifier + (x, y, angle)
    _findPair(guidelines1, guidelines2, pairs, ("identifier", "x", "y", "angle"))
    # name matches
    if guidelines1 and guidelines2:
        _findPair(guidelines1, guidelines2, pairs, ("name",))
    # identifier matches
    if guidelines1 and guidelines2:
        _findPair(guidelines1, guidelines2, pairs, ("identifier",))
    # done
    return pairs

def _findPair(guidelines1, guidelines2, pairs, attrs):
    removeFromGuidelines1 = []
    for guideline1 in guidelines1:
        match = None
        for guideline2 in guidelines2:
            attrMatch = False not in [guideline1.get(attr) == guideline2.get(attr) for attr in attrs]
            if attrMatch:
                match = guideline2
                break
        if match is not None:
            guideline2 = match
            removeFromGuidelines1.append(guideline1)
            guidelines2.remove(guideline2)
            pairs.append((guideline1, guideline2))

def _processMathOneGuidelines(guidelinePairs, ptFunc, func):
    """
    >>> guidelines = [
    ...     (
    ...         dict(x=1, y=3, angle=5, name="test", identifier="1", color="0,0,0,0"),
    ...         dict(x=6, y=8, angle=10, name=None, identifier=None, color=None)
    ...     )
    ... ]
    >>> expected = [
    ...     dict(x=7, y=11, angle=15, name="test", identifier="1", color="0,0,0,0")
    ... ]
    >>> _processMathOneGuidelines(guidelines, addPt, add) == expected
    True
    """
    result = []
    for guideline1, guideline2 in guidelinePairs:
        guideline = dict(guideline1)
        pt1 = (guideline1["x"], guideline1["y"])
        pt2 = (guideline2["x"], guideline2["y"])
        guideline["x"], guideline["y"] = ptFunc(pt1, pt2)
        angle1 = guideline1["angle"]
        angle2 = guideline2["angle"]
        guideline["angle"] = func(angle1, angle2)
        result.append(guideline)
    return result

def _processMathTwoGuidelines(guidelines, factor, func):
    """
    >>> guidelines = [
    ...     dict(x=2, y=3, angle=5, name="test", identifier="1", color="0,0,0,0")
    ... ]
    >>> expected = [
    ...     dict(x=4, y=4.5, angle=3.75, name="test", identifier="1", color="0,0,0,0")
    ... ]
    >>> result = _processMathTwoGuidelines(guidelines, (2, 1.5), mul)
    >>> result[0]["angle"] = round(result[0]["angle"], 2)
    >>> result == expected
    True
    """
    result = []
    for guideline in guidelines:
        guideline = dict(guideline)
        guideline["x"] = func(guideline["x"], factor[0])
        guideline["y"] = func(guideline["y"], factor[1])
        angle = guideline["angle"]
        guideline["angle"] = factorAngle(angle, factor, func)
        result.append(guideline)
    return result

def _roundGuidelines(guidelines, digits=None):
    """
    >>> guidelines = [
    ...     dict(x=1.99, y=3.01, angle=5, name="test", identifier="1", color="0,0,0,0")
    ... ]
    >>> expected = [
    ...     dict(x=2, y=3, angle=5, name="test", identifier="1", color="0,0,0,0")
    ... ]
    >>> result = _roundGuidelines(guidelines)
    >>> result == expected
    True
    """
    results = []
    for guideline in guidelines:
        guideline = dict(guideline)
        guideline['x'] = _roundNumber(guideline['x'], digits)
        guideline['y'] = _roundNumber(guideline['y'], digits)
        results.append(guideline)
    return results



if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
