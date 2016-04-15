from __future__ import print_function, absolute_import
from copy import deepcopy
from robofab.pens.pointPen import AbstractPointPen
from robofab.pens.adapterPens import PointToSegmentPen
from fontMath.mathFunctions import *
from fontMath.mathGuideline import *

# ------------------
# UFO 3 branch notes
# ------------------
#
# to do:
# X anchors
#   - try to preserve ordering?
# X components
#   X identifiers
# X contours
#   X identifiers
# X points
#   X identifiers
# X guidelines
# X height
# X image
#
# - is there any cruft that can be removed?
# X why is divPt here? move all of those to the math funcions
#   and get rid of the robofab dependency.
# - FilterRedundantPointPen._flushContour is a mess
# X for the pt math funcons, always send (x, y) factors instead
#   of coercing within the funcion. the coercion can happen at
#   the beginning of the _processMathTwo method.
#   - try list comprehensions in the point math for speed
#
# Questionable stuff:
# X is getRef needed?
# X nothing is ever set to _structure. should it be?
# X should the compatibilty be a function or pen?
# X the lib import is shallow and modifications to
#   lower level objects (ie dict) could modify the
#   original object. this probably isn't desirable.
#   deepcopy won't work here since it will try to
#   maintain the original class. may need to write
#   a custom copier. or maybe something like this
#   would be sufficient:
#     self.lib = deepcopy(dict(glyph.lib))
#   the class would be maintained for everything but
#   the top level. that shouldn't matter for the
#   purposes here.
# - __cmp__ is dubious but harmless i suppose.
# X is generationCount needed?
# X can box become bounds? have both?

try:
    basestring, xrange
    range = xrange
except NameError:
    basestring = str


