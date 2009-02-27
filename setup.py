#!/usr/bin/env python

from distutils.core import setup

try:
    import robofab
except:
    print "*** Warning: defcon requires RoboFab, see:"
    print "    robofab.com"


setup(name="fontMath",
    version="0.2",
    description="A set of objects for performing math operations on font data.",
    author="Tal Leming",
    author_email="tal@typesupply.com",
    url="http://code.typesupply.com",
    license="MIT",
    packages=["fontMath"],
    package_dir={"":"Lib"}
)