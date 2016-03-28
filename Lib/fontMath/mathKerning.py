from __future__ import division, absolute_import
from copy import deepcopy
from ufoLib.validators import kerningValidatorReportPairs
from fontMath.mathFunctions import add, sub, mul, div

"""
An object that serves kerning data from a
class kerning dictionary.

It scans a group dictionary and stores
a mapping of glyph to group relationships.
this map is then used to lookup kerning values.
"""


side1Prefix = "public.kern1."
side2Prefix = "public.kern2."


class MathKerning(object):

    def __init__(self, kerning={}, groups={}):
        self.update(kerning)
        self.updateGroups(groups)

    # -------
    # Loading
    # -------

    def update(self, kerning):
        self._kerning = dict(kerning)

    def updateGroups(self, groups):
        self._groups = {}
        self._side1GroupMap = {}
        self._side2GroupMap = {}
        self._side1Groups = {}
        self._side2Groups = {}
        for groupName, glyphList in groups.items():
            if groupName.startswith(side1Prefix):
                self._groups[groupName] = list(glyphList)
                self._side1Groups[groupName] = glyphList
                for glyphName in glyphList:
                    self._side1GroupMap[glyphName] = groupName
            elif groupName.startswith(side2Prefix):
                self._groups[groupName] = list(glyphList)
                self._side2Groups[groupName] = glyphList
                for glyphName in glyphList:
                    self._side2GroupMap[glyphName] = groupName

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

    # -------------
    # dict Behavior
    # -------------

    def keys(self):
        return self._kerning.keys()

    def values(self):
        return self._kerning.values()

    def items(self):
        return self._kerning.items()

    def groups(self):
        return deepcopy(self._groups)

    def __contains__(self, pair):
        return pair in self._kerning

    def __getitem__(self, pair):
        """
        >>> kerning = {
        ...     ("public.kern1.A", "public.kern2.A") : 1,
        ...     ("A1", "public.kern2.A") : 2,
        ...     ("public.kern1.A", "A2") : 3,
        ...     ("A3", "A3") : 4,
        ... }
        >>> groups = {
        ... "public.kern1.A" : ["A", "A1", "A2", "A3"],
        ... "public.kern2.A" : ["A", "A1", "A2", "A3"],
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
        >>> obj["A3", "public.kern2.A"]
        1
        >>> sorted(obj.keys())[1]
        ('A3', 'A3')
        >>> sorted(obj.values())[3]
        4
        """
        if pair in self._kerning:
            return self._kerning[pair]
        side1, side2 = pair
        if side1.startswith(side1Prefix):
            side1Group = side1
            side1 = None
        else:
            side1Group = self._side1GroupMap.get(side1)
        if side2.startswith(side2Prefix):
            side2Group = side2
            side2 = None
        else:
            side2Group = self._side2GroupMap.get(side2)
        if (side1Group, side2) in self._kerning:
            return self._kerning[side1Group, side2]
        elif (side1, side2Group) in self._kerning:
            return self._kerning[side1, side2Group]
        elif (side1Group, side2Group) in self._kerning:
            return self._kerning[side1Group, side2Group]
        else:
            return 0

    def get(self, pair):
        v = self[pair]
        return v

    # ---------
    # Pair Type
    # ---------

    def guessPairType(self, pair):
        """
        >>> kerning = {
        ...     ("public.kern1.A", "public.kern2.A") : 1,
        ...     ("A1", "public.kern2.A") : 2,
        ...     ("public.kern1.A", "A2") : 3,
        ...     ("A3", "A3") : 4,
        ...     ("public.kern1.B", "public.kern2.B") : 5,
        ...     ("public.kern1.B", "B") : 6,
        ...     ("public.kern1.C", "public.kern2.C") : 7,
        ...     ("C", "public.kern2.C") : 8,
        ... }
        >>> groups = {
        ... "public.kern1.A" : ["A", "A1", "A2", "A3"],
        ... "public.kern2.A" : ["A", "A1", "A2", "A3"],
        ... "public.kern1.B" : ["B"],
        ... "public.kern2.B" : ["B"],
        ... "public.kern1.C" : ["C"],
        ... "public.kern2.C" : ["C"],
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj.guessPairType(("public.kern1.A", "public.kern2.A"))
        ('group', 'group')
        >>> obj.guessPairType(("A1", "public.kern2.A"))
        ('exception', 'group')
        >>> obj.guessPairType(("public.kern1.A", "A2"))
        ('group', 'exception')
        >>> obj.guessPairType(("A3", "A3"))
        ('exception', 'exception')
        >>> obj.guessPairType(("A", "A"))
        ('group', 'group')
        >>> obj.guessPairType(("B", "B"))
        ('group', 'exception')
        >>> obj.guessPairType(("C", "C"))
        ('exception', 'group')
        """
        side1, side2 = pair
        if side1.startswith(side1Prefix):
            side1Group = side1
        else:
            side1Group = self._side1GroupMap.get(side1)
        if side2.startswith(side2Prefix):
            side2Group = side2
        else:
            side2Group = self._side2GroupMap.get(side2)
        side1Type = side2Type = "glyph"
        if pair in self:
            if side1 == side1Group:
                side1Type = "group"
            elif side1Group is not None:
                side1Type = "exception"
            if side2 == side2Group:
                side2Type = "group"
            elif side2Group is not None:
                side2Type = "exception"
        elif (side1Group, side2) in self:
            side1Type = "group"
            if side2Group is not None:
                if side2 != side2Group:
                    side2Type = "exception"
        elif (side1, side2Group) in self:
            side2Type = "group"
            if side1Group is not None:
                if side1 != side1Group:
                    side1Type = "exception"
        else:
            if side1Group is not None:
                side1Type = "group"
            if side2Group is not None:
                side2Type = "group"
        return side1Type, side2Type

    # ----
    # Copy
    # ----

    def copy(self):
        """
        >>> kerning1 = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : 1,
        ...     ("NotIn2", "NotIn2") : 1,
        ...     ("public.kern1.NotIn2", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups1 = {
        ...     "public.kern1.NotIn1" : ["C"],
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> obj1 = MathKerning(kerning1, groups1)
        >>> obj2 = obj1.copy()
        >>> sorted(obj1.items()) == sorted(obj2.items())
        True
        """
        k = MathKerning(self._kerning)
        k._side1Groups = deepcopy(self._side1Groups)
        k._side2Groups = deepcopy(self._side2Groups)
        k._side1GroupMap = deepcopy(self._side1GroupMap)
        k._side2GroupMap = deepcopy(self._side2GroupMap)
        return k

    # ----
    # Math
    # ----

    # math with other kerning

    def __add__(self, other):
        """
        >>> kerning1 = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : 1,
        ...     ("NotIn2", "NotIn2") : 1,
        ...     ("public.kern1.NotIn2", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups1 = {
        ...     "public.kern1.NotIn1" : ["C"],
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> kerning2 = {
        ...     ("A", "A") : -1,
        ...     ("B", "B") : 1,
        ...     ("NotIn1", "NotIn1") : 1,
        ...     ("public.kern1.NotIn1", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups2 = {
        ...     "public.kern1.NotIn2" : ["C"],
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> obj = MathKerning(kerning1, groups1) + MathKerning(kerning2, groups2)
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('NotIn1', 'NotIn1'), 1), (('NotIn2', 'NotIn2'), 1), (('public.kern1.D', 'public.kern2.D'), 2), (('public.kern1.NotIn1', 'C'), 1), (('public.kern1.NotIn2', 'C'), 1)]
        >>> sorted(obj.groups()["public.kern1.D"])
        ['D', 'H']
        >>> sorted(obj.groups()["public.kern2.D"])
        ['D', 'H']

        groups1 = groups2
        -----------------
        >>> kerning1 = {
        ...     ("A", "A") : 1,
        ...     ("B", "B") : 1,
        ...     ("NotIn2", "NotIn2") : 1,
        ...     ("public.kern1.NotIn2", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups1 = {
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> kerning2 = {
        ...     ("A", "A") : -1,
        ...     ("B", "B") : 1,
        ...     ("NotIn1", "NotIn1") : 1,
        ...     ("public.kern1.NotIn1", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups2 = {
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> obj = MathKerning(kerning1, groups1) + MathKerning(kerning2, groups2)
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('NotIn1', 'NotIn1'), 1), (('NotIn2', 'NotIn2'), 1), (('public.kern1.D', 'public.kern2.D'), 2), (('public.kern1.NotIn1', 'C'), 1), (('public.kern1.NotIn2', 'C'), 1)]
        >>> sorted(obj.groups()["public.kern1.D"])
        ['D', 'H']
        >>> sorted(obj.groups()["public.kern2.D"])
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
        ...     ("public.kern1.NotIn2", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups1 = {
        ...     "public.kern1.NotIn1" : ["C"],
        ...     "public.kern1.D" : ["D", "H"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> kerning2 = {
        ...     ("A", "A") : -1,
        ...     ("B", "B") : 1,
        ...     ("NotIn1", "NotIn1") : 1,
        ...     ("public.kern1.NotIn1", "C") : 1,
        ...     ("public.kern1.D", "public.kern2.D") : 1,
        ... }
        >>> groups2 = {
        ...     "public.kern1.NotIn2" : ["C"],
        ...     "public.kern1.D" : ["D"],
        ...     "public.kern2.D" : ["D", "H"],
        ... }
        >>> obj = MathKerning(kerning1, groups1) - MathKerning(kerning2, groups2)
        >>> sorted(obj.items())
        [(('A', 'A'), 2), (('NotIn1', 'NotIn1'), -1), (('NotIn2', 'NotIn2'), 1), (('public.kern1.NotIn1', 'C'), -1), (('public.kern1.NotIn2', 'C'), 1)]
        >>> sorted(obj.groups()["public.kern1.D"])
        ['D', 'H']
        >>> sorted(obj.groups()["public.kern2.D"])
        ['D', 'H']
        """
        k = self._processMathOne(other, sub)
        k.cleanup()
        return k

    def _processMathOne(self, other, funct):
        comboPairs = set(self._kerning.keys()) | set(other._kerning.keys())
        kerning = dict.fromkeys(comboPairs, None)
        for k in comboPairs:
            v1 = self.get(k)
            v2 = other.get(k)
            v = funct(v1, v2)
            kerning[k] = v
        g1 = self.groups()
        g2 = other.groups()
        if g1 == g2:
            groups = g1
        else:
            comboGroups = set(g1.keys()) | set(g2.keys())
            groups = dict.fromkeys(comboGroups, None)
            for groupName in comboGroups:
                s1 = set(g1.get(groupName, []))
                s2 = set(g2.get(groupName, []))
                groups[groupName] = list(s1 | s2)
        ks = MathKerning(kerning, groups)
        return ks

    # math with factor

    def __mul__(self, factor):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C2", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 2,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C1", "C2"],
        ...     "public.kern2.C" : ["C1", "C2"],
        ... }
        >>> obj = MathKerning(kerning, groups) * 2
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 4)]

        tuple factor
        ------------
        >>> obj = MathKerning(kerning, groups) * (3, 2)
        >>> sorted(obj.items())
        [(('B', 'B'), 3), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 6)]
        """
        if isinstance(factor, tuple):
            factor = factor[0]
        k = self._processMathTwo(factor, mul)
        k.cleanup()
        return k

    def __rmul__(self, factor):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C2", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 2,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C1", "C2"],
        ...     "public.kern2.C" : ["C1", "C2"],
        ... }
        >>> obj = 2 * MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 4)]

        tuple factor
        ------------
        >>> obj = (3, 2) * MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('B', 'B'), 3), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 6)]
        """
        if isinstance(factor, tuple):
            factor = factor[0]
        k = self._processMathTwo(factor, mul)
        k.cleanup()
        return k

    def __div__(self, factor):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 4,
        ...     ("C2", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 4,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C1", "C2"],
        ...     "public.kern2.C" : ["C1", "C2"],
        ... }
        >>> obj = MathKerning(kerning, groups) / 2
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 2)]

        tuple factor
        ------------
        >>> obj = MathKerning(kerning, groups) / (4, 2)
        >>> sorted(obj.items())
        [(('B', 'B'), 1), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 1)]
        """
        if isinstance(factor, tuple):
            factor = factor[0]
        k = self._processMathTwo(factor, div)
        k.cleanup()
        return k

    __truediv__ = __div__

    def __rdiv__(self, factor):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 4,
        ...     ("C2", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 4,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C1", "C2"],
        ...     "public.kern2.C" : ["C1", "C2"],
        ... }
        >>> obj = 2 / MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('B', 'B'), 2), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 2)]

        tuple factor
        ------------
        >>> obj = (4, 2) / MathKerning(kerning, groups)
        >>> sorted(obj.items())
        [(('B', 'B'), 1), (('C2', 'public.kern2.C'), 0), (('public.kern1.C', 'public.kern2.C'), 1)]
        """
        if isinstance(factor, tuple):
            factor = factor[0]
        k = self._processMathTwo(factor, div)
        k.cleanup()
        return k

    __rtruediv__ = __rdiv__

    def _processMathTwo(self, factor, funct):
        kerning = deepcopy(self._kerning)
        for k, v in self._kerning.items():
            v = funct(v, factor)
            kerning[k] = v
        ks = MathKerning(kerning)
        ks._side1Groups = deepcopy(self._side1Groups)
        ks._side2Groups = deepcopy(self._side2Groups)
        ks._side1GroupMap = deepcopy(self._side1GroupMap)
        ks._side2GroupMap = deepcopy(self._side2GroupMap)
        return ks

    # ---------
    # More math
    # ---------

    def round(self, multiple=1):
        """
        >>> kerning = {
        ...     ("A", "A") : 1.99,
        ...     ("B", "B") : 4,
        ...     ("C", "C") : 7,
        ...     ("D", "D") : 9.01,
        ... }
        >>> obj = MathKerning(kerning)
        >>> obj.round(5)
        >>> sorted(obj.items())
        [(('A', 'A'), 0), (('B', 'B'), 5), (('C', 'C'), 5), (('D', 'D'), 10)]
        """
        multiple = float(multiple)
        for k, v in self._kerning.items():
            self._kerning[k] = int(round(int(round(v / multiple)) * multiple))

    # -------
    # Cleanup
    # -------

    def cleanup(self):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 1,
        ...     ("D", "D") : 1.0,
        ...     ("E", "E") : 1.2,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C", "C1"],
        ...     "public.kern2.C" : ["C", "C1"]
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj.cleanup()
        >>> sorted(obj.items())
        [(('B', 'B'), 1), (('C', 'public.kern2.C'), 0), (('D', 'D'), 1), (('E', 'E'), 1.2), (('public.kern1.C', 'public.kern2.C'), 1)]
        """
        for (side1, side2), v in list(self._kerning.items()):
            if int(v) == v:
                v = int(v)
                self._kerning[side1, side2] = v
            if v == 0:
                side1Type, side2Type = self.guessPairType((side1, side2))
                if side1Type != "exception" and side2Type != "exception":
                    del self._kerning[side1, side2]

    # ----------
    # Extraction
    # ----------

    def extractKerning(self, font):
        """
        >>> kerning = {
        ...     ("A", "A") : 0,
        ...     ("B", "B") : 1,
        ...     ("C", "public.kern2.C") : 0,
        ...     ("public.kern1.C", "public.kern2.C") : 1,
        ...     ("D", "D") : 1.0,
        ...     ("E", "E") : 1.2,
        ... }
        >>> groups = {
        ...     "public.kern1.C" : ["C", "C1"],
        ...     "public.kern2.C" : ["C", "C1"]
        ... }
        >>> from robofab.world import RFont
        >>> font = RFont()
        >>> font.kerning.asDict() == {}
        True
        >>> list(font.groups.items()) == []
        True
        >>> obj = MathKerning(kerning, groups)
        >>> obj.extractKerning(font)
        >>> sorted(font.kerning.asDict().items())
        [(('B', 'B'), 1), (('D', 'D'), 1), (('E', 'E'), 1), (('public.kern1.C', 'public.kern2.C'), 1)]
        >>> sorted(font.groups.items())
        [('public.kern1.C', ['C', 'C1']), ('public.kern2.C', ['C', 'C1'])]
        """
        self._resolveConflictingKerning()
        font.kerning.clear()
        font.kerning.update(self._kerning)
        font.groups.update(self.groups())

    def _resolveConflictingKerning(self):
        """
        Resolve conflicting kerning by averaging the
        conflicting pairs. This is not a "correct"
        solution to the problem, but there is not
        a correct solution. The problem is that two
        source kerning dictionaries can be combined
        through the math functions to create conflicting
        pairs. The masters are not incorrect and the
        conflicts are mathematically correct. However,
        the conflicts are not logically solvable.
        This logical conflict must not be passed to
        the caller. There is not a right way to solve
        this, so do the thing that yields a mathematically
        reproducable result.

        >>> groups = {
        ...     "public.kern1.O" : ["O", "D", "Q"],
        ...     "public.kern2.E" : ["E", "F"]
        ... }
        >>> kerning = {
        ...     ("public.kern1.O", "public.kern2.E") : -100,
        ...     ("public.kern1.O", "F") : -200,
        ...     ("Q", "public.kern2.E") : -250,
        ...     ("D", "F") : -300,
        ... }
        >>> obj = MathKerning(kerning, groups)
        >>> obj._resolveConflictingKerning()
        >>> sorted(obj._kerning.values())
        [-300, -225.0, -100]
        """
        valid, errors, pairs = kerningValidatorReportPairs(self._kerning, self._groups)
        if not valid:
            for pair1, pair2 in pairs:
                if pair1 not in self._kerning or pair2 not in self._kerning:
                    continue
                value1 = self._kerning[pair1]
                value2 = self._kerning[pair2]
                del self._kerning[pair2]
                self._kerning[pair1] = (value1 + value2) / 2.0
            valid, errors, pairs = kerningValidatorReportPairs(self._kerning, self._groups)
            if not valid:
                self._resolveConflictingKerning()


if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
