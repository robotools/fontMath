from __future__ import division, absolute_import
from fontMath.mathFunctions import *
from fontMath.mathGuideline import *


class MathInfo(object):

    def __init__(self, infoObject):
        for attr in _infoAttrs.keys():
            if hasattr(infoObject, attr):
                setattr(self, attr, getattr(infoObject, attr))
        if isinstance(infoObject, MathInfo):
            self.guidelines = [dict(guideline) for guideline in infoObject.guidelines]
        elif infoObject.guidelines is not None:
            self.guidelines = [_expandGuideline(guideline) for guideline in infoObject.guidelines]
        else:
            self.guidelines = []

    # ----
    # Copy
    # ----

    def copy(self):
        copied = MathInfo(self)
        return copied

    # ----
    # Math
    # ----

    # math with other info

    def __add__(self, otherInfo):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = MathInfo(_TestInfoObject())
        >>> info3 = info1 + info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info3, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v + v for v in value]
        ...     else:
        ...         expectedValue = value + value
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True

        data subset (1st operand)
        -------------------------
        >>> info1 = MathInfo(_TestInfoObject(_testDataSubset))
        >>> info2 = MathInfo(_TestInfoObject())
        >>> info3 = info1 + info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info3, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v + v for v in value]
        ...     else:
        ...         expectedValue = value + value
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True

        data subset (2nd operand)
        -------------------------
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = MathInfo(_TestInfoObject(_testDataSubset))
        >>> info3 = info1 + info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info3, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v + v for v in value]
        ...     else:
        ...         expectedValue = value + value
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        copiedInfo = self.copy()
        self._processMathOne(copiedInfo, otherInfo, addPt, add)
        return copiedInfo

    def __sub__(self, otherInfo):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = MathInfo(_TestInfoObject())
        >>> info3 = info1 - info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info3, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v - v for v in value]
        ...     else:
        ...         expectedValue = value - value
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        copiedInfo = self.copy()
        self._processMathOne(copiedInfo, otherInfo, subPt, sub)
        return copiedInfo

    def _processMathOne(self, copiedInfo, otherInfo, ptFunc, func):
        # basic attributes
        for attr in _infoAttrs.keys():
            a = None
            b = None
            v = None
            if hasattr(copiedInfo, attr):
                a = getattr(copiedInfo, attr)
            if hasattr(otherInfo, attr):
                b = getattr(otherInfo, attr)
            if a is not None and b is not None:
                if isinstance(a, (list, tuple)):
                    v = self._processMathOneNumberList(a, b, func)
                else:
                    v = self._processMathOneNumber(a, b, func)
            elif a is not None and b is None:
                v = a
            elif b is not None and a is None:
                v = b
            if v is not None:
                setattr(copiedInfo, attr, v)
        # special attributes
        self._processPostscriptWeightName(copiedInfo)
        # guidelines
        copiedInfo.guidelines = []
        if self.guidelines:
            guidelinePairs = _pairGuidelines(self.guidelines, otherInfo.guidelines)
            copiedInfo.guidelines = _processMathOneGuidelines(guidelinePairs, ptFunc, func)

    def _processMathOneNumber(self, a, b, func):
        return func(a, b)

    def _processMathOneNumberList(self, a, b, func):
        if len(a) != len(b):
            return None
        v = []
        for index, aItem in enumerate(a):
            bItem = b[index]
            v.append(func(aItem, bItem))
        return v

    # math with factor

    def __mul__(self, factor):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = info1 * 2.5
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info2, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v * 2.5 for v in value]
        ...     else:
        ...         expectedValue = value * 2.5
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True

        data subset
        -----------
        >>> info1 = MathInfo(_TestInfoObject(_testDataSubset))
        >>> info2 = info1 * 2.5
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testDataSubset.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info2, attr)
        ...     if attr == 'guidelines':
        ...         guidelines = [_expandGuideline(guideline) for guideline in value]
        ...         expectedValue = _processMathTwoGuidelines(guidelines, (2.5, 2.5), mul)
        ...     elif isinstance(value, list):
        ...         expectedValue = [v * 2.5 for v in value]
        ...     else:
        ...         expectedValue = value * 2.5
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        copiedInfo = self.copy()
        self._processMathTwo(copiedInfo, factor, mul)
        return copiedInfo

    __rmul__ = __mul__

    def __div__(self, factor):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = info1 / 2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info2, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v / 2 for v in value]
        ...     else:
        ...         expectedValue = value / 2
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        copiedInfo = self.copy()
        self._processMathTwo(copiedInfo, factor, div)
        return copiedInfo

    __truediv__ = __div__

    __rdiv__ = __div__

    __rtruediv__ = __rdiv__

    def _processMathTwo(self, copiedInfo, factor, func):
        # basic attributes
        for attr, (formatter, factorIndex) in _infoAttrs.items():
            if hasattr(copiedInfo, attr):
                v = getattr(copiedInfo, attr)
                if v is not None and factor is not None:
                    if factorIndex == 3:
                        v = self._processMathTwoAngle(v, factor, func)
                    else:
                        if isinstance(v, (list, tuple)):
                            v = self._processMathTwoNumberList(v, factor[factorIndex], func)
                        else:
                            v = self._processMathTwoNumber(v, factor[factorIndex], func)
                else:
                    v = None
                setattr(copiedInfo, attr, v)
        # special attributes
        self._processPostscriptWeightName(copiedInfo)
        # guidelines
        copiedInfo.guidelines = []
        if self.guidelines:
            copiedInfo.guidelines = _processMathTwoGuidelines(self.guidelines, factor, func)

    def _processMathTwoNumber(self, v, factor, func):
        return func(v, factor)

    def _processMathTwoNumberList(self, v, factor, func):
        return [func(i, factor) for i in v]

    def _processMathTwoAngle(self, angle, factor, func):
        return factorAngle(angle, factor, func)

    # special attributes

    def _processPostscriptWeightName(self, copiedInfo):
        """
        >>> info = MathInfo(_TestInfoObject())
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Medium'
        >>> info.openTypeOS2WeightClass = 549
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Medium'
        >>> info.openTypeOS2WeightClass = 550
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Semi-bold'
        >>> info.openTypeOS2WeightClass = 450
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Medium'
        >>> info.openTypeOS2WeightClass = 449
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Normal'
        >>> info.openTypeOS2WeightClass = 0
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Thin'
        >>> info.openTypeOS2WeightClass = -1000
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Thin'
        >>> info.openTypeOS2WeightClass = 1000
        >>> info._processPostscriptWeightName(info)
        >>> info.postscriptWeightName
        'Black'
        """
        # handle postscriptWeightName by taking the value
        # of openTypeOS2WeightClass and getting the closest
        # value from the OS/2 specification.
        name = None
        if hasattr(copiedInfo, "openTypeOS2WeightClass") and copiedInfo.openTypeOS2WeightClass is not None:
            v = copiedInfo.openTypeOS2WeightClass
            v = v * .01
            # Python3 rounds halves to nearest even integer
            # but Python2 rounds halves up.
            if round(0.5) != 1 and v % 1 == .5 and not int(v) % 2:
                v = int((round(v) + 1) * 100)
            else:
                v = int(round(v) * 100)
            v = int(round(v * .01) * 100)
            if v < 100:
                v = 100
            elif v > 900:
                v = 900
            name = _postscriptWeightNameOptions[v]
        copiedInfo.postscriptWeightName = name

    # ----------
    # More math
    # ----------

    def round(self, digits=None):
        """
        >>> m = _TestInfoObject()
        >>> m.ascender = 699.99
        >>> m.descender = -199.99
        >>> m.xHeight = 399.66
        >>> m.postscriptSlantAngle = None
        >>> m.postscriptStemSnapH = [80.1, 90.2]
        >>> m.guidelines = [{'y': 100.99, 'x': None, 'angle': None, 'name': 'bar'}]
        >>> m.italicAngle = -9.4
        >>> m.postscriptBlueScale = 0.137
        >>> info = MathInfo(m)
        >>> info = info.round()
        >>> info.ascender
        700
        >>> info.descender
        -200
        >>> info.xHeight
        400
        >>> m.italicAngle
        -9.4
        >>> m.postscriptBlueScale
        0.137
        >>> info.postscriptSlantAngle
        >>> info.postscriptStemSnapH
        [80, 90]
        >>> [sorted(gl.items()) for gl in info.guidelines]
        [[('angle', 0), ('name', 'bar'), ('x', 0), ('y', 101)]]
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [_roundNumber(v) for v in value]
        ...     else:
        ...         expectedValue = _roundNumber(value)
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        excludeFromRounding = ['postscriptBlueScale', 'italicAngle']
        copiedInfo = self.copy()
        # basic attributes
        for attr, (formatter, factorIndex) in _infoAttrs.items():
            if attr in excludeFromRounding:
                continue
            if hasattr(copiedInfo, attr):
                v = getattr(copiedInfo, attr)
                if v is not None:
                    if factorIndex == 3:
                        v = int(round(v))
                    else:
                        if isinstance(v, (list, tuple)):
                            v = [_roundNumber(a, digits) for a in v]
                        else:
                            v = _roundNumber(v, digits)
                else:
                    v = None
                setattr(copiedInfo, attr, v)
        # special attributes
        self._processPostscriptWeightName(copiedInfo)
        # guidelines
        copiedInfo.guidelines = []
        if self.guidelines:
            copiedInfo.guidelines = _roundGuidelines(self.guidelines, digits)
        return copiedInfo

    # ----------
    # Extraction
    # ----------

    def extractInfo(self, otherInfoObject):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = info1 * 2.5
        >>> info3 = _TestInfoObject()
        >>> info2.extractInfo(info3)
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     if value is None:
        ...         continue
        ...     written[attr] = getattr(info2, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [int(round(v * 2.5)) for v in value]
        ...     elif isinstance(value, int):
        ...         expectedValue = int(round(value * 2.5))
        ...     else:
        ...         expectedValue = value * 2.5
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        for attr, (formatter, factorIndex) in _infoAttrs.items():
            if hasattr(self, attr):
                v = getattr(self, attr)
                if v is not None:
                    if formatter is not None:
                        v = formatter(v)
                setattr(otherInfoObject, attr, v)
        if hasattr(self, "postscriptWeightName"):
            otherInfoObject.postscriptWeightName = self.postscriptWeightName


# ----------
# Formatters
# ----------

def _numberFormatter(value):
    v = int(value)
    if v == value:
        return v
    return value

def _integerFormatter(value):
    return int(round(value))

def _floatFormatter(value):
    return float(value)

def _nonNegativeNumberFormatter(value):
    """
    >>> _nonNegativeNumberFormatter(-10)
    0
    """
    if value < 0:
        return 0
    return value

def _nonNegativeIntegerFormatter(value):
    value = _integerFormatter(value)
    if value < 0:
        return 0
    return value

def _integerListFormatter(value):
    """
    >>> _integerListFormatter([.9, 40.3, 16.0001])
    [1, 40, 16]
    """
    return [_integerFormatter(v) for v in value]

def _numberListFormatter(value):
    return [_numberFormatter(v) for v in value]

def _openTypeOS2WidthClassFormatter(value):
    """
    >>> _openTypeOS2WidthClassFormatter(-2)
    1
    >>> _openTypeOS2WidthClassFormatter(0)
    1
    >>> _openTypeOS2WidthClassFormatter(5.4)
    5
    >>> _openTypeOS2WidthClassFormatter(9.6)
    9
    >>> _openTypeOS2WidthClassFormatter(12)
    9
    """
    value = int(round(value))
    if value > 9:
        value = 9
    elif value < 1:
        value = 1
    return value

def _openTypeOS2WeightClassFormatter(value):
    """
    >>> _openTypeOS2WeightClassFormatter(-20)
    0
    >>> _openTypeOS2WeightClassFormatter(0)
    0
    >>> _openTypeOS2WeightClassFormatter(50.4)
    50
    >>> _openTypeOS2WeightClassFormatter(90.6)
    91
    >>> _openTypeOS2WeightClassFormatter(120)
    120
    """
    value = int(round(value))
    if value < 0:
        value = 0
    return value

_infoAttrs = dict(
    # these are structured as:
    #   attribute name = (formatter function, factor direction)
    # where factor direction 0 = x, 1 = y and 3 = x, y (for angles)

    unitsPerEm=(_nonNegativeNumberFormatter, 1),
    descender=(_numberFormatter, 1),
    xHeight=(_numberFormatter, 1),
    capHeight=(_numberFormatter, 1),
    ascender=(_numberFormatter, 1),
    italicAngle=(_numberFormatter, 3),

    openTypeHeadLowestRecPPEM=(_nonNegativeIntegerFormatter, 1),

    openTypeHheaAscender=(_integerFormatter, 1),
    openTypeHheaDescender=(_integerFormatter, 1),
    openTypeHheaLineGap=(_integerFormatter, 1),
    openTypeHheaCaretSlopeRise=(_integerFormatter, 1),
    openTypeHheaCaretSlopeRun=(_integerFormatter, 1),
    openTypeHheaCaretOffset=(_integerFormatter, 1),

    openTypeOS2WidthClass=(_openTypeOS2WidthClassFormatter, 0),
    openTypeOS2WeightClass=(_openTypeOS2WeightClassFormatter, 0),
    openTypeOS2TypoAscender=(_integerFormatter, 1),
    openTypeOS2TypoDescender=(_integerFormatter, 1),
    openTypeOS2TypoLineGap=(_integerFormatter, 1),
    openTypeOS2WinAscent=(_nonNegativeIntegerFormatter, 1),
    openTypeOS2WinDescent=(_nonNegativeIntegerFormatter, 1),
    openTypeOS2SubscriptXSize=(_integerFormatter, 0),
    openTypeOS2SubscriptYSize=(_integerFormatter, 1),
    openTypeOS2SubscriptXOffset=(_integerFormatter, 0),
    openTypeOS2SubscriptYOffset=(_integerFormatter, 1),
    openTypeOS2SuperscriptXSize=(_integerFormatter, 0),
    openTypeOS2SuperscriptYSize=(_integerFormatter, 1),
    openTypeOS2SuperscriptXOffset=(_integerFormatter, 0),
    openTypeOS2SuperscriptYOffset=(_integerFormatter, 1),
    openTypeOS2StrikeoutSize=(_integerFormatter, 1),
    openTypeOS2StrikeoutPosition=(_integerFormatter, 1),

    openTypeVheaVertTypoAscender=(_integerFormatter, 1),
    openTypeVheaVertTypoDescender=(_integerFormatter, 1),
    openTypeVheaVertTypoLineGap=(_integerFormatter, 1),
    openTypeVheaCaretSlopeRise=(_integerFormatter, 1),
    openTypeVheaCaretSlopeRun=(_integerFormatter, 1),
    openTypeVheaCaretOffset=(_integerFormatter, 1),

    postscriptSlantAngle=(_numberFormatter, 3),
    postscriptUnderlineThickness=(_numberFormatter, 1),
    postscriptUnderlinePosition=(_numberFormatter, 1),
    postscriptBlueValues=(_numberListFormatter, 1),
    postscriptOtherBlues=(_numberListFormatter, 1),
    postscriptFamilyBlues=(_numberListFormatter, 1),
    postscriptFamilyOtherBlues=(_numberListFormatter, 1),
    postscriptStemSnapH=(_numberListFormatter, 0),
    postscriptStemSnapV=(_numberListFormatter, 1),
    postscriptBlueFuzz=(_numberFormatter, 1),
    postscriptBlueShift=(_numberFormatter, 1),
    postscriptBlueScale=(_floatFormatter, 1),
    postscriptDefaultWidthX=(_numberFormatter, 0),
    postscriptNominalWidthX=(_numberFormatter, 0),
    # this will be handled in a special way
    # postscriptWeightName=unicode
)

_postscriptWeightNameOptions = {
    100 : "Thin",
    200 : "Extra-light",
    300 : "Light",
    400 : "Normal",
    500 : "Medium",
    600 : "Semi-bold",
    700 : "Bold",
    800 : "Extra-bold",
    900 : "Black"
}

# ----
# Test
# ----

_testData = dict(
    # generic
    unitsPerEm=1000,
    descender=-200,
    xHeight=400,
    capHeight=650,
    ascender=700,
    italicAngle=0,
    # head
    openTypeHeadLowestRecPPEM=5,
    # hhea
    openTypeHheaAscender=700,
    openTypeHheaDescender=-200,
    openTypeHheaLineGap=200,
    openTypeHheaCaretSlopeRise=1,
    openTypeHheaCaretSlopeRun=1,
    openTypeHheaCaretOffset=1,
    # OS/2
    openTypeOS2WidthClass=5,
    openTypeOS2WeightClass=500,
    openTypeOS2TypoAscender=700,
    openTypeOS2TypoDescender=-200,
    openTypeOS2TypoLineGap=200,
    openTypeOS2WinAscent=700,
    openTypeOS2WinDescent=-200,
    openTypeOS2SubscriptXSize=300,
    openTypeOS2SubscriptYSize=300,
    openTypeOS2SubscriptXOffset=0,
    openTypeOS2SubscriptYOffset=-200,
    openTypeOS2SuperscriptXSize=300,
    openTypeOS2SuperscriptYSize=300,
    openTypeOS2SuperscriptXOffset=0,
    openTypeOS2SuperscriptYOffset=500,
    openTypeOS2StrikeoutSize=50,
    openTypeOS2StrikeoutPosition=300,
    # Vhea
    openTypeVheaVertTypoAscender=700,
    openTypeVheaVertTypoDescender=-200,
    openTypeVheaVertTypoLineGap=200,
    openTypeVheaCaretSlopeRise=1,
    openTypeVheaCaretSlopeRun=1,
    openTypeVheaCaretOffset=1,
    # postscript
    postscriptSlantAngle=0,
    postscriptUnderlineThickness=100,
    postscriptUnderlinePosition=-150,
    postscriptBlueValues=[-10, 0, 400, 410, 650, 660, 700, 710],
    postscriptOtherBlues=[-210, -200],
    postscriptFamilyBlues=[-10, 0, 400, 410, 650, 660, 700, 710],
    postscriptFamilyOtherBlues=[-210, -200],
    postscriptStemSnapH=[80, 90],
    postscriptStemSnapV=[110, 130],
    postscriptBlueFuzz=1,
    postscriptBlueShift=7,
    postscriptBlueScale=0.039625,
    postscriptDefaultWidthX=400,
    postscriptNominalWidthX=400,
    # guidelines
    guidelines=None
)

_testDataSubset = dict(
    # generic
    unitsPerEm=1000,
    descender=-200,
    xHeight=None,
    # postscript
    postscriptBlueValues=[-10, 0, 400, 410, 650],
    # guidelines
    guidelines=[{'y': 100, 'x': None, 'angle': None, 'name': 'bar', 'identifier': '2'}]
)

class _TestInfoObject(object):

    def __init__(self, data=_testData):
        for attr, value in data.items():
            setattr(self, attr, value)


if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
