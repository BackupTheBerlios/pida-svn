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

import bdb
import gtk
import sys
import os
import cPickle as pickle
import types
import sys
import linecache
import cmd
import bdb
import pdb
from repr import Repr
import os
import re
import pprint
import traceback
import marshal
import pida.gtkextra as gtkextra
import tempfile
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
        print tb
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



#! /usr/bin/python2.4

"""A Python debugger."""

# (See pdb.doc for documentation.)

# Create a custom safe Repr instance and increase its maxstring.
# The default of 30 truncates error messages too easily.
_repr = Repr()
_repr.maxstring = 200
_saferepr = _repr.repr

__all__ = ["run", "pm", "Pdb", "runeval", "runctx", "runcall", "set_trace",
           "post_mortem", "help"]

def find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % funcname)
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while 1:
        line = fp.readline()
        if line == '':
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno = lineno + 1
    fp.close()
    return answer


# Interaction prompt line will separate file and call info from code
# text using value of line_prefix string.  A newline and arrow may
# be to your liking.  You can set it once pdb is imported using the
# command "pdb.line_prefix = '\n% '".
# line_prefix = ': '    # Use this to get the old situation back
line_prefix = '\n-> '   # Probably a better default

class Pdb(pdb.Pdb):

    def __init__(self, cb):
        self.cb = cb
        pdb.Pdb.__init__(self)
        self.prompt = 'dbg> '
        #self.aliases = {}
        #self.mainpyfile = ''
        #self._wait_for_mainpyfile = 0
        # Try to load readline if it exists
        #try:
        #    import readline
        #except ImportError:
        #    pass
        # Read $HOME/.pdbrc and ./.pdbrc
        #self.rcLines = []
        #if 'HOME' in os.environ:
        #    envHome = os.environ['HOME']
        #    try:
        #        rcFile = open(os.path.join(envHome, ".pdbrc"))
        #    except IOError:
        #        pass
        #    else:
        #        for line in rcFile.readlines():
        #            self.rcLines.append(line)
        #        rcFile.close()
        #try:
        #    rcFile = open(".pdbrc")
        #except IOError:
        #    pass
        #else:
        #    for line in rcFile.readlines():
        #        self.rcLines.append(line)
        #    rcFile.close()

    #def reset(self):
    #    bdb.Bdb.reset(self)
    #    self.forget()

    #def forget(self):
    #    self.lineno = None
    #    self.stack = []
    #    self.curindex = 0
    #    self.curframe = None

    #def setup(self, f, t):
    #    self.forget()
    #    self.stack, self.curindex = self.get_stack(f, t)
    #    self.curframe = self.stack[self.curindex][0]
    #    self.execRcLines()

    # Can be executed earlier than 'setup' if desired
    def execRcLines(self):
        if self.rcLines:
            # Make local copy because of recursion
            rcLines = self.rcLines
            # executed only once
            self.rcLines = []
            for line in rcLines:
                line = line[:-1]
                if len(line) > 0 and line[0] != '#':
                    self.onecmd(line)

    # Override Bdb methods

    #def user_call(self, frame, argument_list):
    #    """This method is called when there is the remote possibility
    #    that we ever need to stop in this function."""
    #    if self._wait_for_mainpyfile:
    #        return
    #    if self.stop_here(frame):
    #        print '--Call--'
    #        self.interaction(frame, None)

    #def user_line(self, frame):
    #    """This function is called when we stop or break at this line."""
    #    if self._wait_for_mainpyfile:
    #        if (self.mainpyfile != self.canonic(frame.f_code.co_filename)
    #            or frame.f_lineno<= 0):
    #            return
    #        self._wait_for_mainpyfile = 0
    #    self.interaction(frame, None)

    #def user_return(self, frame, return_value):
    #    """This function is called when a return trap is set here."""
    #    frame.f_locals['__return__'] = return_value
    #    print '--Return--'
    #    self.interaction(frame, None)

    #def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
    #    """This function is called if an exception occurs,
    #    but only if we are to stop at or just below this level."""
    #    frame.f_locals['__exception__'] = exc_type, exc_value
    #    if type(exc_type) == type(''):
    #        exc_type_name = exc_type
    #    else: exc_type_name = exc_type.__name__
    #    print exc_type_name + ':', _saferepr(exc_value)
    #    self.interaction(frame, exc_traceback)

    # General interaction function

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        #self.print_stack_entry(self.stack[self.curindex])
        self.cb.received(self.stack, traceback)
        self.cmdloop()
        self.forget()


    def default(self, line):
        if line[:1] == '!': line = line[1:]
        locals = self.curframe.f_locals
        globals = self.curframe.f_globals
        try:
            code = compile(line + '\n', '<stdin>', 'single')
            s = cStringIO.StringIO()
            oldstdout = sys.stdout
            sys.stdout = s
            exec code in globals, locals
            sys.stdout = oldstdout
            s.seek(0)
            self.cb.evaled(line, s.read())

        except:
            t, v = sys.exc_info()[:2]
            if type(t) == type(''):
                exc_type_name = t
            else: exc_type_name = t.__name__
            print '***', exc_type_name + ':', v

    def precmd(self, line):
        """Handle alias expansion and ';;' separator."""
        if not line.strip():
            return line
        args = line.split()
        while args[0] in self.aliases:
            line = self.aliases[args[0]]
            ii = 1
            for tmpArg in args[1:]:
                line = line.replace("%" + str(ii),
                                      tmpArg)
                ii = ii + 1
            line = line.replace("%*", ' '.join(args[1:]))
            args = line.split()
        # split into ';;' separated commands
        # unless it's an alias command
        if args[0] != 'alias':
            marker = line.find(';;')
            if marker >= 0:
                # queue up everything after marker
                next = line[marker+2:].lstrip()
                self.cmdqueue.append(next)
                line = line[:marker].rstrip()
        return line

    # Command definitions, called by cmdloop()
    # The argument is the remaining string on the command line
    # Return true to exit from the command loop

    do_h = cmd.Cmd.do_help

    def do_break(self, arg, temporary = 0):
        # break [ ([filename:]lineno | function) [, "condition"] ]
        if not arg:
            if self.breaks:  # There's at least one
                print "Num Type         Disp Enb   Where"
                for bp in bdb.Breakpoint.bpbynumber:
                    if bp:
                        bp.bpprint()
            return
        # parse arguments; comma has lowest precedence
        # and cannot occur in filename
        filename = None
        lineno = None
        cond = None
        comma = arg.find(',')
        if comma > 0:
            # parse stuff after comma: "condition"
            cond = arg[comma+1:].lstrip()
            arg = arg[:comma].rstrip()
        # parse stuff before comma: [filename:]lineno | function
        colon = arg.rfind(':')
        funcname = None
        if colon >= 0:
            filename = arg[:colon].rstrip()
            f = self.lookupmodule(filename)
            if not f:
                print '*** ', repr(filename),
                print 'not found from sys.path'
                return
            else:
                filename = f
            arg = arg[colon+1:].lstrip()
            try:
                lineno = int(arg)
            except ValueError, msg:
                print '*** Bad lineno:', arg
                return
        else:
            # no colon; can be lineno or function
            try:
                lineno = int(arg)
            except ValueError:
                try:
                    func = eval(arg,
                                self.curframe.f_globals,
                                self.curframe.f_locals)
                except:
                    func = arg
                try:
                    if hasattr(func, 'im_func'):
                        func = func.im_func
                    code = func.func_code
                    #use co_name to identify the bkpt (function names
                    #could be aliased, but co_name is invariant)
                    funcname = code.co_name
                    lineno = code.co_firstlineno
                    filename = code.co_filename
                except:
                    # last thing to try
                    (ok, filename, ln) = self.lineinfo(arg)
                    if not ok:
                        print '*** The specified object',
                        print repr(arg),
                        print 'is not a function'
                        print ('or was not found '
                               'along sys.path.')
                        return
                    funcname = ok # ok contains a function name
                    lineno = int(ln)
        if not filename:
            filename = self.defaultFile()
        # Check for reasonable breakpoint
        line = self.checkline(filename, lineno)
        if line:
            # now set the break point
            err = self.set_break(filename, line, temporary, cond, funcname)
            if err: print '***', err
            else:
                bp = self.get_breaks(filename, line)[-1]
                print "Breakpoint %d at %s:%d" % (bp.number,
                                                  bp.file,
                                                  bp.line)

    # To be overridden in derived debuggers
    def defaultFile(self):
        """Produce a reasonable default."""
        filename = self.curframe.f_code.co_filename
        if filename == '<string>' and self.mainpyfile:
            filename = self.mainpyfile
        return filename

    do_b = do_break

    def do_tbreak(self, arg):
        self.do_break(arg, 1)

    def lineinfo(self, identifier):
        failed = (None, None, None)
        # Input is identifier, may be in single quotes
        idstring = identifier.split("'")
        if len(idstring) == 1:
            # not in single quotes
            id = idstring[0].strip()
        elif len(idstring) == 3:
            # quoted
            id = idstring[1].strip()
        else:
            return failed
        if id == '': return failed
        parts = id.split('.')
        # Protection for derived debuggers
        if parts[0] == 'self':
            del parts[0]
            if len(parts) == 0:
                return failed
        # Best first guess at file to look at
        fname = self.defaultFile()
        if len(parts) == 1:
            item = parts[0]
        else:
            # More than one part.
            # First is module, second is method/class
            f = self.lookupmodule(parts[0])
            if f:
                fname = f
            item = parts[1]
        answer = find_function(item, fname)
        return answer or failed

    def checkline(self, filename, lineno):
        """Check whether specified line seems to be executable.

        Return `lineno` if it is, 0 if not (e.g. a docstring, comment, blank
        line or EOF). Warning: testing is not comprehensive.
        """
        line = linecache.getline(filename, lineno)
        if not line:
            print 'End of file'
            return 0
        line = line.strip()
        # Don't allow setting breakpoint at a blank line
        if (not line or (line[0] == '#') or
             (line[:3] == '"""') or line[:3] == "'''"):
            print '*** Blank or comment'
            return 0
        return lineno

    def do_enable(self, arg):
        args = arg.split()
        for i in args:
            try:
                i = int(i)
            except ValueError:
                print 'Breakpoint index %r is not a number' % i
                continue

            if not (0 <= i < len(bdb.Breakpoint.bpbynumber)):
                print 'No breakpoint numbered', i
                continue

            bp = bdb.Breakpoint.bpbynumber[i]
            if bp:
                bp.enable()

    def do_disable(self, arg):
        args = arg.split()
        for i in args:
            try:
                i = int(i)
            except ValueError:
                print 'Breakpoint index %r is not a number' % i
                continue

            if not (0 <= i < len(bdb.Breakpoint.bpbynumber)):
                print 'No breakpoint numbered', i
                continue

            bp = bdb.Breakpoint.bpbynumber[i]
            if bp:
                bp.disable()

    def do_condition(self, arg):
        # arg is breakpoint number and condition
        args = arg.split(' ', 1)
        bpnum = int(args[0].strip())
        try:
            cond = args[1]
        except:
            cond = None
        bp = bdb.Breakpoint.bpbynumber[bpnum]
        if bp:
            bp.cond = cond
            if not cond:
                print 'Breakpoint', bpnum,
                print 'is now unconditional.'

    def do_ignore(self,arg):
        """arg is bp number followed by ignore count."""
        args = arg.split()
        bpnum = int(args[0].strip())
        try:
            count = int(args[1].strip())
        except:
            count = 0
        bp = bdb.Breakpoint.bpbynumber[bpnum]
        if bp:
            bp.ignore = count
            if count > 0:
                reply = 'Will ignore next '
                if count > 1:
                    reply = reply + '%d crossings' % count
                else:
                    reply = reply + '1 crossing'
                print reply + ' of breakpoint %d.' % bpnum
            else:
                print 'Will stop next time breakpoint',
                print bpnum, 'is reached.'

    def do_clear(self, arg):
        """Three possibilities, tried in this order:
        clear -> clear all breaks, ask for confirmation
        clear file:lineno -> clear all breaks at file:lineno
        clear bpno bpno ... -> clear breakpoints by number"""
        if not arg:
            try:
                reply = raw_input('Clear all breaks? ')
            except EOFError:
                reply = 'no'
            reply = reply.strip().lower()
            if reply in ('y', 'yes'):
                self.clear_all_breaks()
            return
        if ':' in arg:
            # Make sure it works for "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            try:
                lineno = int(arg)
            except:
                err = "Invalid line number (%s)" % arg
            else:
                err = self.clear_break(filename, lineno)
            if err: print '***', err
            return
        numberlist = arg.split()
        for i in numberlist:
            err = self.clear_bpbynumber(i)
            if err:
                print '***', err
            else:
                print 'Deleted breakpoint %s ' % (i,)
    do_cl = do_clear # 'c' is already an abbreviation for 'continue'

    def do_where(self, arg):
        self.print_stack_trace()
    do_w = do_where
    do_bt = do_where

    def do_up(self, arg):
        if self.curindex == 0:
            print '*** Oldest frame'
        else:
            self.curindex = self.curindex - 1
            self.curframe = self.stack[self.curindex][0]
            self.print_stack_entry(self.stack[self.curindex])
            self.lineno = None
    do_u = do_up

    def do_down(self, arg):
        if self.curindex + 1 == len(self.stack):
            print '*** Newest frame'
        else:
            self.curindex = self.curindex + 1
            self.curframe = self.stack[self.curindex][0]
            self.print_stack_entry(self.stack[self.curindex])
            self.lineno = None
    do_d = do_down

    def do_step(self, arg):
        self.set_step()
        return 1
    do_s = do_step

    def do_next(self, arg):
        self.set_next(self.curframe)
        return 1
    do_n = do_next

    def do_return(self, arg):
        self.set_return(self.curframe)
        return 1
    do_r = do_return

    def do_continue(self, arg):
        self.set_continue()
        return 1
    do_c = do_cont = do_continue

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
    do_j = do_jump

    def do_debug(self, arg):
        sys.settrace(None)
        globals = self.curframe.f_globals
        locals = self.curframe.f_locals
        p = Pdb()
        p.prompt = "(%s) " % self.prompt.strip()
        print "ENTERING RECURSIVE DEBUGGER"
        sys.call_tracing(p.run, (arg, globals, locals))
        print "LEAVING RECURSIVE DEBUGGER"
        sys.settrace(self.trace_dispatch)
        self.lastcmd = p.lastcmd

    def do_quit(self, arg):
        self._user_requested_quit = 1
        self.set_quit()
        return 1

    do_q = do_quit
    do_exit = do_quit

    def do_EOF(self, arg):
        print
        self._user_requested_quit = 1
        self.set_quit()
        return 1

    def do_args(self, arg):
        f = self.curframe
        co = f.f_code
        dict = f.f_locals
        n = co.co_argcount
        if co.co_flags & 4: n = n+1
        if co.co_flags & 8: n = n+1
        for i in range(n):
            name = co.co_varnames[i]
            print name, '=',
            if name in dict: print dict[name]
            else: print "*** undefined ***"
    do_a = do_args

    def do_retval(self, arg):
        if '__return__' in self.curframe.f_locals:
            print self.curframe.f_locals['__return__']
        else:
            print '*** Not yet returned!'
    do_rv = do_retval

    def _getval(self, arg):
        try:
            return eval(arg, self.curframe.f_globals,
                        self.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
            else: exc_type_name = t.__name__
            print '***', exc_type_name + ':', repr(v)
            raise

    def do_p(self, arg):
        try:
            print repr(self._getval(arg))
        except:
            pass

    def do_pp(self, arg):
        try:
            pprint.pprint(self._getval(arg))
        except:
            pass

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
    do_l = do_list

    def do_whatis(self, arg):
        try:
            value = eval(arg, self.curframe.f_globals,
                            self.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == type(''):
                exc_type_name = t
            else: exc_type_name = t.__name__
            print '***', exc_type_name + ':', repr(v)
            return
        code = None
        # Is it a function?
        try: code = value.func_code
        except: pass
        if code:
            print 'Function', code.co_name
            return
        # Is it an instance method?
        try: code = value.im_func.func_code
        except: pass
        if code:
            print 'Method', code.co_name
            return
        # None of the above...
        print type(value)

    def do_alias(self, arg):
        args = arg.split()
        if len(args) == 0:
            keys = self.aliases.keys()
            keys.sort()
            for alias in keys:
                print "%s = %s" % (alias, self.aliases[alias])
            return
        if args[0] in self.aliases and len(args) == 1:
            print "%s = %s" % (args[0], self.aliases[args[0]])
        else:
            self.aliases[args[0]] = ' '.join(args[1:])

    def do_unalias(self, arg):
        args = arg.split()
        if len(args) == 0: return
        if args[0] in self.aliases:
            del self.aliases[args[0]]

    # Print a traceback starting at the top stack frame.
    # The most recently entered frame is printed last;
    # this is different from dbx and gdb, but consistent with
    # the Python interpreter's stack trace.
    # It is also consistent with the up/down commands (which are
    # compatible with dbx and gdb: up moves towards 'main()'
    # and down moves towards the most recent stack frame).

    def print_stack_trace(self):
        try:
            for frame_lineno in self.stack:
                self.print_stack_entry(frame_lineno)
        except KeyboardInterrupt:
            pass

    def print_stack_entry(self, frame_lineno, prompt_prefix=line_prefix):
        frame, lineno = frame_lineno
        if frame is self.curframe:
            print '>',
        else:
            print ' ',
        print self.format_stack_entry(frame_lineno, prompt_prefix)


    # Help methods (derived from pdb.doc)


    def lookupmodule(self, filename):
        """Helper function for break/clear parsing -- may be overridden.

        lookupmodule() translates (possibly incomplete) file or module name
        into an absolute file name.
        """
        if os.path.isabs(filename) and  os.path.exists(filename):
            return filename
        f = os.path.join(sys.path[0], filename)
        if  os.path.exists(f) and self.canonic(f) == self.mainpyfile:
            return f
        root, ext = os.path.splitext(filename)
        if ext == '':
            filename = filename + '.py'
        if os.path.isabs(filename):
            return filename
        for dirname in sys.path:
            while os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            if os.path.exists(fullname):
                return fullname
        return None

    def _runscript(self, filename):
        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the pdb.py namespace.
        globals_ = {"__name__" : "__main__"}
        locals_ = globals_

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1
        self.mainpyfile = self.canonic(filename)
        self._user_requested_quit = 0
        statement = 'execfile( "%s")' % filename
        self.run(statement, globals=globals_, locals=locals_)

# Simplified interface

def run(statement, globals=None, locals=None):
    Pdb().run(statement, globals, locals)

def runeval(expression, globals=None, locals=None):
    return Pdb().runeval(expression, globals, locals)

def runctx(statement, globals, locals):
    # B/W compatibility
    run(statement, globals, locals)

def runcall(*args, **kwds):
    return Pdb().runcall(*args, **kwds)

def set_trace():
    Pdb().set_trace(sys._getframe().f_back)

# Post-Mortem interface

def post_mortem(t):
    p = Pdb()
    p.reset()
    while t.tb_next is not None:
        t = t.tb_next
    p.interaction(t.tb_frame, t)

def pm():
    post_mortem(sys.last_traceback)


# Main program for testing

TESTCMD = 'import x; x.main()'

def test():
    run(TESTCMD)

# print help
def help():
    for dirname in sys.path:
        fullname = os.path.join(dirname, 'pdb.doc')
        if os.path.exists(fullname):
            sts = os.system('${PAGER-more} '+fullname)
            if sts: print '*** Pager exit status:', sts
            break
    else:
        print 'Sorry, can\'t find the help file "pdb.doc"',
        print 'along the Python search path'

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
    pdb = Pdb(client)
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
