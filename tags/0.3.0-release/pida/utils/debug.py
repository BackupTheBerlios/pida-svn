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

import sys
import linecache

eggpath = ''	# overwritten by develop.sh
pidadir = '' # overwritten by develop.sh
leneggpath = 0

def configure_tracer( eggpath = '', pidadir = '' ):
    import pida.utils.debug as debug
    if eggpath:
        debug.eggpath = eggpath
    if pidadir:
        debug.pidadir = pidadir

    debug.leneggpath = len(debug.eggpath) + 1

def start_tracing():
    sys.settrace(tracer)

def stop_tracing():
    sys.settrace(None)

def tracer(frame, event, arg):
    def local_tracer(frame, event, arg):        
        import pida.utils.debug as debug
        if event == 'line':
            lineno = frame.f_lineno
            filename = frame.f_code.co_filename #frame.f_globals["__file__"] 
            realfile = filename
            if filename.startswith(debug.eggpath):
                filename = filename[debug.leneggpath:]
                realfile = debug.pidadir + filename
            line = linecache.getline(realfile, lineno)

            try:
                sys.stderr.write( "%s:%s: %s\n" % 
                    (filename, lineno, line.rstrip()) )
            except IOError:
                sys.stdout.write( "[STDOUT] %s:%s: %s\n" % 
                    (filename, lineno, line.rstrip()) )
    return local_tracer