class MathGlyph(object):

    """
    A very shallow glyph object for rapid math operations.

    Notes about glyph math:
    -   absolute contour compatibility is required
    -   absolute component, anchor, guideline and image compatibility is NOT required.
        in cases of incompatibility in this data, only compatible data is processed and
        returned. becuase of this, anchors and components may not be returned in the
        same order as the original.
    """

    def __init__(self, glyph):
        self.contours = []
        self.components = []
        if glyph is None:
            self.anchors = []
            self.guidelines = []
            self.image = _expandImage(None)
            self.lib = {}
            self.name = None
            self.unicodes = None
            self.width = None
            self.height = None
            self.note = None
        else:
            p = MathGlyphPen(self)
            glyph.drawPoints(p)
            self.anchors = [dict(anchor) for anchor in glyph.anchors]
            self.guidelines = [_expandGuideline(guideline) for guideline in glyph.guidelines]
            self.image = _expandImage(glyph.image)
            self.lib = deepcopy(dict(glyph.lib))
            self.name = glyph.name
            self.unicodes = list(glyph.unicodes)
            self.width = glyph.width
            self.height = glyph.height
            self.note = glyph.note

    def __cmp__(self, other):
        flag = False
        if self.name != other.name:
            flag = True
        if self.unicodes != other.unicodes:
            flag = True
        if self.width != other.width:
            flag = True
        if self.height != other.height:
            flag = True
        if self.note != other.note:
            flag = True
        if self.lib != other.lib:
            flag = True
        if self.contours != other.contours:
            flag = True
        if self.components != other.components:
            flag = True
        if self.anchors != other.anchors:
            flag = True
        if self.guidelines != other.guidelines:
            flag = True
        if self.image != other.image:
            flag = True
        return flag

    # ----
    # Copy
    # ----

    def copy(self):
        """return a new MathGlyph containing all data in self"""
        return MathGlyph(self)

    def copyWithoutMathSubObjects(self):
        """
        return a new MathGlyph containing all data except:
        contours
        components
        anchors
        guidelines

        this is used mainly for internal glyph math.
        """
        n = MathGlyph(None)
        n.name = self.name
        if self.unicodes is not None:
            n.unicodes = list(self.unicodes)
        n.width = self.width
        n.height = self.height
        n.note = self.note
        n.lib = deepcopy(dict(self.lib))
        return n

    # ----
    # Math
    # ----

    # math with other glyph

    def __add__(self, otherGlyph):
        copiedGlyph = self.copyWithoutMathSubObjects()
        self._processMathOne(copiedGlyph, otherGlyph, addPt, add)
        return copiedGlyph

    def __sub__(self, otherGlyph):
        copiedGlyph = self.copyWithoutMathSubObjects()
        self._processMathOne(copiedGlyph, otherGlyph, subPt, sub)
        return copiedGlyph

    def _processMathOne(self, copiedGlyph, otherGlyph, ptFunc, func):
        # width
        copiedGlyph.width = func(self.width, otherGlyph.width)
        # height
        copiedGlyph.height = func(self.height, otherGlyph.height)
        # contours
        copiedGlyph.contours = []
        if self.contours:
            copiedGlyph.contours = _processMathOneContours(self.contours, otherGlyph.contours, ptFunc)
        # components
        copiedGlyph.components = []
        if self.components:
            componentPairs = _pairComponents(self.components, otherGlyph.components)
            copiedGlyph.components = _processMathOneComponents(componentPairs, ptFunc)
        # anchors
        copiedGlyph.anchors = []
        if self.anchors:
            anchorTree1 = _anchorTree(self.anchors)
            anchorTree2 = _anchorTree(otherGlyph.anchors)
            anchorPairs = _pairAnchors(anchorTree1, anchorTree2)
            copiedGlyph.anchors = _processMathOneAnchors(anchorPairs, ptFunc)
        # guidelines
        copiedGlyph.guidelines = []
        if self.guidelines:
            guidelinePairs = _pairGuidelines(self.guidelines, otherGlyph.guidelines)
            copiedGlyph.guidelines = _processMathOneGuidelines(guidelinePairs, ptFunc, func)
        # image
        copiedGlyph.image = _expandImage(None)
        imagePair = _pairImages(self.image, otherGlyph.image)
        if imagePair:
            copiedGlyph.image = _processMathOneImage(imagePair, ptFunc)

    # math with factor

    def __mul__(self, factor):
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        copiedGlyph = self.copyWithoutMathSubObjects()
        self._processMathTwo(copiedGlyph, factor, mulPt, mul)
        return copiedGlyph

    __rmul__ = __mul__

    def __div__(self, factor):
        if not isinstance(factor, tuple):
            factor = (factor, factor)
        copiedGlyph = self.copyWithoutMathSubObjects()
        self._processMathTwo(copiedGlyph, factor, divPt, div)
        return copiedGlyph

    __truediv__ = __div__

    __rdiv__ = __div__

    __rtruediv__ = __rdiv__

    def _processMathTwo(self, copiedGlyph, factor, ptFunc, func):
        # width
        copiedGlyph.width = func(self.width, factor[0])
        # height
        copiedGlyph.height = func(self.height, factor[1])
        # contours
        copiedGlyph.contours = []
        if self.contours:
            copiedGlyph.contours = _processMathTwoContours(self.contours, factor, ptFunc)
        # components
        copiedGlyph.components = []
        if self.components:
            copiedGlyph.components = _processMathTwoComponents(self.components, factor, ptFunc)
        # anchors
        copiedGlyph.anchors = []
        if self.anchors:
            copiedGlyph.anchors = _processMathTwoAnchors(self.anchors, factor, ptFunc)
        # guidelines
        copiedGlyph.guidelines = []
        if self.guidelines:
            copiedGlyph.guidelines = _processMathTwoGuidelines(self.guidelines, factor, func)
        # image
        if self.image:
            copiedGlyph.image = _processMathTwoImage(self.image, factor, ptFunc)

    # -------
    # Additional math
    # -------
    def round(self, digits=None):
        """round the geometry."""
        copiedGlyph = self.copyWithoutMathSubObjects()
        # misc
        copiedGlyph.width = _roundNumber(self.width, digits)
        copiedGlyph.height = _roundNumber(self.height, digits)
        # contours
        copiedGlyph.contours = []
        if self.contours:
            copiedGlyph.contours = _roundContours(self.contours, digits)
        # components
        copiedGlyph.components = []
        if self.components:
            copiedGlyph.components = _roundComponents(self.components, digits)
        # guidelines
        copiedGlyph.guidelines = []
        if self.guidelines:
            copiedGlyph.guidelines = _roundGuidelines(self.guidelines, digits)
        # anchors
        copiedGlyph.anchors = []
        if self.anchors:
            copiedGlyph.anchors = _roundAnchors(self.anchors, digits)
        # image
        copiedGlyph.image = None
        if self.image:
            copiedGlyph.image = _roundImage(self.image, digits)
        return copiedGlyph


    # -------
    # Pen API
    # -------

    def getPointPen(self):
        """get a point pen for drawing to this object"""
        return MathGlyphPen(self)

    def drawPoints(self, pointPen, filterReduntantPoints=False):
        """draw self using pointPen"""
        if filterReduntantPoints:
            pointPen = FilterRedundantPointPen(pointPen)
        for contour in self.contours:
            pointPen.beginPath(identifier=contour["identifier"])
            for segmentType, pt, smooth, name, identifier in contour["points"]:
                pointPen.addPoint(pt=pt, segmentType=segmentType, smooth=smooth, name=name, identifier=identifier)
            pointPen.endPath()
        for component in self.components:
            pointPen.addComponent(component["baseGlyph"], component["transformation"], identifier=component["identifier"])

    def draw(self, pen, filterReduntantPoints=False):
        """draw self using pen"""
        pointPen = PointToSegmentPen(pen)
        self.drawPoints(pointPenfilterReduntantPoints=filterReduntantPoints)

    # ----------
    # Extraction
    # ----------

    def extractGlyph(self, glyph, pointPen=None, onlyGeometry=False):
        """
        "rehydrate" to a glyph. this requires
        a glyph as an argument. if a point pen other
        than the type of pen returned by glyph.getPointPen()
        is required for drawing, send this the needed point pen.
        """
        if pointPen is None:
            pointPen = glyph.getPointPen()
        glyph.clearContours()
        glyph.clearComponents()
        glyph.clearAnchors()
        glyph.clearGuidelines()
        glyph.lib.clear()
        cleanerPen = FilterRedundantPointPen(pointPen)
        self.drawPoints(cleanerPen)
        glyph.anchors = [dict(anchor) for anchor in self.anchors]
        glyph.guidelines = [_compressGuideline(guideline) for guideline in self.guidelines]
        glyph.image = _compressImage(self.image)
        glyph.lib = deepcopy(dict(self.lib))
        glyph.width = self.width
        glyph.height = self.height
        glyph.note = self.note
        if not onlyGeometry:
            glyph.name = self.name
            glyph.unicodes = list(self.unicodes)
        return glyph


# ----------
# Point Pens
# ----------

