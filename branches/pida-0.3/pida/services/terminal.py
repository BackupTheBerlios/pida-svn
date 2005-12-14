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

# system import(s)
import subprocess

defs = service.definitions
types = service.types

class terminal_view(contentview.content_view):

    SHORT_TITLE = 'Terminal'

    def init(self, term_type, command_args, **kw):
        terminal, kw = make_terminal(term_type, **kw)
        self.widget.pack_start(terminal.widget)
        terminal.execute(command_args, **kw)
        self.set_long_title(' '.join(command_args))
        

class terminal_manager(service.service):

    multi_view_type = terminal_view
    multi_view_book = 'view'

    class shell(defs.optiongroup):
        """Shell options."""
        class command(defs.option):
            """The command used for the shell."""
            default = 'bash'
            rtype = types.string

    class terminal(defs.optiongroup):
        """Terminal options."""
        class terminal_type(defs.option):
            """The default terminal type used."""
            default = 'moo'
            rtype = types.stringlist('vte', 'moo')

    def cmd_execute(self, command_args=[], command_line='',
                    term_type=None, icon_name='terminal', kwdict={}):
        print kwdict
        if term_type == None:
            term_type = self.opt('terminal', 'terminal_type')
        self.create_multi_view(term_type=term_type,
                               command_args=command_args,
                               icon_name=icon_name,
                               **kwdict)

    def cmd_execute_shell(self, term_type=None, kwdict={}):
        shellcommand = self.opt('shell', 'command')
        self.call('execute', command_args=[shellcommand],
                  term_type=term_type, kwdict=kwdict)

    def act_shell(self, action):
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
            <menuitem name="shell" action="terminal+shell" />
            <menuitem name="pyshell" action="terminal+python_shell" />
            </menu>
            </menubar>
            """


Service = terminal_manager

class pida_terminal(base.pidacomponent):
    
    def execute(self, commandargs, **kw):
        pass

    @staticmethod
    def translate_kwargs(**kw):
        return kw

    def get_widget(self):
        return None
    widget = property(get_widget)

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
        self.__term.set_size_request(-1, 10)

    def get_widget(self):
        return self.__term
    widget = property(get_widget)

    def execute(self, command_args, **kw):
        command = command_args[0]
        self.__term.fork_command(command, command_args, **kw)

    def connect_child_exit(self):
        pass

    def translate_kwargs(self, **kw):
        kwdict = {}
        if 'directory' in kw:
            kwdict['directory'] = kw['directory']
        print kwdict
        return kwdict
        

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


TT_HIDDEN = 'hidden'
TT_VTE = 'vte'
TT_MOO = 'moo'

TERMINAL_TYPES = {TT_HIDDEN: hidden_terminal,
                  TT_VTE: vte_terminal,
                  TT_MOO: moo_terminal}

def make_terminal(terminal_type_name, **kw):
    print kw
    if terminal_type_name in TERMINAL_TYPES:
        terminal_type = TERMINAL_TYPES[terminal_type_name]
        terminal = terminal_type()
        kw = terminal.translate_kwargs(**kw)
        return terminal, kw

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






