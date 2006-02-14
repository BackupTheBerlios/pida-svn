#! /bin/sh

set -e
distdir=`mktemp -d`
python setup.py build 2>&1>/dev/null
python setup.py bdist --dist-dir=$distdir --formats=egg 2>&1>/dev/null
export PYTHONPATH=$distdir/`ls $distdir`
echo built and added $PYTHONPATH to '$PYTHONPATH'
nosetests -w tests/ $*

