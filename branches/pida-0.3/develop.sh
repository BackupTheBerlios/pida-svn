#! /bin/sh
set -e

me=$(readlink -f $0); cd ${me%/*}
distdir=$PWD/build/egg
python setup.py build 2>&1>/dev/null
python setup.py bdist --dist-dir=$distdir --formats=egg 2>&1>/dev/null

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2-`
egg="$distdir/pida-$version-py$pyver.egg"
export PYTHONPATH=$egg:$PYTHONPATH
echo "built and added $egg to '\$PYTHONPATH'"
exec python scripts/pida "$@"
