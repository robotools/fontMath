import unittest

from fontMath.mathDict import MathDict

class MathDictTest(unittest.TestCase):

    def test_add(self):
        omd1 = MathDict(a=1, b=2, c=3)
        omd2 = MathDict(a=10, b=20, c=30)
        omd3 = omd1 + omd2
        self.assertEqual(omd3, MathDict([('a', 11), ('b', 22), ('c', 33)]))

    def test_sub(self):
        omd1 = MathDict(a=1, b=2, c=3)
        omd2 = MathDict(a=10, b=20, c=30)
        omd3 = omd1 - omd2
        self.assertEqual(omd3, MathDict([('a', -9), ('b', -18), ('c', -27)]))

    def test_mul(self):
        omd1 = MathDict(a=1, b=2, c=3)
        omd2 = omd1 * 100
        self.assertEqual(omd2, MathDict([('a', 100), ('b', 200), ('c', 300)]))

    def test_div(self):
        omd1 = MathDict(a=1, b=2, c=3)
        omd2 = omd1 / 5
        self.assertEqual(omd2, MathDict([('a', 0.2), ('b', 0.4), ('c', 0.6)]))
        triedZeroDivision = False
        try:
            omd3 = omd1 / 0
        except ZeroDivisionError:
            triedZeroDivision = True
        self.assertEqual(triedZeroDivision, True)



if __name__ == "__main__":
    unittest.main()
