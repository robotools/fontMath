#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup

try:
    import robofab
except ImportError:
    print("*** Warning: fontMath requires RoboFab, see:")
    print("    robofab.com")


setup(name="fontMath",
    version="0.2",
    description="A set of objects for performing math operations on font data.",
    author="Tal Leming",
    author_email="tal@typesupply.com",
    url="https://github.com/typesupply/fontMath",
    license="MIT",
    packages=["fontMath"],
    package_dir={"":"Lib"}
)
