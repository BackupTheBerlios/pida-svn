#!/bin/bash
set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg

# build pida
echo "Building pida ..."
( cd $pidadir
  python setup.py rotate --dist-dir=$distdir --match=.egg --keep=3
  python setup.py build
  grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > data/version
  python setup.py bdist --dist-dir=$distdir --formats=egg
) 2>&1 > /dev/null

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`cat $pidadir/data/version`
eggpath='build/bdist.linux-i686/egg'
egg="$distdir/pida-${version//-/_}-py$pyver.egg"

echo "Adding ${egg#$pidadir/} to '\$PYTHONPATH' ..."
export PYTHONPATH=$egg:$PYTHONPATH

DEBUG= REMOTE= GDB= PROFILE= PDB= TRACE=
while [ $# -gt 0 ]; do
    case "$1" in
        -remote) REMOTE=1 ;;
        -debug)  DEBUG=1 ;;
        -gdb)    GDB=1 ;;
        -pdb)    PDB=1 ;;
        -trace)  TRACE=1 ;;
        -profile) PROFILE=1 ;;
        *)       break ;;
    esac
    shift
done

[ -z "$DEBUG" ] || export PIDA_DEBUG=1

if [ "$REMOTE" ]; then
    pidacmd="$pidadir/pida/utils/pida-remote.py $* &"
elif [ "$PDB" ]; then
    pidacmd=$distdir/pida
    cat<<EOT >> $pidacmd.$$
import pdb
pdb.set_trace()
import pida.core.application as application
application.main()
EOT
    mv $pidacmd.$$ $pidacmd
    pidacmd="$pidacmd $*"
elif [ "$TRACE" ]; then
    pidacmd=$distdir/pida
    cat<<EOT >> $pidacmd.$$
import sys
import linecache

eggpath = "$eggpath"
leneggpath = len(eggpath) + 1

def tracer(frame, event, arg):
    def local_tracer(frame, event, arg):        
        if event == 'line':
	    lineno = frame.f_lineno
	    filename = frame.f_code.co_filename #frame.f_globals["__file__"] 
	    if filename.startswith(eggpath):
	    	filename = filename[leneggpath:]
	    line = linecache.getline(filename, lineno)
            print "%s:%s: %s" % (filename, lineno, line.rstrip())
    return local_tracer

import pida.core.application as application
sys.settrace(tracer)
application.main()
EOT
    mv $pidacmd.$$ $pidacmd
    pidacmd="$pidacmd $*"
elif [ -z "$PROFILE" ]; then
    pidacmd="$pidadir/scripts/pida $*"
else
    pidacmd=$distdir/pida
    cat<<EOT >> $pidacmd.$$
import profile
import pida.core.application as application
profile.run('application.main()')
EOT
    mv $pidacmd.$$ $pidacmd
    pidacmd="$pidacmd $*"
fi

echo "Running $pidacmd ..."
if [ "$GDB" ]; then
    exec gdb python -q -x <( echo "run $pidacmd" )
else
    eval exec "python $pidacmd"
fi
