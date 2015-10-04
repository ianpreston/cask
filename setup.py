#!/usr/bin/env python
from setuptools import setup

setup(
    name='cask',
    version='0.0.0',
    description='Linux container manager',
    author='Ian Preston',
    url='https://github.com/ianpreston/cask',
    install_requires=[
        'click==5.1',
    ],
    package_dir={
        '': 'src',
    },
    packages=['libcask'],
    scripts=['src/scripts/cask'],
)