class MathGlyphPen(AbstractPointPen):

    """
    Point pen for building MathGlyph data structures.

    >>> pen = MathGlyphPen()
    >>> pen.beginPath(identifier="contour 1")
    >>> pen.addPoint((  0, 100), "line", smooth=False, name="name 1", identifier="point 1")
    >>> pen.addPoint((100, 100), "line", smooth=False, name="name 2", identifier="point 2")
    >>> pen.addPoint((100,   0), "line", smooth=False, name="name 3", identifier="point 3")
    >>> pen.addPoint((  0,   0), "line", smooth=False, name="name 4", identifier="point 4")
    >>> pen.endPath()
    >>> expected = [
    ...     ("curve", (  0, 100), False, "name 1", "point 1"),
    ...     (None,    (  0, 100), False, None,     None),
    ...     (None,    (100, 100), False, None,     None),
    ...     ("curve", (100, 100), False, "name 2", "point 2"),
    ...     (None,    (100, 100), False, None,     None),
    ...     (None,    (100,   0), False, None,     None),
    ...     ("curve", (100,   0), False, "name 3", "point 3"),
    ...     (None,    (100,   0), False, None,     None),
    ...     (None,    (  0,   0), False, None,     None),
    ...     ("curve", (  0,   0), False, "name 4", "point 4"),
    ...     (None,    (  0,   0), False, None,     None),
    ...     (None,    (  0, 100), False, None,     None),
    ... ]
    >>> pen.contours[-1]["points"] == expected
    True
    >>> pen.contours[-1]["identifier"]
    'contour 1'

    >>> pen = MathGlyphPen()
    >>> pen.beginPath(identifier="contour 1")
    >>> pen.addPoint((  0,  50), "curve", smooth=False, name="name 1", identifier="point 1")
    >>> pen.addPoint(( 50, 100), "line", smooth=False, name="name 2", identifier="point 2")
    >>> pen.addPoint(( 75, 100), None)
    >>> pen.addPoint((100,  75), None)
    >>> pen.addPoint((100,  50), "curve", smooth=True, name="name 3", identifier="point 3")
    >>> pen.addPoint((100,  25), None)
    >>> pen.addPoint(( 75,   0), None)
    >>> pen.addPoint(( 50,   0), "curve", smooth=False, name="name 4", identifier="point 4")
    >>> pen.addPoint(( 25,   0), None)
    >>> pen.addPoint((  0,  25), None)
    >>> pen.endPath()
    >>> expected = [
    ...     ("curve", (  0,  50), False, "name 1", "point 1"),
    ...     (None,    (  0,  50), False, None,     None),
    ...     (None,    ( 50, 100), False, None,     None),
    ...     ("curve", ( 50, 100), False, "name 2", "point 2"),
    ...     (None,    ( 75, 100), False, None,     None),
    ...     (None,    (100,  75), False, None,     None),
    ...     ("curve", (100,  50), True, "name 3", "point 3"),
    ...     (None,    (100,  25), False, None,     None),
    ...     (None,    ( 75,   0), False, None,     None),
    ...     ("curve", ( 50,   0), False, "name 4", "point 4"),
    ...     (None,    ( 25,   0), False, None,     None),
    ...     (None,    (  0,  25), False, None,     None),
    ... ]
    >>> pen.contours[-1]["points"] == expected
    True
    >>> pen.contours[-1]["identifier"]
    'contour 1'
    """

    def __init__(self, glyph=None):
        if glyph is None:
            self.contours = []
            self.components = []
        else:
            self.contours = glyph.contours
            self.components = glyph.components
        self._contourIdentifier = None
        self._points = []

    def _flushContour(self):
        """
        This normalizes the contour so that:
        - there are no line segments. in their place will be
          curve segments with the off curves positioned on top
          of the previous on curve and the new curve on curve.
        - the contour starts with an on curve
        """
        self.contours.append(
            dict(identifier=self._contourIdentifier, points=[])
        )
        contourPoints = self.contours[-1]["points"]
        points = self._points
        # move offcurves at the beginning of the contour to the end
        haveOnCurve = False
        for point in points:
            if point[0] is not None:
                haveOnCurve = True
                break
        if haveOnCurve:
            while 1:
                if points[0][0] is None:
                    point = points.pop(0)
                    points.append(point)
                else:
                    break
        # convert lines to curves
        holdingOffCurves = []
        for index, point in enumerate(points):
            segmentType = point[0]
            if segmentType == "line":
                pt, smooth, name, identifier = point[1:]
                prevPt = points[index - 1][1]
                if index == 0:
                    holdingOffCurves.append((None, prevPt, False, None, None))
                    holdingOffCurves.append((None, pt, False, None, None))
                else:
                    contourPoints.append((None, prevPt, False, None, None))
                    contourPoints.append((None, pt, False, None, None))
                contourPoints.append(("curve", pt, smooth, name, identifier))
            else:
                contourPoints.append(point)
        contourPoints.extend(holdingOffCurves)

    def beginPath(self, identifier=None):
        self._contourIdentifier = identifier
        self._points = []

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, identifier=None, **kwargs):
        self._points.append((segmentType, pt, smooth, name, identifier))

    def endPath(self):
        self._flushContour()

    def addComponent(self, baseGlyph, transformation, identifier=None, **kwargs):
        self.components.append(dict(baseGlyph=baseGlyph, transformation=transformation, identifier=identifier))


