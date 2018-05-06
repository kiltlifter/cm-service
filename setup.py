# -*- coding: utf-8 -*-

from distutils.core import setup

__author__ = "Sean Douglas"
__version__ = "0.1.0"
__license__ = "MIT"

setup(
    name='CMService',
    version=__version__,
    author='Sean Douglas',
    author_email='seancdouglas@gmail.com',
    packages=['cm-service'],
    url='',
    license='LICENSE.txt',
    description='Tool to extract useful info from RHEL base systems.',
    long_description=open('README.md').read(),
    install_requires=[
        "flask >= 0.12.2",
        "flask-restplus >= 0.10.1",
    ],
)

