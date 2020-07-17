import os
import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent


# The text of the README file
README = (HERE / "README.md").read_text()

# Get version
version = ""
with open(os.path.join(HERE, "two_phase", "__init__.py")) as f:
    for line in f.readlines():
        if "__version__" in line:
            version = line
version = version.split("=")[1].strip().replace('"', "")

# This call to setup() does all the work
setup(
    name="two-phase",
    version="0.1.0",
    description="A simple and easy-to-use two-phase flow library.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/felipecastrotc/two-phase",
    author="Felipe de Castro Teixeira Carvalho",
    author_email="felipecastrotc@protonmail.ch",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
    ],
    packages=["two_phase"],
    include_package_data=True,
    install_requires=["CoolProp", "numpy"],
)