class FilterRedundantPointPen(AbstractPointPen):

    def __init__(self, anotherPointPen):
        self._pen = anotherPointPen
        self._points = []

    def _flushContour(self):
        """
        >>> points = [
        ...     ("curve", (  0, 100), False, "name 1", "point 1"),
        ...     (None,    (  0, 100), False, None,     None),
        ...     (None,    (100, 100), False, None,     None),
        ...     ("curve", (100, 100), False, "name 2", "point 2"),
        ...     (None,    (100, 100), False, None,     None),
        ...     (None,    (100,   0), False, None,     None),
        ...     ("curve", (100,   0), False, "name 3", "point 3"),
        ...     (None,    (100,   0), False, None,     None),
        ...     (None,    (  0,   0), False, None,     None),
        ...     ("curve", (  0,   0), False, "name 4", "point 4"),
        ...     (None,    (  0,   0), False, None,     None),
        ...     (None,    (  0, 100), False, None,     None),
        ... ]
        >>> testPen = _TestPointPen()
        >>> filterPen = FilterRedundantPointPen(testPen)
        >>> filterPen.beginPath(identifier="contour 1")
        >>> for segmentType, pt, smooth, name, identifier in points:
        ...     filterPen.addPoint(pt, segmentType=segmentType, smooth=smooth, name=name, identifier=identifier)
        >>> filterPen.endPath()
        >>> testPen.dump()
        beginPath(identifier="contour 1")
        addPoint((0, 100), segmentType="line", smooth=False, name="name 1", identifier="point 1")
        addPoint((100, 100), segmentType="line", smooth=False, name="name 2", identifier="point 2")
        addPoint((100, 0), segmentType="line", smooth=False, name="name 3", identifier="point 3")
        addPoint((0, 0), segmentType="line", smooth=False, name="name 4", identifier="point 4")
        endPath()
        """
        points = self._points
        prevOnCurve = None
        offCurves = []

        pointsToDraw = []

        # deal with the first point
        pt, segmentType, smooth, name, identifier = points[0]
        # if it is an offcurve, add it to the offcurve list
        if segmentType is None:
            offCurves.append((pt, segmentType, smooth, name, identifier))
        else:
            # potential redundancy
            if segmentType == "curve":
                # gather preceding off curves
                testOffCurves = []
                lastPoint = None
                for i in range(len(points)):
                    i = -i - 1
                    testPoint = points[i]
                    testSegmentType = testPoint[1]
                    if testSegmentType is not None:
                        lastPoint = testPoint[0]
                        break
                    testOffCurves.append(testPoint[0])
                # if two offcurves exist we can test for redundancy
                if len(testOffCurves) == 2:
                    if testOffCurves[1] == lastPoint and testOffCurves[0] == pt:
                        segmentType = "line"
                        # remove the last two points
                        points = points[:-2]
            # add the point to the contour
            pointsToDraw.append((pt, segmentType, smooth, name, identifier))
            prevOnCurve = pt
        for pt, segmentType, smooth, name, identifier in points[1:]:
            # store offcurves
            if segmentType is None:
                offCurves.append((pt, segmentType, smooth, name, identifier))
                continue
            # curves are a potential redundancy
            elif segmentType == "curve":
                if len(offCurves) == 2:
                    # test for redundancy
                    if offCurves[0][0] == prevOnCurve and offCurves[1][0] == pt:
                        offCurves = []
                        segmentType = "line"
            # add all offcurves
            for offCurve in offCurves:
                pointsToDraw.append(offCurve)
            # add the on curve
            pointsToDraw.append((pt, segmentType, smooth, name, identifier))
            # reset the stored data
            prevOnCurve = pt
            offCurves = []
        # catch any remaining offcurves
        if len(offCurves) != 0:
            for offCurve in offCurves:
                pointsToDraw.append(offCurve)
        # draw to the pen
        for pt, segmentType, smooth, name, identifier in pointsToDraw:
            self._pen.addPoint(pt, segmentType, smooth=smooth, name=name, identifier=identifier)

    def beginPath(self, identifier=None, **kwargs):
        self._points = []
        self._pen.beginPath(identifier=identifier)

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, identifier=None, **kwargs):
        self._points.append((pt, segmentType, smooth, name, identifier))

    def endPath(self):
        self._flushContour()
        self._pen.endPath()

    def addComponent(self, baseGlyph, transformation, identifier=None, **kwargs):
        self._pen.addComponent(baseGlyph, transformation, identifier)


class _TestPointPen(AbstractPointPen):

    def __init__(self):
        self._text = []

    def dump(self):
        for line in self._text:
            print(line)

    def _prep(self, i):
        if isinstance(i, basestring):
            i = "\"%s\"" % i
        return str(i)

    def beginPath(self, identifier=None, **kwargs):
        self._text.append("beginPath(identifier=%s)" % self._prep(identifier))

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, identifier=None, **kwargs):
        self._text.append("addPoint(%s, segmentType=%s, smooth=%s, name=%s, identifier=%s)" % (
                self._prep(pt),
                self._prep(segmentType),
                self._prep(smooth),
                self._prep(name),
                self._prep(identifier)
            )
        )

    def endPath(self):
        self._text.append("endPath()")

    def addComponent(self, baseGlyph, transformation, identifier=None, **kwargs):
        self._text.append("addComponent(baseGlyph=%s, transformation=%s, identifier=%s)" % (
                self._prep(baseGlyph),
                self._prep(transformation),
                self._prep(identifier)
            )
        )


