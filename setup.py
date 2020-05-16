import codecs
from os import path
from textwrap import dedent

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

TESTS_REQUIRE = ["pytest~=5.4.2", "pytest-cov~=2.8.1"]

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
    install_requires=[],
    tests_require=TESTS_REQUIRE,
    extras={"test": TESTS_REQUIRE},
    url="https://github.com/Code0x58/python-stripzip/",
    use_scm_version=True,
    classifiers=dedent(
        """
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Topic :: Software Development
        Topic :: System :: Archiving :: Packaging
        License :: OSI Approved :: MIT License
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: 3.8
        Programming Language :: Python :: 3.9
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
    """
    )
    .strip()
    .split("\n"),
)
