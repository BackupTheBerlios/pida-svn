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

# Copied from the bdb, pdb, Idle and eric3 debuggers

import gtk
import os
import cPickle as pickle
import types
import sys
import linecache
import pdb
import traceback
import pida.gtkextra as gtkextra
import cStringIO

class Debugger(object):
    def __init__(self, sid):
        self.ipc = gtkextra.IPWindow(self)
        self.ipc.reset(long(sid))
        self.ipc.connect()
    
    def loop(self):
        while gtk.gdk.events_pending():
            gtk.main_iteration()
        

    def evaled(self, line, s):
        self.ipc.write('eval', '%s\n%s' % (line, s), 8)
        self.loop()

    def received(self, stack, tb):
        s = self.format_stack(stack)
        self.ipc.write('stack', s, 8)
        self.loop()
        #self.ipc.write('frame', [self.pdb.curindex], 32)

    def listed(self, L):
        self.ipc.write('list', ''.join(L), 8)
        self.loop()

    def started(self):
        self.ipc.write('started', [1], 32)
        self.loop()
    
    def format_stack(self, stack):
        return pickle.dumps([self.format_stack_entry(f) for f in stack])

    def format_stack_entry(self, frame_lineno, lprefix=': '):
        import linecache, repr
        frame, lineno = frame_lineno
        filename = self.pdb.canonic(frame.f_code.co_filename)
        L = [filename, lineno]
        if frame.f_code.co_name:
             L.append(frame.f_code.co_name)
        else:
            L.append("<lambda>")
        if '__args__' in frame.f_locals:
            L.append(repr.repr(frame.f_locals['__args__']))
        else:
            L.append([])
        if '__return__' in frame.f_locals:
            rv = frame.f_locals['__return__']
            L.append(repr.repr(rv))
        else:
            L.append(None)
        line = linecache.getline(filename, lineno)
        if line:
            L.append(line.strip())
        else:
            L.append('')
        L.append(self.format_namespace(frame.f_locals))
        L.append(self.format_namespace(frame.f_globals))
        return L

    def format_namespace(self, nsdict):
        #return nsdict
        L = []
        ks = nsdict.keys()
        for k in ks:
            typ = type(nsdict[k])
            v = ''
            if typ in [int, str, long, float]:
                v = '%r' % (nsdict[k])
            else:
                v = typ.__name__
            L.append((k, v))
        #print L
        return L


class Pidadb(pdb.Pdb):

    def __init__(self, cb):
        self.cb = cb
        pdb.Pdb.__init__(self)
        self.prompt = 'dbg> '

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.cb.received(self.stack, traceback)
        self.cmdloop()
        self.forget()

    def default(self, line):
        s = cStringIO.StringIO()
        oldstdout = sys.stdout
        sys.stdout = s
        pdb.Pdb.default(self, line)
        sys.stdout = oldstdout
        s.seek(0)
        self.cb.evaled(line.strip(), s.read())

    def do_jump(self, arg):
        if self.curindex + 1 != len(self.stack):
            print "*** You can only jump within the bottom frame"
            return
        try:
            arg = int(arg)
        except ValueError:
            print "*** The 'jump' command requires a line number."
        else:
            try:
                # Do the jump, fix up our copy of the stack, and display the
                # new position
                self.curframe.f_lineno = arg
                self.stack[self.curindex] = self.stack[self.curindex][0], arg
                self.print_stack_entry(self.stack[self.curindex])
            except ValueError, e:
                print '*** Jump failed:', e

    def do_list(self, arg):
        self.lastcmd = 'list'
        last = None
        if arg:
            try:
                x = eval(arg, {}, {})
                if type(x) == type(()):
                    first, last = x
                    first = int(first)
                    last = int(last)
                    if last < first:
                        # Assume it's a count
                        last = first + last
                else:
                    first = max(1, int(x) - 5)
            except:
                print '*** Error in argument:', repr(arg)
                return
        elif self.lineno is None:
            first = max(1, self.curframe.f_lineno - 5)
        else:
            first = self.lineno + 1
        if last is None:
            last = first + 10
        filename = self.curframe.f_code.co_filename
        breaklist = self.get_file_breaks(filename)
        try:
            L = []
            for lineno in range(first, last+1):
                line = linecache.getline(filename, lineno)
                if not line:
                    print '[EOF]'
                    break
                else:
                    s = repr(lineno).rjust(3)
                    if len(s) < 4: s = s + ' '
                    if lineno in breaklist: s = s + 'B'
                    else: s = s + ' '
                    if lineno == self.curframe.f_lineno:
                        s = s + '->'
                    else:
                        s = s + '  '
                    s = s + '  ' + line
                    L.append(s)
                    #print s
                    self.lineno = lineno
            self.cb.listed(L)
        except KeyboardInterrupt:
            pass



def main():
    if not sys.argv[1:]:
        print "usage: pdb.py scriptfile [arg] ..."
        sys.exit(2)
    mainpyfile =  sys.argv[1]     # Get script filename
    if not os.path.exists(mainpyfile):
        print 'Error:', mainpyfile, 'does not exist'
        sys.exit(1)

    sid = sys.argv[2]
    #del sys.argv[0]         # Hide "pdb.py" from argument list

    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(mainpyfile)

    # Note on saving/restoring sys.argv: it's a good idea when sys.argv was
    # modified by the script being debugged. It's a bad idea when it was
    # changed by the user from the command line. The best approach would be to
    # have a "restart" command which would allow explicit specification of
    # command line arguments.
    client = Debugger(sid)
    pdb = Pidadb(client)
    client.pdb = pdb
    client.started()
    while 1:
        try:
            pdb._runscript(mainpyfile)
            if pdb._user_requested_quit:
                break
            print "The program finished and will be restarted"
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            print "The program exited via sys.exit(). Exit status: ",
            print sys.exc_info()[1]
        except:
            traceback.print_exc()
            print "Uncaught exception. Entering post mortem debugging"
            print "Running 'cont' or 'step' will restart the program"
            t = sys.exc_info()[2]
            while t.tb_next is not None:
                t = t.tb_next
            pdb.interaction(t.tb_frame,t)
            print "Post mortem debugger finished. The "+mainpyfile+" will be restarted"


# When invoked as main program, invoke the debugger on a script
if __name__=='__main__':
    main()