# -------
# Support
# -------

# contours

def _processMathOneContours(contours1, contours2, func):
    """
    >>> contours1 = [
    ...     dict(identifier="contour 1", points=[("line", (1, 3), False, "test", "1")])
    ... ]
    >>> contours2 = [
    ...     dict(identifier=None, points=[(None, (4, 6), True, None, None)])
    ... ]
    >>> expected = [
    ...     dict(identifier="contour 1", points=[("line", (5, 9), False, "test", "1")])
    ... ]
    >>> _processMathOneContours(contours1, contours2, addPt) == expected
    True
    """
    result = []
    for index, contour1 in enumerate(contours1):
        contourIdentifier = contour1["identifier"]
        points1 = contour1["points"]
        points2 = contours2[index]["points"]
        resultPoints = []
        for index, point in enumerate(points1):
            segmentType, pt1, smooth, name, identifier = point
            pt2 = points2[index][1]
            pt = func(pt1, pt2)
            resultPoints.append((segmentType, pt, smooth, name, identifier))
        result.append(dict(identifier=contourIdentifier, points=resultPoints))
    return result

def _processMathTwoContours(contours, factor, func):
    """
    >>> contours = [
    ...     dict(identifier="contour 1", points=[("line", (1, 3), False, "test", "1")])
    ... ]
    >>> expected = [
    ...     dict(identifier="contour 1", points=[("line", (2, 4.5), False, "test", "1")])
    ... ]
    >>> _processMathTwoContours(contours, (2, 1.5), mulPt) == expected
    True
    """
    result = []
    for contour in contours:
        contourIdentifier = contour["identifier"]
        points = contour["points"]
        resultPoints = []
        for point in points:
            segmentType, pt, smooth, name, identifier = point
            pt = func(pt, factor)
            resultPoints.append((segmentType, pt, smooth, name, identifier))
        result.append(dict(identifier=contourIdentifier, points=resultPoints))
    return result

# anchors

def _anchorTree(anchors):
    """
    >>> anchors = [
    ...     dict(identifier="1", name="test", x=1, y=2, color=None),
    ...     dict(name="test", x=1, y=2, color=None),
    ...     dict(name="test", x=3, y=4, color=None),
    ...     dict(name="test", x=2, y=3, color=None),
    ...     dict(name="test 2", x=1, y=2, color=None),
    ... ]
    >>> expected = {
    ...     "test" : [
    ...         ("1", 1, 2, None),
    ...         (None, 1, 2, None),
    ...         (None, 3, 4, None),
    ...         (None, 2, 3, None),
    ...     ],
    ...     "test 2" : [
    ...         (None, 1, 2, None)
    ...     ]
    ... }
    >>> _anchorTree(anchors) == expected
    True
    """
    tree = {}
    for anchor in anchors:
        x = anchor["x"]
        y = anchor["y"]
        name = anchor.get("name")
        identifier = anchor.get("identifier")
        color = anchor.get("color")
        if name not in tree:
            tree[name] = []
        tree[name].append((identifier, x, y, color))
    return tree

def _pairAnchors(anchorDict1, anchorDict2):
    """
    Anchors are paired using the following rules:


    Matching Identifiers
    --------------------
    >>> anchors1 = {
    ...     "test" : [
    ...         (None, 1, 2, None),
    ...         ("identifier 1", 3, 4, None)
    ...      ]
    ... }
    >>> anchors2 = {
    ...     "test" : [
    ...         ("identifier 1", 1, 2, None),
    ...         (None, 3, 4, None)
    ...      ]
    ... }
    >>> expected = [
    ...     (
    ...         dict(name="test", identifier=None, x=1, y=2, color=None),
    ...         dict(name="test", identifier=None, x=3, y=4, color=None)
    ...     ),
    ...     (
    ...         dict(name="test", identifier="identifier 1", x=3, y=4, color=None),
    ...         dict(name="test", identifier="identifier 1", x=1, y=2, color=None)
    ...     )
    ... ]
    >>> _pairAnchors(anchors1, anchors2) == expected
    True

    Mismatched Identifiers
    ----------------------
    >>> anchors1 = {
    ...     "test" : [
    ...         ("identifier 1", 3, 4, None)
    ...      ]
    ... }
    >>> anchors2 = {
    ...     "test" : [
    ...         ("identifier 2", 1, 2, None),
    ...      ]
    ... }
    >>> expected = [
    ...     (
    ...         dict(name="test", identifier="identifier 1", x=3, y=4, color=None),
    ...         dict(name="test", identifier="identifier 2", x=1, y=2, color=None)
    ...     )
    ... ]
    >>> _pairAnchors(anchors1, anchors2) == expected
    True
    """
    pairs = []
    for name, anchors1 in anchorDict1.items():
        if name not in anchorDict2:
            continue
        anchors2 = anchorDict2[name]
        # align with matching identifiers
        removeFromAnchors1 = []
        for anchor1 in anchors1:
            match = None
            identifier = anchor1[0]
            for anchor2 in anchors2:
                if anchor2[0] == identifier:
                    match = anchor2
                    break
            if match is not None:
                anchor2 = match
                anchors2.remove(anchor2)
                removeFromAnchors1.append(anchor1)
                a1 = dict(name=name, identifier=identifier)
                a1["x"], a1["y"], a1["color"] = anchor1[1:]
                a2 = dict(name=name, identifier=identifier)
                a2["x"], a2["y"], a2["color"] = anchor2[1:]
                pairs.append((a1, a2))
        for anchor1 in removeFromAnchors1:
            anchors1.remove(anchor1)
        if not anchors1 or not anchors2:
            continue
        # align by index
        while 1:
            anchor1 = anchors1.pop(0)
            anchor2 = anchors2.pop(0)
            a1 = dict(name=name)
            a1["identifier"], a1["x"], a1["y"], a1["color"] = anchor1
            a2 = dict(name=name, identifier=identifier)
            a2["identifier"], a2["x"], a2["y"], a2["color"] = anchor2
            pairs.append((a1, a2))
            if not anchors1:
                break
            if not anchors2:
                break
    return pairs

