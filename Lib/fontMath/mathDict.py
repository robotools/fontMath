
from __future__ import division, absolute_import
from collections import OrderedDict
from fontMath.mathFunctions import (
    add, addPt, div, factorAngle, mul, _roundNumber, sub, subPt, round2)


"""
    An object that behaves like an ordered dictionary
    as well as a math object.

    Notes
    No anisotropic support for the factors, because we do not 
    know the geometric nature of the values.

    Do we need a separate MathDict and MathOrderedDict?
    OrderedDict is implemented in C and should perform
    just like dict. (Untested assumption, fine for now.)
    https://github.com/python/cpython/issues/61195

"""

class MathDict(OrderedDict):

    # mathInfo
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

    def _processMathTwoNumber(self, v, factor, func):
        return func(v, factor)

    def _processMathTwoNumberList(self, v, factor, func):
        return [func(i, factor) for i in v]

    def _processMathOne(self, copiedMathDict, otherMathDict, ptFunc, func):
        for k in copiedMathDict.keys():
            a = copiedMathDict.get(k)
            b = otherMathDict.get(k)
            if a is not None and b is not None:
                if isinstance(a, (list, tuple)):
                    v = self._processMathOneNumberList(a, b, func)
                else:
                    v = self._processMathOneNumber(a, b, func)
                copiedMathDict[k] = v

    def _processMathTwo(self, copiedMathDict, factor, func):
        for k in copiedMathDict.keys():
            v = copiedMathDict.get(k)
            if v is not None and factor is not None:
                if isinstance(v, (list, tuple)):
                    print("_processMathTwo", k, v, factor)
                    v = self._processMathTwoNumberList(v, factor, func)
                else:
                    v = self._processMathTwoNumber(v, factor, func)
                copiedMathDict[k] = v

    def copy(self):
        copied = MathDict(self)
        return copied

    def __add__(self, otherMathDict):
        assert self.keys() == otherMathDict.keys()
        copiedDict = self.copy()
        self._processMathOne(copiedDict, otherMathDict, addPt, add)
        return copiedDict

    def __sub__(self, otherMathDict):
        assert self.keys() == otherMathDict.keys()
        copiedDict = self.copy()
        self._processMathOne(copiedDict, otherMathDict, subPt, sub)
        return copiedDict

    # math with factor
    # No anisotropic processing for the factor.
    # because we don't actually know if the values in MathDict
    # represent any x y geometry.
    def __mul__(self, factor):
        copiedDict = self.copy()
        self._processMathTwo(copiedDict, factor, mul)
        return copiedDict

    __rmul__ = __mul__

    def __div__(self, factor):
        if factor == 0:
            raise ZeroDivisionError
        copiedDict = self.copy()
        self._processMathTwo(copiedDict, factor, div)
        return copiedDict

    __truediv__ = __div__

    __rdiv__ = __div__

    __rtruediv__ = __rdiv__


if __name__ == "__main__":
    omd = MathDict(a=1, b=2, c=3)
    assert list(omd.keys()) == ['a', 'b', 'c']  # keys are odict_keys(['a', 'b', 'c'])
    assert list(omd.values()) == [1, 2, 3]  # values are odict_values([1, 2, 3])

    # make sure the copy has the same content
    omd2 = omd.copy()
    #print('omd2', omd2)
    assert omd == omd2

    # make sure the copy was not shallow
    # by changing a value in the original
    # and comparing it to the copy.
    omd['a'] = 100
    assert omd2['a'] != omd['a']

    # make sure the new object has the same keys
    omd3 = omd + omd2
    #print('omd3', omd3)
    assert omd3.keys()==omd.keys()
    assert (omd3-omd) == MathDict([('a', 1), ('b', 2), ('c', 3)])

    # addition
    omd4 = MathDict(a=-100, b=-200, c=-300)
    #print('omd4', omd4)
    #print('omd+omd4', omd+omd4)
    assert (omd+omd4) == MathDict([('a', 0), ('b', -198), ('c', -297)])
    # subtraction
    assert (omd-omd4) == MathDict([('a', 200), ('b', 202), ('c', 303)])
    assert omd.keys() == omd4.keys()

    # multiplication
    omd5 = omd * 2
    #print('omd5', omd5)
    assert omd5 == MathDict([('a', 200), ('b', 4), ('c', 6)])
    assert omd.keys() == omd5.keys()

    # division
    omd6 = omd / 100
    #print('omd6', omd6)
    assert omd6 == MathDict([('a', 1.0), ('b', 0.02), ('c', 0.03)])
    assert omd.keys() == omd6.keys()

    try:
        omd7 = omd / 0
    except ZeroDivisionError:
        # yes
        #print('omd7 zero division error caught')
        pass

