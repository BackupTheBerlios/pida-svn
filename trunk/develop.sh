#!/bin/sh
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg

DEBUG= REMOTE= GDB= PROFILE= PDB= UPDATE=
while [ $# -gt 0 ]; do
    case "$1" in
	-update) UPDATE=1 ;;
        -remote) REMOTE=1 ;;
        -debug)  DEBUG=1 ;;
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
else
    echo "ERROR: python setup.py failed, log will follow"
    mv $pidadir/buildlog.$$ $pidadir/buildlog.log
    sed -e 's,^,  ,' $pidadir/buildlog.log
    echo "ERROR: END"
    exit 1
fi

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`cat $pidadir/data/version`
eggpath=$( echo build/bdist.`uname -s`-`uname -m`/egg | tr A-Z a-z )
egg="$distdir/pida-${version//-/_}-py$pyver.egg"

echo "Adding ${egg#$pidadir/} to '\$PYTHONPATH' ..."
export PYTHONPATH=$egg:$PYTHONPATH

[ -z "$DEBUG" ] || export PIDA_DEBUG=1

pidacmd=$distdir/pida
tmpfile=$pidacmd.$$
if [ "$REMOTE" ]; then
    if [ $# -gt 0 ]; then
        file="$1"; shift
        [ "${file:0:1}" == "/" ] || file="$PWD/$file"
    else
        file=
    fi
    pidacmd="$pidadir/pida/utils/pida-remote.py $file $* &"
elif [ "$PDB" ]; then
    cat<<EOT > $tmpfile
import pdb
pdb.set_trace()
import pida.core.application as application
application.main()
EOT
    mv $tmpfile $pidacmd
    pidacmd="$pidacmd $*"
else
    cat<<EOT > $tmpfile
import pida.core.application as application
import pida.utils.debug as debug

debug.configure_tracer( eggpath="$eggpath", pidadir = "$pidadir/" )
EOT
    if [ "$PROFILE" ]; then
        cat<<EOT
import profile
profile.run('application.main()')
EOT
    else
        cat<<EOT
application.main()
EOT
    fi >> $tmpfile
    mv $tmpfile $pidacmd
    pidacmd="$pidacmd $*"
fi

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