def _processMathOneAnchors(anchorPairs, func):
    """
    >>> anchorPairs = [
    ...     (
    ...         dict(x=100, y=-100, name="foo", identifier="1", color="0,0,0,0"),
    ...         dict(x=200, y=-200, name="bar", identifier="2", color="1,1,1,1")
    ...     )
    ... ]
    >>> expected = [
    ...     dict(x=300, y=-300, name="foo", identifier="1", color="0,0,0,0")
    ... ]
    >>> _processMathOneAnchors(anchorPairs, addPt) == expected
    True
    """
    result = []
    for anchor1, anchor2 in anchorPairs:
        anchor = dict(anchor1)
        pt1 = (anchor1["x"], anchor1["y"])
        pt2 = (anchor2["x"], anchor2["y"])
        anchor["x"], anchor["y"] = func(pt1, pt2)
        result.append(anchor)
    return result

def _processMathTwoAnchors(anchors, factor, func):
    """
    >>> anchors = [
    ...     dict(x=100, y=-100, name="foo", identifier="1", color="0,0,0,0")
    ... ]
    >>> expected = [
    ...     dict(x=200, y=-150, name="foo", identifier="1", color="0,0,0,0")
    ... ]
    >>> _processMathTwoAnchors(anchors, (2, 1.5), mulPt) == expected
    True
    """
    result = []
    for anchor in anchors:
        anchor = dict(anchor)
        pt = (anchor["x"], anchor["y"])
        anchor["x"], anchor["y"] = func(pt, factor)
        result.append(anchor)
    return result

# components

def _pairComponents(components1, components2):
    """
    >>> components1 = [
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier="1"),
    ...     dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier="1"),
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ... ]
    >>> components2 = [
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...     dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier="1"),
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier="1")
    ... ]
    >>> expected = [
    ...     (
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier="1"),
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier="1")
    ...     ),
    ...     (
    ...         dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier="1"),
    ...         dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier="1")
    ...     ),
    ...     (
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ...     ),
    ... ]
    >>> _pairComponents(components1, components2) == expected
    True

    >>> components1 = [
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...     dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ... ]
    >>> components2 = [
    ...     dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...     dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ... ]
    >>> expected = [
    ...     (
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...         dict(baseGlyph="A", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ...     ),
    ...     (
    ...         dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier=None),
    ...         dict(baseGlyph="B", transformation=(0, 0, 0, 0, 0, 0), identifier=None)
    ...     ),
    ... ]
    >>> _pairComponents(components1, components2) == expected
    True
    """
    components1 = list(components1)
    components2 = list(components2)
    pairs = []
    # align with matching identifiers
    removeFromComponents1 = []
    for component1 in components1:
        baseGlyph = component1["baseGlyph"]
        identifier = component1["identifier"]
        match = None
        for component2 in components2:
            if component2["baseGlyph"] == baseGlyph and component2["identifier"] == identifier:
                match = component2
                break
        if match is not None:
            component2 = match
            removeFromComponents1.append(component1)
            components2.remove(component2)
            pairs.append((component1, component2))
    for component1 in removeFromComponents1:
        components1.remove(component1)
    # align with index
    for component1 in components1:
        baseGlyph = component1["baseGlyph"]
        for component2 in components2:
            if component2["baseGlyph"] == baseGlyph:
                components2.remove(component2)
                pairs.append((component1, component2))
                break
    return pairs

def _processMathOneComponents(componentPairs, func):
    """
    >>> components = [
    ...    (
    ...        dict(baseGlyph="A", transformation=( 1,  3,  5,  7,  9, 11), identifier="1"),
    ...        dict(baseGlyph="A", transformation=(12, 14, 16, 18, 20, 22), identifier=None)
    ...    )
    ... ]
    >>> expected = [
    ...     dict(baseGlyph="A", transformation=(13, 17, 21, 25, 29, 33), identifier="1")
    ... ]
    >>> _processMathOneComponents(components, addPt) == expected
    True
    """
    result = []
    for component1, component2 in componentPairs:
        component = dict(component1)
        component["transformation"] = _processMathOneTransformation(component1["transformation"], component2["transformation"], func)
        result.append(component)
    return result

def _processMathTwoComponents(components, factor, func):
    """
    >>> components = [
    ...     dict(baseGlyph="A", transformation=(1, 2, 3, 4, 5, 6), identifier="1"),
    ... ]
    >>> expected = [
    ...     dict(baseGlyph="A", transformation=(2, 4, 4.5, 6, 10, 9), identifier="1")
    ... ]
    >>> _processMathTwoComponents(components, (2, 1.5), mulPt) == expected
    True
    """
    result = []
    for component in components:
        component = dict(component)
        component["transformation"] = _processMathTwoTransformation(component["transformation"], factor, func)
        result.append(component)
    return result

