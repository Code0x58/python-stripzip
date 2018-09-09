import codecs
from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    author="Oliver Bristow",
    author_email="github+pypi@oliverbristow.co.uk",
    description="strip zip timestamps for reproducible builds",
    entry_points={"console_scripts": ["stripzip = stripzip:cli"]},
    keywords="zipfile reproducible-builds",
    platforms=["any"],
    license="MIT",
    long_description=long_description,
    name="python-stripzip",
    py_modules=["stripzip"],
    setup_requires=["setuptools_scm", "wheel"],
    url="https://github.com/Code0x58/python-stripzip/",
    use_scm_version=True,
)
