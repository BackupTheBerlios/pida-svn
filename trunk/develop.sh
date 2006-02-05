#!/bin/sh
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg
tmpdir=$pidadir/build/tmp
mkdir -p $pidadir/build/{egg,tmp}

REMOTE= GDB= PROFILE= PDB= UPDATE=
while [ $# -gt 0 ]; do
    case "$1" in
        -update) UPDATE=1 ;;
        -remote) REMOTE=1 ;;
        -gdb)    GDB=1 ;;
        -pdb)    PDB=1 ;;
        -profile) PROFILE=1 ;;
        *)       break ;;
    esac
    shift
done

if [ "$UPDATE" ]; then
	echo "Updating pida ..."
	svn up $pidadir || true
fi

# build pida
echo "Building pida ..."
if ( cd $pidadir; {
    touch data/version
    python setup.py rotate --dist-dir=$distdir --match=.egg --keep=3 &&
    python setup.py build &&
    grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > data/version &&
    python setup.py bdist --dist-dir=$distdir --formats=egg
    } 2>&1 ) > $pidadir/buildlog.$$; then
    rm $pidadir/buildlog.$$
elif zenity --text-info --title="I'm sorry, python setup.py failed :-(" \
        --width=400 \
        --filename="$pidadir/buildlog.$$" 2> /dev/null; then
    true
else
    echo "ERROR: python setup.py failed, log will follow"
    sed -e 's,^,  ,' $pidadir/buildlog.$$
    echo "ERROR: END"
fi

if [ -f $pidadir/buildlog.$$ ]; then
    mv $pidadir/buildlog.$$ $pidadir/buildlog.log
    exit 1
fi

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`cat $pidadir/data/version`
eggpath=$( echo build/bdist.`uname -s`-`uname -m`/egg | tr A-Z a-z )
egg="$distdir/pida-${version//-/_}-py$pyver.egg"

echo "Adding ${egg#$pidadir/} to '\$PYTHONPATH' ..."
export PYTHONPATH=$egg:$PYTHONPATH

pidacmd=$tmpdir/pida
tmpfile=$pidacmd.$$

if [ "$REMOTE" ]; then
    echo "import pida.utils.pidaremote as pidaremote"
    echo "pidaremote.main()"
else
    echo "from pkg_resources import load_entry_point"

    if [ "$PDB" ]; then
        echo "import pdb"
        echo "pdb.set_trace()"
    else
        echo "import pida.utils.debug as debug"
        echo "debug.configure_tracer( eggpath='$eggpath', pidadir='$pidadir/' )"
    fi

    echo "entry_point=load_entry_point('pida', 'console_scripts', 'pida')"

    if [ "$PROFILE" ]; then
        echo "import profile"
        echo "profile.run('entry_point()')"
    else
        echo "import sys"
        echo "sys.exit( entry_point() )"
    fi
fi > $tmpfile
mv $tmpfile $pidacmd
pidacmd="$pidacmd $*"

echo "Running $pidacmd ..."
if [ "$GDB" ]; then
    echo "run $pidacmd" > $tmpfile
    gdb python -q -x $tmpfile
    wait
    errno=$?
    rm $tmpfile
    exit $errno
else
    eval exec "python $pidacmd"
fi
