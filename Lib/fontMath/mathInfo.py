from mathFunctions import add, sub, mul, div

_infoAttrs = dict(
    unitsPerEm=int,
    descender=int,
    xHeight=int,
    capHeight=int,
    ascender=int,
    italicAngle=float,
    openTypeHeadLowestRecPPEM=int,
    openTypeHheaAscender=int,
    openTypeHheaDescender=int,
    openTypeHheaLineGap=int,
    openTypeHheaCaretSlopeRise=int,
    openTypeHheaCaretSlopeRun=int,
    openTypeHheaCaretOffset=int,
    openTypeOS2WidthClass=int,
    openTypeOS2WeightClass=int,
    openTypeOS2Panose="intList",
    openTypeOS2FamilyClass="intList",
    openTypeOS2TypoAscender=int,
    openTypeOS2TypoDescender=int,
    openTypeOS2TypoLineGap=int,
    openTypeOS2WinAscent=int,
    openTypeOS2WinDescent=int,
    openTypeOS2SubscriptXSize=int,
    openTypeOS2SubscriptYSize=int,
    openTypeOS2SubscriptXOffset=int,
    openTypeOS2SubscriptYOffset=int,
    openTypeOS2SuperscriptXSize=int,
    openTypeOS2SuperscriptYSize=int,
    openTypeOS2SuperscriptXOffset=int,
    openTypeOS2SuperscriptYOffset=int,
    openTypeOS2StrikeoutSize=int,
    openTypeOS2StrikeoutPosition=int,
    openTypeVheaVertTypoAscender=int,
    openTypeVheaVertTypoDescender=int,
    openTypeVheaVertTypoLineGap=int,
    openTypeVheaCaretSlopeRise=int,
    openTypeVheaCaretSlopeRun=int,
    openTypeVheaCaretOffset=int,
    postscriptSlantAngle=float,
    postscriptUnderlineThickness=int,
    postscriptUnderlinePosition=int,
    postscriptBlueValues="intList",
    postscriptOtherBlues="intList",
    postscriptFamilyBlues="intList",
    postscriptFamilyOtherBlues="intList",
    postscriptStemSnapH="intList",
    postscriptStemSnapV="intList",
    postscriptBlueFuzz=int,
    postscriptBlueShift=int,
    postscriptBlueScale=float,
    postscriptDefaultWidthX=int,
    postscriptNominalWidthX=int,
    postscriptWeightName=unicode
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


class MathInfo(object):

    def __init__(self, infoObject):
        for attr in _infoAttrs.keys():
            if hasattr(infoObject, attr):
                setattr(self, attr, getattr(infoObject, attr))

    def _processMathOne(self, copiedInfo, otherInfo, funct):
        # used by: __add__, __sub__
        for attr, typ in _infoAttrs.items():
            # strings will be handled by special methods
            if typ == unicode:
                continue
            a = None
            b = None
            v = None
            if hasattr(copiedInfo, attr):
                a = getattr(copiedInfo, attr)
            if hasattr(otherInfo, attr):
                b = getattr(otherInfo, attr)
            if a is not None and b is not None:
                if typ == int:
                    v = self._processMathOneInt(a, b, funct)
                elif typ == float:
                    v = self._processMathOneFloat(a, b, funct)
                elif typ == "intList":
                    v = self._processMathOneIntList(a, b, funct)
            elif a is not None and b is None:
                v = a
            elif b is not None and a is None:
                v = b
            if v is not None:
                setattr(copiedInfo, attr, v)
        self._processPostscriptWeightName(copiedInfo)

    def _processMathTwo(self, copiedInfo, factor, funct):
        # used by: __mul__, __div__
        for attr, typ in _infoAttrs.items():
            # strings will be handled by special methods
            if typ == unicode:
                continue
            if hasattr(copiedInfo, attr):
                v = getattr(copiedInfo, attr)
                if v is not None and factor is not None:
                    if typ == int:
                        v = self._processMathTwoInt(v, factor, funct)
                    elif typ == float:
                        v = self._processMathTwoFloat(v, factor, funct)
                    elif typ == "intList":
                        v = self._processMathTwoIntList(v, factor, funct)
                else:
                    v = None
                setattr(copiedInfo, attr, v)
        self._processPostscriptWeightName(copiedInfo)

    def _processMathOneInt(self, a, b, funct):
        return funct(a, b)

    def _processMathTwoInt(self, v, factor, funct):
        return funct(v, factor)

    def _processMathOneFloat(self, a, b, funct):
        return funct(a, b)

    def _processMathTwoFloat(self, v, factor, funct):
        return funct(v, factor)

    def _processMathOneIntList(self, a, b, funct):
        if len(a) != len(b):
            return None
        v = []
        for index, aItem in enumerate(a):
            bItem = b[index]
            v.append(funct(aItem, bItem))
        return v

    def _processMathTwoIntList(self, v, factor, funct):
        return [funct(i, factor) for i in v]

    def _processPostscriptWeightName(self, copiedInfo):
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
        copiedInfo = self.copy()
        self._processMathOne(copiedInfo, otherInfo, add)
        return copiedInfo

    def __sub__(self, otherInfo):
        copiedInfo = self.copy()
        self._processMathOne(copiedInfo, otherInfo, sub)
        return copiedInfo

    def __mul__(self, factor):
        if isinstance(factor, tuple):
            factor = factor[0]
        copiedInfo = self.copy()
        self._processMathTwo(copiedInfo, factor, mul)
        return copiedInfo

    __rmul__ = __mul__

    def __div__(self, factor):
        if isinstance(factor, tuple):
            factor = factor[0]
        copiedInfo = self.copy()
        self._processMathTwo(copiedInfo, factor, div)
        return copiedInfo

    __rdiv__ = __div__

    def extractInfo(self, otherInfoObject):
        for attr, typ in _infoAttrs.items():
            if hasattr(self, attr):
                v = getattr(self, attr)
                if v is not None:
                    if typ == int:
                        v = int(v)
                    elif typ == float:
                        v = float(v)
                    elif typ == intList:
                        v = [int(i) for i in v]
                    elif typ == unicode:
                        # don't need to do any conversion
                        pass
                setattr(otherInfoObject, attr, v)


