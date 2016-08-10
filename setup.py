#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='3R4',
    version='0.1.0-alpha',
    description='3R4 game shell',
    author='Jeremy Lucas',
    author_email='jeremyalucas@gmail.com',
    url='https://github.com/jerluc/3R4',
    packages=['era'],
    entry_points={
        'console_scripts': ['3R4=era.__main__:main'],
    },
    install_requires=[l.strip() for l in open('requirements.txt')],
    license='License :: OSI Approved :: Apache Software License',
)
