

import plugin
import gtk
import os
import pickle
import tree
import gobject
import tempfile

import gtkipc
import linecache
import marshal

def script_directory():
    def f(): pass
    d, f = os.path.split(f.func_code.co_filename)
    return d

SCRIPT_DIR = script_directory()

class StackTree(tree.Tree):
    COLUMNS = [('display', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup'),
               ('frame', gobject.TYPE_PYOBJECT, None, False, None)]

    def init(self):
        pass
        #self.fv = FrameViewer()
        #self.toolbar.pack_start(self.fv)
        
    #def l_cb_selected(self, tv):
        #self.fv.refresh_label(self.selected(1))

    def populate(self, stack, curindex):
        self.clear()
        last = None
        for fr in stack:
            if not fr.filename.count('bdb.py') and fr.filename != '<string>':
                last = self.add_item([fr.markup(), fr])
        if last:
            path = self.model.get_path(last)
            self.view.set_cursor(path)

class BreakTree(tree.Tree):
    COLUMNS = [('display', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup'),
               ('filename', gobject.TYPE_STRING, None, False, None),
               ('line', gobject.TYPE_STRING, None, False, None)]

    def init(self):
        self.title = gtk.Label()
        self.toolbar.pack_start(self.title)
        self.refresh_label()

    def refresh_label(self):
        self.title.set_markup('Breakpoints')

    def add(self, filename, line):
        mu = self.markup(filename, line)
        self.add_item([mu, filename, line])

    def get_list(self):
        for row in self.model:
            # not allowed to slice row sequences
            yield [row[1], row[2]]

    def markup(self, filename, line):
        return '%s\n%s' % (filename, line)

def bframe(frame):
    c = frame.f_code
    return '%s %s %s %s %s' % (c.co_name,
        c.co_argcount, c.co_names, c.co_filename, c.co_firstlineno)

class VarTree(tree.Tree):
    COLUMNS = [('display', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup'),
               ('dispval', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup'),
               ('name', gobject.TYPE_STRING, None, False, None),
               ('value', gobject.TYPE_STRING, None, False, None)]

    def populate(self, varlist):
        self.clear()
        varlist.sort()
        for n, v in varlist:
            self.add_item(self.markup(n, v) + [n, v])

    def markup(self, name, value):
        MUN = '<span size="small"><b>%s</b></span>'
        MUV = '<span size="small">%s</span>'
        return [(MUN % name), (MUV % value)]

from cgi import escape

class PidaFrame(object):
    def __init__(self, fn, lineno, name, args, ret, line, locs, globs=None):
        self.filename = fn
        self.lineno = lineno
        self.name = name
        self.args = args
        self.line = line
        self.ret = ret
        self.locs = locs
        self.globs = globs

    def markup(self):
        t = ('<span size="small">%s\n'
            '%s (%s)\n<b>%s(</b>%s<b>)</b> &gt; %s\n<tt>%s</tt></span>')
        dirn, filen = os.path.split(self.filename)
        
        return t % tuple([escape('%s' % s) for s in [dirn, filen, self.lineno,
                                        self.name, ', '.join(self.args),
                                        self.ret, self.line]])

class FrameViewer(gtk.Label):
    MU = ('<span size="small">'
               '<b>%s</b>'
               ' (<span color="#0000c0">%s</span>)\n'
               '%s\n<tt>%s</tt></span>')

    def refresh_label(self, fr):
        return
        dn, fn = os.path.split(fr['filename'])
        mu = self.MU % (fn, fr['line'], dn, fr['so'])
        self.set_markup(mu)

import vte

class DebugTerminal(vte.Terminal):

    def __init__(self, cb):
        self.cb = cb
        self.pid = None
        vte.Terminal.__init__(self)
        self.set_size_request(-1, 50)

    def kill(self):
        if self.pid:
            try:
                os.kill(self.pid, 15)
            except OSError:
                try:
                    os.kill(self.pid, 15)
                except OSError:
                    pass

    def start(self, xid, fn):
        self.kill()
        
        sn = os.path.join(SCRIPT_DIR, 'debugger.py')
        c = self.cb.opts.get('commands', 'python')
        args = ['python', sn, fn, '%s' % xid]
        self.pid = self.fork_command(c, args)
        self.grab_focus()
        return self.pid


class Plugin(plugin.Plugin):
    NAME = 'Debugger'
    ICON = 'debug'
    DICON = 'debug', 'Load current buffer into debugger.'

    def populate_widgets(self):
        self._dbg = None
        self.ipc = gtkipc.IPWindow(self)
        #self.add_button('debug', self.cb_but_debug, 'start')
        self.add_button('stop', self.cb_but_stop, 'Stop debugging.')
        self.add_button('step', self.cb_step, 'step')
        self.add_button('jump', self.cb_next, 'next')
        self.add_button('continue', self.cb_continue, 'continue')
        self.add_button('list', self.cb_but_list, 'Show source code context.')

        vp = gtk.VPaned()
        self.add(vp)
        
        tb = gtk.VBox()
        vp.pack1(tb)

        self.term = DebugTerminal(self.cb)
        tb.pack_start(self.term, expand=False)

        self.stack = StackTree(self.cb)
        tb.pack_start(self.stack.win)
        self.stack.connect_select(self.cb_stack_select)


        nb = gtk.Notebook()
        vp.pack2(nb)

        brlb = gtk.Label()
        brlb.set_markup('<span size="small">Breaks</span>')
        self.breaks = BreakTree(self.cb)
        nb.append_page(self.breaks.win, tab_label=brlb)

        loclb = gtk.Label()
        loclb.set_markup('<span size="small">Locals</span>')
        self.locs = VarTree(self.cb)
        nb.append_page(self.locs.win, tab_label=loclb)

        gllb = gtk.Label()
        gllb.set_markup('<span size="small">Globals</span>')
        self.globs = VarTree(self.cb)
        nb.append_page(self.globs.win, tab_label=gllb)

        self.curindex = 0
        self.lfn = tempfile.mktemp('.py', 'pidatmp')
        self.debugger_loaded = False

    def do_list(self, s):
        f = open(self.lfn, 'w')
        f.write(s)
        f.close()
        self.cb.action_preview(self.lfn)

        #self.btree = tree.Tree(self.cb)
        #vp.pack1(self.stree)

    def do_started(self, *args):
        self.load_breakpoints()

    def do_frame(self, fs):
        self.curindex = fs.pop()
        
    def do_stack(self, stacks):
        stack = pickle.loads(stacks)
        #print len(stack[0].split('\1'))
        self.stack.populate([PidaFrame(*fr) for fr in stack], -1)
        

    def send(self, command):
        if self.term.pid:
            self.term.feed_child('%s\n' % command)

    def send_breakpoint(self, fn, line):
        self.send('break %s:%s' % (fn, line))

    def load_breakpoints(self):
        for bp in self.breaks.get_list():
            self.send_breakpoint(*bp)

    def load(self):
        pid = self.term.start(self.ipc.get_lid(), self.fn)
        self.debugger_loaded = True

    def cb_but_debug(self, *args):
        self.load()

    cb_alternative = cb_but_debug

    def cb_but_stop(self, *args):
        self.send('quit')
        self.term.kill()

    def cb_but_list(self, *args):
        self.send('list')


    def set_breakpoint(self, fn, line):
        self.breaks.add(fn, line)
        if self.debugger_loaded:
            self.send_breakpoint(fn, line)

    def cb_step(self, *args):
        self.send('step')

    def cb_next(self, *args):
        self.send('next')

    def cb_continue(self, *args):
        self.send('continue')

    def cb_stack_select(self, ite):
        frame = self.stack.selected(1)
        self.locs.populate(frame.locs)
        self.globs.populate(frame.globs)
        print frame.globs, frame.locs
        

    def evt_bufferchange(self, nr, name):
        self.fn = name

    def evt_die(self):
        self.term.kill()

    def evt_breakpointset(self, line, fn=None):
        if not fn:
            fn = self.fn
        if fn:
            self.set_breakpoint(fn, line)

        


