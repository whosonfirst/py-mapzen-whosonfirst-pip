#!/usr/bin/env python
from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),

setup(
    name='mapzen.whosonfirst.pip',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.pip'],
    version='0.1',
    description='Simple Python wrapper for talking to the go-whosonfirst-pip server',
    author='Mapzen',
    url='https://github.com/mapzen/py-mapzen-whosonfirst-pip',
    install_requires=[
        'requests',
        ],
    dependency_links=[
        ],
    packages=packages,
    scripts=[
        ],
    download_url='https://github.com/mapzen/py-mapzen-whosonfirst-pip/releases/tag/v0.1',
    license='BSD')
