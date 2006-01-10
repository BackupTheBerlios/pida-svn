#!/bin/bash
set -e

me=$(readlink -f $0)
pidadir=${me%/*}
distdir=$pidadir/build/egg

DEBUG= REMOTE= GDB= PROFILE= PDB= TRACE= UPDATE=
while [ $# -gt 0 ]; do
    case "$1" in
	-update) UPDATE=1 ;;
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

if [ "$UPDATE" ]; then
	echo "Updating pida ..."
	svn up $pidadir || true
fi

generate_pida_initpy() {
	cat <<EOT
# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

EOT
	echo -n '__AUTHORS__ = ['
	sed -ne 's|^\(.*\) <\(.*\)>\(.*\)$|\t( "\1", "\2", "\3"),|p' \
		$pidadir/AUTHORS
	echo -e '\t]'
}

# build pida
echo "Building pida ..."
( cd $pidadir
  python setup.py rotate --dist-dir=$distdir --match=.egg --keep=3
  generate_pida_initpy | sed -e 's,^\t,    ,g' -e 's,\t, ,g' > pida/__init__.py
  python setup.py build
  grep '^Version:' pida.egg-info/PKG-INFO | cut -d' ' -f2- > data/version
  python setup.py bdist --dist-dir=$distdir --formats=egg
) 2>&1 > /dev/null

pyver=`python -V 2>&1 | cut -d' ' -f2 | cut -c1-3`
version=`cat $pidadir/data/version`
eggpath=$( echo build/bdist.`uname -s`-`uname -m`/egg | tr A-Z a-z )
egg="$distdir/pida-${version//-/_}-py$pyver.egg"

echo "Adding ${egg#$pidadir/} to '\$PYTHONPATH' ..."
export PYTHONPATH=$egg:$PYTHONPATH

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
pidadir = "$pidadir/"
leneggpath = len(eggpath) + 1

def tracer(frame, event, arg):
    def local_tracer(frame, event, arg):        
        if event == 'line':
	    lineno = frame.f_lineno
	    filename = frame.f_code.co_filename #frame.f_globals["__file__"] 
	    realfile = filename
	    if filename.startswith(eggpath):
	    	filename = filename[leneggpath:]
		realfile = pidadir + filename
            line = linecache.getline(realfile, lineno)
            sys.stderr.write( "%s:%s: %s\n" % (filename, lineno, line.rstrip()) )
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
