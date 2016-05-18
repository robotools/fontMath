#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

try:
    import ufoLib
except:
    print("*** Warning: fontMath requires ufoLib, see:")
    print("    github.com/unified-font-object/ufoLib")


setup(
    name="fontMath",
    version="0.2",
    description="A set of objects for performing math operations on font data.",
    author="Tal Leming",
    author_email="tal@typesupply.com",
    url="http://code.typesupply.com",
    license="MIT",
    packages=["fontMath"],
    package_dir={"":"Lib"}
)
