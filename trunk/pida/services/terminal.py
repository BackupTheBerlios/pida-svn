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

# pIDA import(s)
import pida.core.base as base
import pida.core.service as service

# pidagtk import(s)
import pida.pidagtk.contentview as contentview
import gobject
import gtk

# system import(s)
import os
import subprocess

defs = service.definitions
types = service.types

class terminal_view(contentview.content_view):

    SHORT_TITLE = 'Terminal'

    def init(self, term_type, command_args, **kw):
        terminal, kw = make_terminal(term_type, **kw)
        self.widget.pack_start(terminal.widget)
        self.set_long_title(' '.join(command_args))
        terminal.configure(self.service.opt('fonts_and_colours',
                                            'foreground_colour'),
                           self.service.opt('fonts_and_colours',
                                            'background_colour'),
                           self.service.opt('fonts_and_colours',
                                            'font'))
        terminal.connect_child_exit(self.cb_exited)
        terminal.connect_title(self.set_long_title)
        terminal.execute(command_args, **kw)

    def cb_exited(self):
        self.close()
        
view_location_map = {'View Pane':'view',
                     'Quick Pane':'content',
                     'Detached':'ext'}

class terminal_manager(service.service):

    display_name = 'Terminals'

    multi_view_type = terminal_view

    def get_multi_view_book_type(self):
        opt = self.opt('general', 'terminal_location')
        return view_location_map[opt]
    multi_view_book = property(get_multi_view_book_type)

    class shell(defs.optiongroup):
        """Shell options."""
        class command(defs.option):
            """The command used for the shell."""
            default = os.environ['SHELL'] or 'bash'
            rtype = types.string

    class general(defs.optiongroup):
        """Terminal options."""
        class terminal_type(defs.option):
            """The default terminal type used."""
            default = 'Vte'
            rtype = types.stringlist('Vte', 'Moo')
        class terminal_location(defs.option):
            """Where newly started terminals will appear by default"""
            rtype = types.stringlist(*view_location_map.keys())
            default = 'View Pane'

    class fonts_and_colours(defs.optiongroup):
        """Fonts and colours for the terminal"""
        class background_colour(defs.option):
            """The background colour to be used"""
            default = '#000000'
            rtype = types.color
        class foreground_colour(defs.option):
            """The background colour to be used"""
            default = '#c0c0c0'
            rtype = types.color
        class font(defs.option):
            """The font to be used in terminals"""
            default = 'Monospace 8'
            rtype = types.font

    def cmd_execute(self, command_args=[], command_line='',
                    term_type=None, icon_name='terminal', kwdict={}):
        if term_type == None:
            term_type = self.opt('general', 'terminal_type').lower()
        self.create_multi_view(term_type=term_type,
                               command_args=command_args,
                               icon_name=icon_name,
                               **kwdict)

    def cmd_execute_shell(self, term_type=None, kwdict={}):
        shellcommand = self.opt('shell', 'command')
        self.call('execute', command_args=[shellcommand],
                  term_type=term_type, kwdict=kwdict)

    def act_terminal(self, action):
        """Start a shell in a terminal emulator."""
        self.call('execute_shell')

    def act_python_shell(self, action):
        """Start an interactive python shell."""
        self.call('execute', command_args=['python'])

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_tools" action="base_tools_menu">
            <separator />
            <menuitem name="shell" action="terminal+terminal" />
            <menuitem name="pyshell" action="terminal+python_shell" />
            </menu>
            </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
                </placeholder>
                <placeholder name="SaveFileToolbar">
                </placeholder>
                <placeholder name="EditToolbar">
                </placeholder>
                <placeholder name="ProjectToolbar">
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
                <placeholder name="ToolsToolbar">
            <separator />
            <toolitem  name="terminal" action="terminal+terminal" />
            <separator />
                </placeholder>
                </toolbar>
            """


Service = terminal_manager

class pida_terminal(base.pidacomponent):

    def connect_child_exit(self, callback):
        self.exited = callback
    
    def execute(self, commandargs, **kw):
        pass

    @staticmethod
    def translate_kwargs(**kw):
        return kw

    def get_widget(self):
        return None
    widget = property(get_widget)

    def configure(self, fg, bg, font):
        pass

class hidden_terminal(pida_terminal):

    def init(self):
        pass

    def execute(self, commandline, **kw):
        proc = subprocess.Popen(commandline)

    def connect_child_exit(self):
        pass

class vte_terminal(pida_terminal):

    def init(self):
        import vte
        self.__term = vte.Terminal()
        self.__term.connect('child-exited', self.cb_exited)

    def configure(self, fg, bg, font):
        bgcol = gtk.gdk.color_parse(bg)
        fgcol = gtk.gdk.color_parse(fg)
        self.__term.set_colors(fgcol, bgcol, [])
        self.__term.set_font_from_string(font)
        self.__term.set_size(30, 10)
        self.__term.set_size_request(1, 50)

    def get_widget(self):
        return self.__term
    widget = property(get_widget)

    def execute(self, command_args, **kw):
        command = command_args[0]
        self.__term.fork_command(command, command_args, **kw)


    def feed(self, text, color=None):
        """ Feed text to the terminal, optionally coloured."""
        if color is not None:
            text = '\x1b[%sm%s\x1b[0m' % (color, text)
        self.__term.feed(text)

    def cb_exited(self, term):
        self.feed('Child exited\r\n', '1;34')
        self.feed('Press any key to close.')
        self.__term.connect('commit', self.cb_press_any_key)

    def cb_press_any_key(self, term, data, datalen):
        self.exited()

    def translate_kwargs(self, **kw):
        kwdict = {}
        if 'directory' in kw:
            kwdict['directory'] = kw['directory']
        return kwdict

    def connect_title(self, callback):
        def title_changed(term):
            title = term.get_window_title()
            callback(title)
        self.__term.connect('window-title-changed', title_changed)
        

class moo_terminal(pida_terminal):

    def init(self):
        import moo
        self.__term = moo.term.Term()

    def execute(self, command_args, **kw):
        self.__term.fork_argv(command_args, **kw)

    def get_widget(self):
        return self.__term
    widget = property(get_widget)

    def connect_child_exit(self):
        pass

    def translate_kwargs(self, **kw):
        kwdict = {}
        if 'directory' in kw:
            kwdict['working_dir'] = kw['directory']
        return kwdict

    def connect_title(self, callback):
        pass

class dumb_terminal(pida_terminal):

    def init(self):
        import gtk
        self.__sw = gtk.ScrolledWindow()
        self.__sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__view = gtk.TextView()
        self.__sw.add(self.__view)

    def configure(self, fg, bg, font):
        model = self.__view.get_buffer()
        self.__tag = model.create_tag('fixed', editable=False,
                                      font=font)
                                       #, background=bg,
                                      #foreground=fg)
        #bgcol = gtk.gdk.color_parse(bg)
        #self.__view.modify_bg(gtk.STATE_NORMAL, bgcol)
        #self.__view.modify_base(gtk.STATE_NORMAL, bgcol)


    def translate_kwargs(self, **kw):
        kwdict = {}
        if 'directory' in kw:
            kwdict['cwd'] = kw['directory']
        return kwdict

    def execute(self, command_args, **kw):
        proc = popen(command_args, self.cb_completed, kw)

    def get_widget(self):
        return self.__sw

    def cb_completed(self, data):
        model = self.__view.get_buffer()
        start = model.get_start_iter()
        data = '%s\nChild exited' % data
        model.insert_with_tags(start, data, self.__tag)
        self.__view.scroll_to_iter(model.get_end_iter(), 0.0, False)


    def connect_title(self, callback):
        pass

        

    widget = property(get_widget)

TT_HIDDEN = 'hidden'
TT_VTE = 'vte'
TT_MOO = 'moo'
TT_DUMB = 'dumb'

TERMINAL_TYPES = {TT_HIDDEN: hidden_terminal,
                  TT_VTE: vte_terminal,
                  TT_MOO: moo_terminal,
                  TT_DUMB: dumb_terminal}

def make_terminal(terminal_type_name, **kw):
    if terminal_type_name in TERMINAL_TYPES:
        terminal_type = TERMINAL_TYPES[terminal_type_name]
    else:
        terminal_type = vte_terminal
    terminal = terminal_type()
    kw = terminal.translate_kwargs(**kw)
    return terminal, kw


class popen(object):
    
    def __init__(self, cmdargs, callback, kwargs):
        self.__running = False
        self.__readbuf = []
        self.__callback = callback
        self.run(cmdargs, **kwargs)
    
    def run(self, cmdargs, **kwargs):
        console = subprocess.Popen(args=cmdargs, stdout=subprocess.PIPE,
                                                 stderr=subprocess.STDOUT,
                                                 **kwargs)
        self.__running = True
        self.__readtag = gobject.io_add_watch(
            console.stdout, gobject.IO_IN, self.cb_read)
        self.__huptag = gobject.io_add_watch(
            console.stdout, gobject.IO_HUP, self.cb_hup)
        self.pid = console.pid

    def cb_read(self, fd, cond):
        data = os.read(fd.fileno(), 1024)
        self.__readbuf.append(data)
        return True

    def cb_hup(self, fd, cond):
        self.__callback(''.join(self.__readbuf))
        self.__running = False
        gobject.source_remove(self.__readtag)
        return False

def test_terminal(terminal_type_names, command_line, **kw):
    import gtk
    w = gtk.Window()
    b = gtk.VButtonBox()
    w.add(b)
    for tt in terminal_type_names:
        t, kw = make_terminal(tt, **kw)
        if t.widget is not None:
            t.widget.set_size_request(200, 200)
            b.pack_start(t.widget, expand=True)
        else:
            b.pack_start(gtk.Label('no widget for %s' % tt))
        t.execute(command_line, **kw)
    w.show_all()
    w.connect('destroy', lambda *a: gtk.main_quit())
    gtk.main()






