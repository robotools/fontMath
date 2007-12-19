"""
An object that serves kerning data from a
class kerning dictionary.

It scans a group dictionary and stores
a mapping of glyph to group relationships.
this map is then used to lookup kerning values.

It is important to note that all groups names
used in class kerning pairs must have the
standard kerning class prefix (@) at the begining
of the group name.
"""

from copy import deepcopy
from mathFunctions import add, sub, mul, div


KERNING_CLASS_PREFIX = '@'


class MathKerning(object):

    def __init__(self, kerning={}, groups={}):
        self.update(kerning)
        self.updateGroups(groups)

    def update(self, kerning):
        from robofab.objects.objectsBase import BaseKerning
        if isinstance(kerning, BaseKerning):
            kerning = kerning.asDict()
        else:
            kerning = deepcopy(kerning)
        self._kerning = kerning

    def updateGroups(self, groups):
        self._groupMap = {}
        #
        groupDict = groups
        groupMap = self._groupMap
        #
        for groupName, glyphList in groupDict.items():
            if not groupName.startswith(KERNING_CLASS_PREFIX):
                continue
            for glyphName in glyphList:
                if not groupMap.has_key(glyphName):
                    groupMap[glyphName] = []
                if groupName not in groupMap[glyphName]:
                    groupMap[glyphName].append(groupName)

    def keys(self):
        return self._kerning.keys()

    def values(self):
        return self._kerning.values()

    def items(self):
        return self._kerning.items()

    def groups(self):
        g = {}
        for glyphName, groupList in self._groupMap.items():
            for groupName in groupList:
                if not g.has_key(groupName):
                    g[groupName] = []
                if not glyphName in g[groupName]:
                    g[groupName].append(glyphName)
        return g

    def __getitem__(self, pair):
        """
        >>> kerning = {
        ...     ("@A_left", "@A_right") : 1,
        ...     ("A1", "@A_right") : 2,
        ...     ("@A_left", "A2") : 3,
        ...     ("A3", "A3") : 4,
        ... }
        >>> groups = {
        ... "@A_left" : ["A", "A1", "A2", "A3"],
        ... "@A_right" : ["A", "A1", "A2", "A3"],
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj["A", "A"]
        1
        >>> obj["A1", "A"]
        2
        >>> obj["A", "A2"]
        3
        >>> obj["A3", "A3"]
        4
        >>> obj["X", "X"]
        0
        """
        if self._kerning.has_key(pair):
            return self._kerning[pair]
        #
        left, right = pair
        #
        potentialLeft = [left]
        potentialLeft.extend(self._groupMap.get(left, []))
        potentialRight = [right]
        potentialRight.extend(self._groupMap.get(right, []))
        #
        notClassed = []
        halfClassed = []
        fullClassed = []
        for l in potentialLeft:
            for r in potentialRight:
                if self._kerning.has_key((l, r)):
                    v = self._kerning[l, r]
                    if l[0] == KERNING_CLASS_PREFIX and r[0] == KERNING_CLASS_PREFIX:
                        fullClassed.append((l, r, v))
                    elif l[0] == KERNING_CLASS_PREFIX and r[0] != KERNING_CLASS_PREFIX:
                        halfClassed.append((l, r, v))
                    elif l[0] != KERNING_CLASS_PREFIX and r[0] == KERNING_CLASS_PREFIX:
                        halfClassed.append((l, r, v))
                    else:
                        notClassed.append((l, r, v))
        if len(notClassed) != 0:
            return notClassed[0][2]
        elif len(halfClassed) != 0:
            halfClassed.sort()
            return halfClassed[0][2]
        elif len(fullClassed) != 0:
            fullClassed.sort()
            return fullClassed[0][2]
        # hm, maybe this should raise a key error
        # instead of returning 0...
        return 0

    def guessPairType(self, pair):
        """
        >>> kerning = {
        ...     ("@A_left", "@A_right") : 1,
        ...     ("A1", "@A_right") : 2,
        ...     ("@A_left", "A2") : 3,
        ...     ("A3", "A3") : 4,
        ... }
        >>> groups = {
        ... "@A_left" : ["A", "A1", "A2", "A3"],
        ... "@A_right" : ["A", "A1", "A2", "A3"],
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj.guessPairType(("@A_left", "@A_right"))
        ('class', 'class')
        >>> obj.guessPairType(("A1", "@A_right"))
        ('exception', 'class')
        >>> obj.guessPairType(("@A_left", "A2"))
        ('class', 'exception')
        >>> obj.guessPairType(("A3", "A3"))
        ('exception', 'exception')
        >>> obj.guessPairType(("A", "A"))
        ('single', 'single')
        """
        left, right = pair
        CLASS_TYPE = "class"
        SINGLE_TYPE = "single"
        EXCEPTION_TYPE = "exception"
        #
        leftType = SINGLE_TYPE
        rightType = SINGLE_TYPE
        # is the left a simple class?
        if left[0] == KERNING_CLASS_PREFIX:
            leftType = CLASS_TYPE
        # or is it part of a class?
        if right[0] == KERNING_CLASS_PREFIX:
            rightType = CLASS_TYPE
        #
        if self._kerning.has_key(pair):
            potLeft = [left]
            potRight = [right]
            if leftType == SINGLE_TYPE and self._groupMap.has_key(left):
                    for groupName in self._groupMap[left]:
                        potLeft.append(groupName)
            if rightType == SINGLE_TYPE and self._groupMap.has_key(right):
                    for groupName in self._groupMap[right]:
                        potRight.append(groupName)
            #
            hits = []
            for left in potLeft:
                for right in potRight:
                    if self._kerning.has_key((left, right)):
                        hits.append((left, right))
            for left, right in hits:
                if leftType != CLASS_TYPE:
                    if left[0] == KERNING_CLASS_PREFIX:
                        leftType = EXCEPTION_TYPE
                if rightType != CLASS_TYPE:
                    if right[0] == KERNING_CLASS_PREFIX:
                        rightType = EXCEPTION_TYPE
        return (leftType, rightType)

    def get(self, pair, default=0):
        v = self[pair]
        if v == 0:
            v = default
        return v

    def copy(self):
        k = MathKerning(self._kerning)
        k._groupMap = deepcopy(self._groupMap)
        return k

    def _processMathOne(self, other, funct):
        from sets import Set
        comboPairs = Set(self._kerning.keys()) | Set(other._kerning.keys())
        kerning = dict.fromkeys(comboPairs, None)
        for k in comboPairs:
            v1 = self.get(k, 0)
            v2 = other.get(k, 0)
            v = funct(v1, v2)
            kerning[k] = v
        #
        g1 = self.groups()
        g2 = other.groups()
        if g1 == g2:
            groups = g1
        else:
            comboGroups = Set(g1.keys()) | Set(g2.keys())
            groups = dict.fromkeys(comboGroups, Set())
            for groupName in comboGroups:
                s1 = Set(g1.get(groupName, []))
                s2 = Set(g2.get(groupName, []))
                groups[groupName] = list(s1 | s2)
        #
        ks = MathKerning(kerning, groups)
        return ks

    def _processMathTwo(self, factor, funct):
        kerning = deepcopy(self._kerning)
        for k, v in self._kerning.items():
            v = funct(v, factor)
            kerning[k] = v
        ks = MathKerning(kerning)
        ks._groupMap = deepcopy(self._groupMap)
        return ks

    def __add__(self, other):
        """
        >>> kerning1 = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : 1,
        ...     ("NotIn2", "NotIn2") : 1,
        ...     ("@NotIn2", "C") : 1,
        ...     ("@D", "@D") : 1,
        ... }
        >>> groups1 = {
        ...     "@NotIn1" : ["C"],
        ...     "@D" : ["D", "H"],
        ... }
        >>> kerning2 = {
        ...     ("A", "A") : -1,
        ...     ("B", "B") : 1,
        ...     ("NotIn1", "NotIn1") : 1,
        ...     ("@NotIn1", "C") : 1,
        ...     ("@D", "@D") : 1,
        ... }
        >>> groups2 = {
        ...     "@NotIn2" : ["C"],
        ...     "@D" : ["D"],
        ... }
        >>> obj = MathKerning(kerning1, groups1) + MathKerning(kerning2, groups2)
        >>> sorted(obj.items())
        [(('@D', '@D'), 2), (('@NotIn1', 'C'), 1), (('@NotIn2', 'C'), 1), (('B', 'B'), 2), (('NotIn1', 'NotIn1'), 1), (('NotIn2', 'NotIn2'), 1)]
        >>> sorted(obj.groups()["@D"])
        ['D', 'H']
        """
        k = self._processMathOne(other, add)
        k.cleanup()
        return k

    def __sub__(self, other):
        """
        >>> kerning1 = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : 1,
        ...     ("NotIn2", "NotIn2") : 1,
        ...     ("@NotIn2", "C") : 1,
        ...     ("@D", "@D") : 1,
        ... }
        >>> groups1 = {
        ...     "@NotIn1" : ["C"],
        ...     "@D" : ["D", "H"],
        ... }
        >>> kerning2 = {
        ...     ("A", "A") : -1,
        ...     ("B", "B") : 1,
        ...     ("NotIn1", "NotIn1") : 1,
        ...     ("@NotIn1", "C") : 1,
        ...     ("@D", "@D") : 1,
        ... }
        >>> groups2 = {
        ...     "@NotIn2" : ["C"],
        ...     "@D" : ["D"],
        ... }
        >>> obj = MathKerning(kerning1, groups1) - MathKerning(kerning2, groups2)
        >>> sorted(obj.items())
        [(('@NotIn1', 'C'), -1), (('@NotIn2', 'C'), 1), (('A', 'A'), 2), (('NotIn1', 'NotIn1'), -1), (('NotIn2', 'NotIn2'), 1)]
        >>> sorted(obj.groups()["@D"])
        ['D', 'H']
        """
        k = self._processMathOne(other, sub)
        k.cleanup()
        return k

    def __mul__(self, value):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C2", "@C") : 0,
        ...     ("@C", "@C") : 2,
        ... }
        >>> groups = {
        ...     "@C" : ["C1", "C2"],
        ...     "@C" : ["C1", "C2"],
        ... }
        >>> obj = MathKerning(kerning, groups) * 2
        >>> sorted(obj.items())
        [(('@C', '@C'), 4), (('B', 'B'), 2), (('C2', '@C'), 0)]
        """
        k = self._processMathTwo(value, mul)
        k.cleanup()
        return k

    def __rmul__(self, value):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C2", "@C") : 0,
        ...     ("@C", "@C") : 2,
        ... }
        >>> groups = {
        ...     "@C" : ["C1", "C2"],
        ...     "@C" : ["C1", "C2"],
        ... }
        >>> obj = 2 * MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('@C', '@C'), 4), (('B', 'B'), 2), (('C2', '@C'), 0)]
        """
        k = self._processMathTwo(value, mul)
        k.cleanup()
        return k

    def __div__(self, value):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 4,
        ...     ("C2", "@C") : 0,
        ...     ("@C", "@C") : 4,
        ... }
        >>> groups = {
        ...     "@C" : ["C1", "C2"],
        ...     "@C" : ["C1", "C2"],
        ... }
        >>> obj = MathKerning(kerning, groups) / 2
        >>> sorted(obj.items())
        [(('@C', '@C'), 2), (('B', 'B'), 2), (('C2', '@C'), 0)]
        """
        k = self._processMathTwo(value, div)
        k.cleanup()
        return k

    def __rdiv__(self, value):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 4,
        ...     ("C2", "@C") : 0,
        ...     ("@C", "@C") : 4,
        ... }
        >>> groups = {
        ...     "@C" : ["C1", "C2"],
        ...     "@C" : ["C1", "C2"],
        ... }
        >>> obj = 2 / MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('@C', '@C'), 2), (('B', 'B'), 2), (('C2', '@C'), 0)]
        """
        k = self._processMathTwo(value, div)
        k.cleanup()
        return k

    def round(self, multiple=1):
        """
        >>> kerning = {
        ...     ("A", "A") : 2,
        ...     ("B", "B") : 4,
        ...     ("C", "C") : 7,
        ...     ("D", "D") : 9,
        ... }
        >>> obj = MathKerning(kerning)
        >>> obj.round(5)
        >>> sorted(obj.items())
        [(('A', 'A'), 0), (('B', 'B'), 5), (('C', 'C'), 5), (('D', 'D'), 10)]
        """
        multiple = float(multiple)
        for k, v in self._kerning.items():
            self._kerning[k] = int(round(int(round(v / multiple)) * multiple))

    def cleanup(self):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C", "@C") : 0,
        ...     ("@C", "@C") : 1,
        ...     ("D", "D") : 1.0,
        ...     ("E", "E") : 1.2,
        ... }
        >>> groups = {
        ...     "@C" : ["C", "C1"]
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj.cleanup()
        >>> sorted(obj.items())
        [(('@C', '@C'), 1), (('B', 'B'), 1), (('C', '@C'), 0), (('D', 'D'), 1), (('E', 'E'), 1.2)]
        """
        for (left, right), v in self._kerning.items():
            if int(v) == v:
                v = int(v)
                self._kerning[left, right] = v
            if v == 0:
                leftType, rightType = self.guessPairType((left, right))
                if leftType != "exception" and rightType != "exception":
                    del self._kerning[left, right]

    def addTo(self, value):
        """
        >>> kerning = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : -1,
        ... }
        >>> obj = MathKerning(kerning)
        >>> obj.addTo(1)
        >>> sorted(obj.items())
        [(('A', 'A'), 2), (('B', 'B'), 0)]
        """
        for k, v in self._kerning.items():
            self._kerning[k] = v + value

    def extractKerning(self, font):
        font.kerning.clear()
        font.kerning.update(self._kerning)
        font.groups.update(self.groups())


if __name__ == "__main__":
    import doctest
    doctest.testmod()