# image

_imageTransformationKeys = "xScale xyScale yxScale yScale xOffset yOffset".split(" ")
_defaultImageTransformation = (1, 0, 0, 1, 0, 0)
_defaultImageTransformationDict = {}
for key, value in zip(_imageTransformationKeys, _defaultImageTransformation):
    _defaultImageTransformationDict[key] = value

def _expandImage(image):
    """
    >>> _expandImage(None) == dict(fileName=None, transformation=(1, 0, 0, 1, 0, 0), color=None)
    True
    >>> _expandImage(dict(fileName="foo")) == dict(fileName="foo", transformation=(1, 0, 0, 1, 0, 0), color=None)
    True
    """
    if image is None:
        fileName = None
        transformation = _defaultImageTransformation
        color = None
    else:
        fileName = image["fileName"]
        color = image.get("color")
        transformation = tuple([
            image.get(key, _defaultImageTransformationDict[key])
            for key in _imageTransformationKeys
        ])
    return dict(fileName=fileName, transformation=transformation, color=color)

def _compressImage(image):
    """
    >>> expected = dict(fileName="foo", color=None, xScale=1, xyScale=0, yxScale=0, yScale=1, xOffset=0, yOffset=0)
    >>> _compressImage(dict(fileName="foo", transformation=(1, 0, 0, 1, 0, 0), color=None)) == expected
    True
    """
    fileName = image["fileName"]
    transformation = image["transformation"]
    color = image["color"]
    if fileName is None:
        return
    image = dict(fileName=fileName, color=color)
    for index, key in enumerate(_imageTransformationKeys):
        image[key] = transformation[index]
    return image

def _pairImages(image1, image2):
    """
    >>> image1 = dict(fileName="foo", transformation=(1, 0, 0, 1, 0, 0), color=None)
    >>> image2 = dict(fileName="foo", transformation=(2, 0, 0, 2, 0, 0), color="0,0,0,0")
    >>> _pairImages(image1, image2) == (image1, image2)
    True

    >>> image1 = dict(fileName="foo", transformation=(1, 0, 0, 1, 0, 0), color=None)
    >>> image2 = dict(fileName="bar", transformation=(1, 0, 0, 1, 0, 0), color=None)
    >>> _pairImages(image1, image2) == ()
    True
    """
    if image1["fileName"] != image2["fileName"]:
        return ()
    return (image1, image2)

def _processMathOneImage(imagePair, func):
    """
    >>> image1 = dict(fileName="foo", transformation=( 1,  3,  5,  7,  9, 11), color="0,0,0,0")
    >>> image2 = dict(fileName="bar", transformation=(12, 14, 16, 18, 20, 22), color=None)
    >>> expected = dict(fileName="foo", transformation=(13, 17, 21, 25, 29, 33), color="0,0,0,0")
    >>> _processMathOneImage((image1, image2), addPt) == expected
    True
    """
    image1, image2 = imagePair
    fileName = image1["fileName"]
    color = image1["color"]
    transformation = _processMathOneTransformation(image1["transformation"], image2["transformation"], func)
    return dict(fileName=fileName, transformation=transformation, color=color)

def _processMathTwoImage(image, factor, func):
    """
    >>> image = dict(fileName="foo", transformation=(1, 2, 3, 4, 5, 6), color="0,0,0,0")
    >>> expected = dict(fileName="foo", transformation=(2, 4, 4.5, 6, 10, 9), color="0,0,0,0")
    >>> _processMathTwoImage(image, (2, 1.5), mulPt) == expected
    True
    """
    fileName = image["fileName"]
    color = image["color"]
    transformation = _processMathTwoTransformation(image["transformation"], factor, func)
    return dict(fileName=fileName, transformation=transformation, color=color)


# transformations

def _processMathOneTransformation(transformation1, transformation2, func):
    """
    >>> transformation1 = ( 1,  3,  5,  7,  9, 11)
    >>> transformation2 = (12, 14, 16, 18, 20, 22)
    >>> expected = (13, 17, 21, 25, 29, 33)
    >>> _processMathOneTransformation(transformation1, transformation2, addPt) == expected
    True
    """
    xScale1, xyScale1, yxScale1, yScale1, xOffset1, yOffset1 = transformation1
    xScale2, xyScale2, yxScale2, yScale2, xOffset2, yOffset2 = transformation2
    xScale, yScale = func((xScale1, yScale1), (xScale2, yScale2))
    xyScale, yxScale = func((xyScale1, yxScale1), (xyScale2, yxScale2))
    xOffset, yOffset = func((xOffset1, yOffset1), (xOffset2, yOffset2))
    return (xScale, xyScale, yxScale, yScale, xOffset, yOffset)

def _processMathTwoTransformation(transformation, factor, func):
    """
    >>> transformation = (1, 2, 3, 4, 5, 6)
    >>> expected = (2, 4, 4.5, 6, 10, 9)
    >>> _processMathTwoTransformation(transformation, (2, 1.5), mulPt) == expected
    True
    """
    xScale, xyScale, yxScale, yScale, xOffset, yOffset = transformation
    xScale, yScale = func((xScale, yScale), factor)
    xyScale, yxScale = func((xyScale, yxScale), factor)
    xOffset, yOffset = func((xOffset, yOffset), factor)
    return (xScale, xyScale, yxScale, yScale, xOffset, yOffset)


# rounding

