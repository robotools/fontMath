
from __future__ import division, absolute_import
from fontMath.mathFunctions import (
    add, addPt, div, factorAngle, mul, _roundNumber, sub, subPt, round2)


"""
    An object that behaves like an (ordered) dictionary
    as well as a math object.

    Notes
    No anisotropic support for the factors, because we do not 
    know the geometric nature of the values.

    MathDict will try to apply mul, div, add and sub to the dict's values.
    Numbers or other math objects will work
    Nested lists of numbers will work

"""


class MathDict(dict):

    def _processMathOneNumber(self, a, b, func):
        print('_processMathOneNumber', type(a), type(b))
        return func(a, b)

    def _processMathOneNumberList(self, a, b, func):
        if len(a) != len(b):
            return None
        v = []
        for index, aItem in enumerate(a):
            bItem = b[index]
            v.append(func(aItem, bItem))
        return v

    def _processMathOneNumberDict(self, a, b, func):
        if len(a) != len(b):
            return None
        v = MathDict()  # assumption, but might as well
        for key, aItem in a.items():
            bItem = b[key]
            v[key] = func(aItem, bItem)
        return v

    def _processMathTwoNumber(self, v, factor, func):
        print('_processMathTwoNumber', type(v))
        return func(v, factor)

    def _processMathTwoNumberList(self, v, factor, func):
        # but this will maintain tuple / list structuring in the result
        result = []
        for item in v:
            if isinstance(item, (list, tuple)):
                itemResult = self._processMathTwoNumberList(item, factor, func)
                if isinstance(item, (tuple)):
                    result.append(tuple(itemResult))
                else:
                    result.append(itemResult)
            else:
                #print('_processMathTwoNumberList', type(item))
                result.append(func(item, factor))
        if isinstance(v, tuple):
            return tuple(result)
        return result

    def _processMathTwoNumberDict(self, v, factor, func):
        result = {}
        for key, item in v.items():
            if isinstance(item, (list, tuple)):
                #print('_processMathTwoNumberDict', type(item))
                itemResult = self._processMathTwoNumberList(item, factor, func)
                if isinstance(item, (tuple)):
                    result[key] = tuple(itemResult)
                else:
                    result[key] = itemResult
            elif isinstance(item, dict):
                itemResult = self._processMathTwoNumberDict(item, factor, func)
                #print('_processMathTwoNumberDict', type(item))
                result[key] = itemResult
            else:
                #print('_processMathTwoNumberDict', type(item))
                result[key] = func(item, factor)
        return result

    def _processMathOne(self, copiedMathDict, otherMathDict, ptFunc, func):
        for k in copiedMathDict.keys():
            a = copiedMathDict.get(k)
            b = otherMathDict.get(k)
            if a is not None and b is not None:
                if isinstance(a, (list, tuple)):
                    v = self._processMathOneNumberList(a, b, func)
                elif isinstance(a, dict):
                    v = self._processMathOneNumberDict(a, b, func)
                else:
                    v = self._processMathOneNumber(a, b, func)
                copiedMathDict[k] = v

    def _processMathTwo(self, copiedMathDict, factor, func):
        for k in copiedMathDict.keys():
            v = copiedMathDict.get(k)
            if v is not None and factor is not None:
                if isinstance(v, (list, tuple)):
                    v = self._processMathTwoNumberList(v, factor, func)
                elif isinstance(v, dict):
                    v = self._processMathTwoNumberDict(v, factor, func)
                else:
                    v = self._processMathTwoNumber(v, factor, func)
                copiedMathDict[k] = v

    def copy(self):
        copied = MathDict(self)
        return copied

    def __add__(self, otherMathDict):
        #assert self.keys() == otherMathDict.keys()
        copiedDict = self.copy()
        self._processMathOne(copiedDict, otherMathDict, addPt, add)
        return copiedDict

    def __sub__(self, otherMathDict):
        #assert self.keys() == otherMathDict.keys()
        copiedDict = self.copy()
        self._processMathOne(copiedDict, otherMathDict, subPt, sub)
        return copiedDict

    # math with factor
    # No anisotropic processing for the factor?
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
    md = MathDict(a=1, b=2, c=3)
    assert list(md.keys()) == ['a', 'b', 'c']  # keys are odict_keys(['a', 'b', 'c'])
    assert list(md.values()) == [1, 2, 3]  # values are odict_values([1, 2, 3])

    # make sure the copy has the same content
    md2 = md.copy()
    assert md == md2
    # check if the copy has the same key order
    assert list(md.keys()) == list(md2.keys())

    # make sure the copy was not shallow
    # by changing a value in the original
    # and comparing it to the copy.
    md['a'] = 100
    assert md2['a'] != md['a']

    # make sure the new object has the same keys
    md3 = md + md2
    #print('md3', md3)
    assert md3.keys()==md.keys()
    #print('md3-md', md3-md)
    assert (md3-md) == {'a': 1, 'b': 2, 'c': 3}

    # addition
    md4 = MathDict(a=-100, b=-200, c=-300)
    #print('md4', md4)
    assert (md+md4) == {'a': 0, 'b': -198, 'c': -297}
    # subtraction
    assert (md-md4) == {'a': 200, 'b': 202, 'c': 303}
    assert md.keys() == md4.keys()

    # multiplication
    md5 = md * 2
    #print('md5', md5)
    assert md5 == {'a': 200, 'b': 4, 'c': 6}
    assert md.keys() == md5.keys()

    # division
    md6 = md / 100
    #print('md6', md6)
    assert md6 == {'a': 1.0, 'b': 0.02, 'c': 0.03}
    assert md.keys() == md6.keys()

    # check zero division
    triedZeroDivision = False
    try:
        md7 = md / 0
    except ZeroDivisionError:
        triedZeroDivision = True
    assert triedZeroDivision == True

    # let's check some expectations
    # check nested lists and tuples
    md8 = MathDict(a=1, b=2, c=[1, 2, 3, [4, 5, [6, 7, 8, (9, 10)]]])
    assert md8 * 2 == {'a': 2, 'b': 4, 'c': [2, 4, 6, [8, 10, [12, 14, 16, (18, 20)]]]}
    assert md8 / 2 == {'a': 0.5, 'b': 1.0, 'c': [0.5, 1.0, 1.5, [2.0, 2.5, [3.0, 3.5, 4.0, (4.5, 5.0)]]]}

    # check structure
    md10 = MathDict(a=(1, 2), b=[3, 4])
    assert md10*2 == {'a': (2, 4), 'b': [6, 8]}
    # check the order of the keys is kept
    assert (md10*2).keys() == md10.keys()

    # check nested dicts
    md11 = MathDict(a=MathDict(nest1=100), b=MathDict(nest2=200))
    assert md11*2 == {'a': {'nest1': 200}, 'b': {'nest2': 400}}
    assert (md11+md11) == {'a': {'nest1': 200}, 'b': {'nest2': 400}}

    # not sure if this is the bhaviour we want for strings.
    md12 = MathDict(a=MathDict(nest1=100), b=MathDict(nest2="aa"))
    assert (md12+md12) == {'a': {'nest1': 200}, 'b': {'nest2': 'aaaa'}}

    md13 = MathDict(a=MathDict(nest1=100), b=MathDict(nest2=MathDict(c=100)))
    assert md13*2 == {'a':{'nest1': 200}, 'b': {'nest2': {'c': 200}}}
    assert (md13+md13) == {'a':{'nest1': 200}, 'b': {'nest2': {'c': 200}}}
    assert (md13+md13)/2 == md13
    assert (md13+md13)*.5 == md13

    # anisotropic
    md14 = MathDict(a=1, b=[3, 4])
    print(md14 * (1, 2))
