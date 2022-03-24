import os
import re

from setuptools import setup, find_packages


def get_version(path):
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as fp:
        matches = re.search(
            r'^__VERSION__ = [\'"]([^\'"]*)[\'"]',
            fp.read(),
            re.M)
    if matches:
        return matches.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='TextRig',
    version=get_version(os.path.join('textrig', '__init__.py')),
    url='https://github.com/VedaWebPlatform/TextRig',
    author='Börge Kiss',
    author_email='b.kiss@uni-koeln.de',
    maintainer='Börge Kiss',
    maintainer_email='b.kiss@uni-koeln.de',
    description='An open and collaborative text research platform',
    packages=find_packages(include=['textrig', 'textrig.*'])
)