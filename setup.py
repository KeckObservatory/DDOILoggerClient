# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.

from setuptools import setup, find_packages

# Get some values from the setup.cfg

from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items("metadata"))
options = dict(conf.items("options"))

NAME = 'ddoiloggerclient'
VERSION = 'dev@0.0.1'
RELEASE = 'dev' not in VERSION
AUTHOR = metadata["author"]
AUTHOR_EMAIL = metadata["author_email"]
LICENSE = metadata["license"]
DESCRIPTION = metadata["description"]

scripts = []

# Define entry points for command-line scripts
entry_points = {
    'console_scripts': []
    }

setup(name=NAME,
      provides=NAME,
      version=VERSION,
      license=LICENSE,
      description=DESCRIPTION,
      long_description=open('README.rst').read(),
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      packages=find_packages(),
      package_data={'ddoiloggerclient': ['configs/*.cfg']},
      scripts=scripts,
      entry_points=entry_points,
      install_requires=[],
      python_requires=">=3.5"
      )