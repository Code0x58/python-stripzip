import codecs
from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, "README.rst"), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="python-stripzip",
    use_scm_version=True,
    setup_requires=["setuptools_scm", "wheel"],
    entry_points={"console_scripts": ["stripzip = stripzip:cli"]},
    py_modules=["stripzip"],
    keywords='zipfile reproducible-builds',
    url='https://github.com/Code0x58/python-stripzip/',
    author="Oliver Bristow",
    author_email='github+pypi@oliverbristow.co.uk',
    long_description=long_description,
)
