#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="sol-ophyd",
    version="0.0.1",
    description="Simulated devices abstraction",
    long_description=readme(),
    author="Hugo Campos",
    author_email="hugo.campos@lnls.br",
    url="https://gitlab.cnpem.br/SOL/bluesky/sol_ophyd",
    install_requires=[
        "ophyd",
    ],
    package_data={},
    include_package_data=True,
    packages=find_packages(where=".", exclude=["test", "test.*", "tests"]),
)
