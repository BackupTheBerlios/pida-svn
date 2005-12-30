#! /bin/sh
set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg

# build pida
( cd $pidadir
python setup.py build 2>&1>/dev/null
python setup.py bdist --dist-dir=$distdir --formats=egg 2>&1>/dev/null
)

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`grep '^Version:' $pidadir/pida.egg-info/PKG-INFO | cut -d' ' -f2-`
egg="$distdir/pida-$version-py$pyver.egg"
export PYTHONPATH=$egg:$PYTHONPATH
echo "built and added $egg to '\$PYTHONPATH'"

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

if [ "$GDB" ]; then
    echo "run $pidacmd" | exec gdb python -x /dev/stdin
else
    eval exec "python $pidacmd"
fi
