#!/usr/bin/env python
# coding: UTF-8


from distutils.core import setup

setup(
    name         = 'odlpet',
    version      = '0.1',
    description  = 'ODL Pet',
    author = 'Olivier Verdier',
    packages=['odlpet',
              'odlpet.scanner',
              'odlpet.stir',
              'odlpet.utils',
    ],
    classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Mathematics',
    ],
    )
