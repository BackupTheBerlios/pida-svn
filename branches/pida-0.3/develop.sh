#! /bin/sh
set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg

# build pida
echo "Building pida ..."
( cd $pidadir
  python setup.py build
  grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > data/version
  python setup.py bdist --dist-dir=$distdir --formats=egg
) 2>&1 > /dev/null

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`cat $pidadir/data/version`
egg="$distdir/pida-${version//-/_}-py$pyver.egg"

echo "Adding ${egg#$pidadir/} to '\$PYTHONPATH' ..."
export PYTHONPATH=$egg:$PYTHONPATH

DEBUG= REMOTE= GDB=
while [ $# -gt 0 ]; do
    case "$1" in
        -remote) REMOTE=1 ;;
        -debug)  DEBUG=1 ;;
        -gdb)    GDB=1 ;;
        *)       break ;;
    esac
    shift
done

[ -z "$DEBUG" ] || export PIDA_DEBUG=1

if [ "$REMOTE" ]; then
    pidacmd="$pidadir/pida/utils/pida-remote.py $* &"
else
    pidacmd="$pidadir/scripts/pida $*"
fi
echo "Running $pidacmd ..."
if [ "$GDB" ]; then
    echo "run $pidacmd" | exec gdb python -x /dev/stdin
else
    eval exec "python $pidacmd"
fi
