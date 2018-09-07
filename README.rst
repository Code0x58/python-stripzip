`PyPi <https://pypi.org/project/python-stripzip/>`__

python-stripzip
=========

This package provides a ``stripzip`` script which will set all of the
date/times in given zips to *1980-01-01 00:00:00* - the lowest valid
value available in zips.

The purpose is to zip archive based builds deterministic, e.g. python wheels,
AWS lambdas.

    usage: stripzip [-h] zip [zip ...]

See also
--------

* `strip-nodeterminism <https://reproducible-builds.org/tools/>`__ - tool written in Perl and released as a Debian package; works on various archive formats
* `stripzip <https://github.com/KittyHawkCorp/stripzip/>`__ - tool written in C without binary releases; currently wipes out more zip metadata