def _roundContours(contours, digits=None):
    """
    >>> contour = [
    ...     dict(identifier="contour 1", points=[("line", (0.55, 3.1), False, "test", "1")]),
    ...     dict(identifier="contour 1", points=[("line", (0.55, 3.1), True, "test", "1")])
    ... ]
    >>> expected = [
    ...     dict(identifier="contour 1", points=[("line", (1, 3), False, "test", "1")]),
    ...     dict(identifier="contour 1", points=[("line", (1, 3), True, "test", "1")])
    ... ]
    >>> _roundContours(contour) == expected
    True
    """
    results = []
    for contour in contours:
        contour = dict(contour)
        roundedPoints = []
        for segmentType, pt, smooth, name, identifier in contour["points"]:
            roundedPt = (_roundNumber(pt[0],digits), _roundNumber(pt[1],digits))
            roundedPoints.append((segmentType, roundedPt, smooth, name, identifier))
        contour["points"] = roundedPoints
        results.append(contour)
    return results

def _roundTransformation(transformation, digits=None):
    """
    >>> transformation = (1, 2, 3, 4, 4.99, 6.01)
    >>> expected = (1, 2, 3, 4, 5, 6)
    >>> _roundTransformation(transformation) == expected
    True
    """
    xScale, xyScale, yxScale, yScale, xOffset, yOffset = transformation
    return (xScale, xyScale, yxScale, yScale, _roundNumber(xOffset, digits), _roundNumber(yOffset, digits))

def _roundImage(image, digits=None):
    """
    >>> image = dict(fileName="foo", transformation=(1, 2, 3, 4, 4.99, 6.01), color="0,0,0,0")
    >>> expected = dict(fileName="foo", transformation=(1, 2, 3, 4, 5, 6), color="0,0,0,0")
    >>> _roundImage(image) == expected
    True
    """
    image = dict(image)
    fileName = image["fileName"]
    color = image["color"]
    transformation = _roundTransformation(image["transformation"], digits)
    return dict(fileName=fileName, transformation=transformation, color=color)

def _roundComponents(components, digits=None):
    """
    >>> components = [
    ...     dict(baseGlyph="A", transformation=(1, 2, 3, 4, 5.1, 5.99), identifier="1"),
    ... ]
    >>> expected = [
    ...     dict(baseGlyph="A", transformation=(1, 2, 3, 4, 5, 6), identifier="1")
    ... ]
    >>> _roundComponents(components) == expected
    True
    """
    result = []
    for component in components:
        component = dict(component)
        component["transformation"] = _roundTransformation(component["transformation"], digits)
        result.append(component)
    return result

def _roundAnchors(anchors, digits=None):
    """
    >>> anchors = [
    ...     dict(x=99.9, y=-100.1, name="foo", identifier="1", color="0,0,0,0")
    ... ]
    >>> expected = [
    ...     dict(x=100, y=-100, name="foo", identifier="1", color="0,0,0,0")
    ... ]
    >>> _roundAnchors(anchors) == expected
    True
    """
    result = []
    for anchor in anchors:
        anchor = dict(anchor)
        anchor["x"], anchor["y"] = _roundNumber(anchor["x"], digits), _roundNumber(anchor["y"], digits)
        result.append(anchor)
    return result


# -----
# Tests
# -----

# these are tests that don't fit elsewhere

def _setupTestGlyph():
    glyph = MathGlyph(None)
    glyph.width = 0
    glyph.height = 0
    return glyph

def _testWidth():
    """
    add
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 1
    >>> glyph2 = _setupTestGlyph()
    >>> glyph2.width = 2
    >>> glyph3 = glyph1 + glyph2
    >>> glyph3.width
    3

    sub
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 3
    >>> glyph2 = _setupTestGlyph()
    >>> glyph2.width = 2
    >>> glyph3 = glyph1 - glyph2
    >>> glyph3.width
    1

    mul
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 2
    >>> glyph2 = glyph1 * 3
    >>> glyph2.width
    6
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 2
    >>> glyph2 = glyph1 * (3, 1)
    >>> glyph2.width
    6

    div
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 7
    >>> glyph2 = glyph1 / 2
    >>> glyph2.width
    3.5
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 7
    >>> glyph2 = glyph1 / (2, 1)
    >>> glyph2.width
    3.5

    round
    -----
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.width = 6.99
    >>> glyph2 = glyph1.round()
    >>> glyph2.width
    7
    """

def _testHeight():
    """
    add
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 1
    >>> glyph2 = _setupTestGlyph()
    >>> glyph2.height = 2
    >>> glyph3 = glyph1 + glyph2
    >>> glyph3.height
    3

    sub
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 3
    >>> glyph2 = _setupTestGlyph()
    >>> glyph2.height = 2
    >>> glyph3 = glyph1 - glyph2
    >>> glyph3.height
    1

    mul
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 2
    >>> glyph2 = glyph1 * 3
    >>> glyph2.height
    6
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 2
    >>> glyph2 = glyph1 * (1, 3)
    >>> glyph2.height
    6

    div
    ---
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 7
    >>> glyph2 = glyph1 / 2
    >>> glyph2.height
    3.5
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 7
    >>> glyph2 = glyph1 / (1, 2)
    >>> glyph2.height
    3.5

    round
    -----
    >>> glyph1 = _setupTestGlyph()
    >>> glyph1.height = 6.99
    >>> glyph2 = glyph1.round()
    >>> glyph2.height
    7
    """

if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod().failed)
