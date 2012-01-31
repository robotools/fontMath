from mathFunctions import add, sub, mul, div

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
    if value < 0:
        return 0
    return value

def _integerListFormatter(value):
    return [_integerFormatter(v) for v in value]

def _numberListFormatter(value):
    return [_numberFormatter(v) for v in value]

def _openTypeOS2WidthClassFormatter(value):
    value = int(round(value))
    if value > 9:
        value = 9
    elif value < 1:
        value = 1
    return value

def _openTypeOS2WeightClassFormatter(value):
    value = int(round(value))
    if value < 0:
        value = 0
    return value

_infoAttrs = dict(
    unitsPerEm=_nonNegativeNumberFormatter,
    descender=_numberFormatter,
    xHeight=_numberFormatter,
    capHeight=_numberFormatter,
    ascender=_numberFormatter,
    italicAngle=_numberFormatter,

    openTypeHeadLowestRecPPEM=_nonNegativeNumberFormatter,

    openTypeHheaAscender=_numberFormatter,
    openTypeHheaDescender=_numberFormatter,
    openTypeHheaLineGap=_numberFormatter,
    openTypeHheaCaretSlopeRise=_integerFormatter,
    openTypeHheaCaretSlopeRun=_integerFormatter,
    openTypeHheaCaretOffset=_numberFormatter,

    openTypeOS2WidthClass=_openTypeOS2WidthClassFormatter,
    openTypeOS2WeightClass=_openTypeOS2WeightClassFormatter,
    openTypeOS2TypoAscender=_numberFormatter,
    openTypeOS2TypoDescender=_numberFormatter,
    openTypeOS2TypoLineGap=_numberFormatter,
    openTypeOS2WinAscent=_nonNegativeNumberFormatter,
    openTypeOS2WinDescent=_nonNegativeNumberFormatter,
    openTypeOS2SubscriptXSize=_numberFormatter,
    openTypeOS2SubscriptYSize=_numberFormatter,
    openTypeOS2SubscriptXOffset=_numberFormatter,
    openTypeOS2SubscriptYOffset=_numberFormatter,
    openTypeOS2SuperscriptXSize=_numberFormatter,
    openTypeOS2SuperscriptYSize=_numberFormatter,
    openTypeOS2SuperscriptXOffset=_numberFormatter,
    openTypeOS2SuperscriptYOffset=_numberFormatter,
    openTypeOS2StrikeoutSize=_numberFormatter,
    openTypeOS2StrikeoutPosition=_numberFormatter,

    openTypeVheaVertTypoAscender=_numberFormatter,
    openTypeVheaVertTypoDescender=_numberFormatter,
    openTypeVheaVertTypoLineGap=_numberFormatter,
    openTypeVheaCaretSlopeRise=_integerFormatter,
    openTypeVheaCaretSlopeRun=_integerFormatter,
    openTypeVheaCaretOffset=_numberFormatter,

    postscriptSlantAngle=_numberFormatter,
    postscriptUnderlineThickness=_numberFormatter,
    postscriptUnderlinePosition=_numberFormatter,
    postscriptBlueValues=_numberListFormatter,
    postscriptOtherBlues=_numberListFormatter,
    postscriptFamilyBlues=_numberListFormatter,
    postscriptFamilyOtherBlues=_numberListFormatter,
    postscriptStemSnapH=_numberListFormatter,
    postscriptStemSnapV=_numberListFormatter,
    postscriptBlueFuzz=_numberFormatter,
    postscriptBlueShift=_numberFormatter,
    postscriptBlueScale=_floatFormatter,
    postscriptDefaultWidthX=_numberFormatter,
    postscriptNominalWidthX=_numberFormatter,
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

# ------
# Object
# ------

class MathInfo(object):

    def __init__(self, infoObject):
        for attr in _infoAttrs.keys():
            if hasattr(infoObject, attr):
                setattr(self, attr, getattr(infoObject, attr))

    def _processMathOne(self, copiedInfo, otherInfo, funct):
        # used by: __add__, __sub__
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
                    v = self._processMathOneNumberList(a, b, funct)
                else:
                    v = self._processMathOneNumber(a, b, funct)
            elif a is not None and b is None:
                v = a
            elif b is not None and a is None:
                v = b
            if v is not None:
                setattr(copiedInfo, attr, v)
        self._processPostscriptWeightName(copiedInfo)

    def _processMathTwo(self, copiedInfo, factor, funct):
        # used by: __mul__, __div__
        for attr in _infoAttrs.keys():
            if hasattr(copiedInfo, attr):
                v = getattr(copiedInfo, attr)
                if v is not None and factor is not None:
                    if isinstance(v, (list, tuple)):
                        v = self._processMathTwoNumberList(v, factor, funct)
                    else:
                        v = self._processMathTwoNumber(v, factor, funct)
                else:
                    v = None
                setattr(copiedInfo, attr, v)
        self._processPostscriptWeightName(copiedInfo)

    def _processMathOneNumber(self, a, b, funct):
        return funct(a, b)

    def _processMathTwoNumber(self, v, factor, funct):
        return funct(v, factor)

    def _processMathOneNumberList(self, a, b, funct):
        if len(a) != len(b):
            return None
        v = []
        for index, aItem in enumerate(a):
            bItem = b[index]
            v.append(funct(aItem, bItem))
        return v

    def _processMathTwoNumberList(self, v, factor, funct):
        return [funct(i, factor) for i in v]

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
            v = int(round(v * .01) * 100)
            if v < 100:
                v = 100
            elif v > 900:
                v = 900
            name = _postscriptWeightNameOptions[v]
        copiedInfo.postscriptWeightName = name

    def copy(self):
        copied = MathInfo(self)
        return copied

    def __add__(self, otherInfo):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = MathInfo(_TestInfoObject())
        >>> info3 = info1 + info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
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
        self._processMathOne(copiedInfo, otherInfo, add)
        return copiedInfo

    def __sub__(self, otherInfo):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = MathInfo(_TestInfoObject())
        >>> info3 = info1 - info2
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
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
        self._processMathOne(copiedInfo, otherInfo, sub)
        return copiedInfo

    def __mul__(self, factor):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = info1 * 2.5
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
        ...     written[attr] = getattr(info2, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v * 2.5 for v in value]
        ...     else:
        ...         expectedValue = value * 2.5
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        if isinstance(factor, tuple):
            factor = factor[0]
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
        ...     written[attr] = getattr(info2, attr)
        ...     if isinstance(value, list):
        ...         expectedValue = [v / 2 for v in value]
        ...     else:
        ...         expectedValue = value / 2
        ...     expected[attr] = expectedValue
        >>> sorted(expected) == sorted(written)
        True
        """
        if isinstance(factor, tuple):
            factor = factor[0]
        copiedInfo = self.copy()
        self._processMathTwo(copiedInfo, factor, div)
        return copiedInfo

    __rdiv__ = __div__

    def extractInfo(self, otherInfoObject):
        """
        >>> info1 = MathInfo(_TestInfoObject())
        >>> info2 = info1 * 2.5
        >>> info3 = _TestInfoObject()
        >>> info2.extractInfo(info3)
        >>> written = {}
        >>> expected = {}
        >>> for attr, value in _testData.items():
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
        for attr, formatter in _infoAttrs.items() + [("postscriptWeightName", None)]:
            if hasattr(self, attr):
                v = getattr(self, attr)
                if v is not None:
                    if formatter is not None:
                        v = formatter(v)
                setattr(otherInfoObject, attr, v)


# ------------
# Test Support
# ------------

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
    postscriptNominalWidthX=400
)

class _TestInfoObject(object):

    def __init__(self):
        for attr, value in _testData.items():
            setattr(self, attr, value)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
