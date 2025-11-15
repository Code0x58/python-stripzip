|PyPi Package| |Build Status| |Codacy Rating| |Coverage Report|

python-stripzip
===============

This package provides a ``stripzip`` script which will set all of the
date/times in given zips to *1980-01-01 00:00:00* - the lowest valid
value available in zips.

The purpose is to zip archive based builds deterministic, e.g. python wheels,
AWS lambdas. There are no extra dependancies, and the package is available
on `PyPi <https://pypi.org/project/python-stripzip/>`__ which is probably the
only advantage of this at the moment.

    usage: stripzip [-h] zip [zip ...]

Installation
------------
You can pick one of::

    pipsi install python-stripzip
    pip install --user python-stripzip
    git clone git@github.com:Code0x58/python-stripzip.git && cd python-stripzip && python setup.py install

See also
--------

* `strip-nodeterminism <https://reproducible-builds.org/tools/>`__ - tool written in Perl and released as a Debian package; works on various archive formats
* `stripzip <https://github.com/KittyHawkCorp/stripzip/>`__ - tool written in C without binary releases; currently wipes out more zip metadata
* ``SOURCE_DATE_EPOCH=315532800 python setup.py bdist_wheel``

.. |Build Status| image:: https://github.com/Code0x58/python-stripzip/actions/workflows/ci.yml/badge.svg?branch=master
   :target: https://github.com/Code0x58/python-stripzip/actions/workflows/ci.yml
.. |Codacy Rating| image:: https://api.codacy.com/project/badge/Grade/7468a12faccb4c1497575d607b097ec6
   :target: https://www.codacy.com/app/evilumbrella-github/python-stripzip?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Code0x58/python-stripzip&amp;utm_campaign=Badge_Grade
.. |PyPi Package| image:: https://badge.fury.io/py/python-stripzip.svg
   :target: https://pypi.org/project/python-stripzip/
.. |Coverage Report| image:: https://codecov.io/gh/Code0x58/python-stripzip/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Code0x58/python-stripzip