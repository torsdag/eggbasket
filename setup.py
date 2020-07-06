# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test

import os
import sys

if sys.version_info < (3, 6):
    sys.exit("python < 3.6 is not supported")

version_path = os.path.join(
    os.path.dirname(__file__), "source", "eggbasket", "_version.py",
)

with open(version_path) as version_file:
    env = {}
    exec(version_file.read(), env)
    VERSION = env["__version__"]

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

SOURCE_PATH = os.path.join(ROOT_PATH, "source")

setup(
    name="eggbasket",
    version=VERSION,
    packages=find_packages(SOURCE_PATH),
    author="Eric Hermelin",
    author_email="eric.hermelin@gmail.com",
    python_requires=">3.6",
    entry_points={"console_scripts": ["eggbasket=eggbasket.__main__:main",],},
    install_requires=[
        "mitmproxy==5.1.1",
        "prometheus-client==0.8.0",
        "dataclasses>=0.7",
    ],
    package_dir={"": "source",},
)
