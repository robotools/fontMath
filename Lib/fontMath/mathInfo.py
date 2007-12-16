from mathFunctions import add, sub, mul, div

_infoAttrs = [
        'unitsPerEm',
        'ascender',
        'descender',
        'capHeight',
        'xHeight',
        'defaultWidth',
        'italicAngle',
        'slantAngle',
        'weightValue'
        ]


class MathInfo(object):

    def __init__(self, infoObject):
        for attr in _infoAttrs:
            if hasattr(infoObject, attr):
                setattr(self, attr, getattr(infoObject, attr))

    def _processMathOne(self, copiedInfo, otherInfo, funct):
        # used by: __add__, __sub__
        for attr in _infoAttrs:
            a = None
            b = None
            v = None
            if hasattr(copiedInfo, attr):
                a = getattr(copiedInfo, attr)
            if hasattr(otherInfo, attr):
                b = getattr(otherInfo, attr)
            if a is not None and b is not None:
                v = funct(a, b)
            elif a is not None and b is None:
                v = a
            elif b is not None and a is None:
                v = b
            if v is not None:
                setattr(copiedInfo, attr, v)

    def _processMathTwo(self, copiedInfo, factor, funct):
        # used by: __mul__, __div__
        for attr in _infoAttrs:
            if hasattr(copiedInfo, attr):
                v = getattr(copiedInfo, attr)
                if v is not None and factor is not None:
                    v = funct(v, factor)
                else:
                    v = None
                setattr(copiedInfo, attr, v)

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
        self._processMathTwo(copiedInfo, factor, mul)
        return copiedInfo

    __rdiv__ = __div__

    def extractInfo(self, otherInfoObject):
        for attr in _infoAttrs:
            if hasattr(self, attr):
                v = getattr(self, attr)
                setattr(otherInfoObject, attr, v)

