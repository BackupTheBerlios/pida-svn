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

import os
import subprocess

import gtk
import gobject

import pida.core.base as base
import pida.core.service as service
import pida.core.actions as actions
import pida.pidagtk.contentview as contentview

defs = service.definitions

from pida.model import attrtypes as types

import pango

class terminal_view(contentview.content_view):

    SHORT_TITLE = 'Terminal'

    def init(self, term_type, command_args, **kw):
        terminal, kw = make_terminal(term_type, **kw)
        self.widget.pack_start(terminal.widget)
        self.set_long_title(' '.join(command_args))
        opts = self.service.options.fonts_and_colours
        
        terminal.configure(opts.foreground_colour, opts.background_colour,
                           opts.font)

        terminal.service = self.service
        terminal.connect_child_exit(self.cb_exited)
        terminal.connect_title(self.set_long_title)
        terminal.execute(command_args, **kw)
        self.grab_focus = terminal.widget.grab_focus
        self.config = terminal.configure

    def cb_exited(self):
        self.close()

view_location_map = {'View Pane':'view',
                     'Quick Pane':'content',
                     'Detached':'ext'}


class TerminalConfig:
    __order__ = ['general', 'shell', 'fonts_and_colours']
    class shell(defs.optiongroup):
        """Options relating to the shell run in terminals"""
        __order__ = ['command']
        label = 'Shell Options'
        class command(defs.option):
            """The command used for the shell"""
            default = os.environ['SHELL'] or 'bash'
            rtype = types.string
            label = 'Shell command'
    class general(defs.optiongroup):
        """General options relating to the terminal emulator"""
        __order__ = ['terminal_type', 'terminal_location']
        label = 'General Options'
        class terminal_type(defs.option):
            """The default terminal type used"""
            default = 'Vte'
            rtype = types.stringlist('Vte', 'Moo')
            label = 'Terminal Type'
        class terminal_location(defs.option):
            """The pane where newly started terminals will appear by default"""
            rtype = types.stringlist(*view_location_map.keys())
            default = 'View Pane'
            label = 'Terminal Location'
    class fonts_and_colours(defs.optiongroup):
        """Font and colour options for the terminal emulator"""
        label = 'Fonts & Colours'
        __order__  = ['background_colour', 'foreground_colour', 'font']
        class background_colour(defs.option):
            """The background colour to be used"""
            default = '#000000'
            rtype = types.color
            label = 'Background colour'
        class foreground_colour(defs.option):
            """The background colour to be used"""
            default = '#c0c0c0'
            rtype = types.color
            label = 'Foreground colour'
        class font(defs.option):
            """The font to be used in terminals"""
            default = 'Monospace 8'
            rtype = types.font
            label = 'Font'
    __markup__ = lambda self: 'Terminal Emulator'


class terminal_manager(service.service):

    config_definition = TerminalConfig

    class TerminalView(defs.View):
        view_type = terminal_view
        book_name = 'view'

    def init(self):
        self.views = []

    def cb_fonts_and_colours__foreground_colour(self, val):
        self._update_view_config()

    def cb_fonts_and_colours__background_colour(self, val):
        self._update_view_config()

    def cb_fonts_and_colours__font(self, val):
        self._update_view_config()

    views = []

    def _update_view_config(self):
        for view in self.views:
            view.config(self.opts.fonts_and_colours__foreground_colour,
                        self.opts.fonts_and_colours__background_colour,
                        self.opts.fonts_and_colours__font)

    def get_multi_view_book_type(self):
        opt = self.opts.general__terminal_location
        return view_location_map[opt]
    multi_view_book = property(get_multi_view_book_type)

    def cmd_execute(self, command_args=[], command_line='',
                    term_type=None, icon_name='terminal',
                    short_title='Terminal', kwdict={}):
        if term_type == None:
            term_type = self.opts.general__terminal_type.lower()
        view = self.create_view('TerminalView',
                                term_type=term_type,
                                command_args=command_args,
                                icon_name=icon_name,
                                short_title=short_title,
                                **kwdict)
        self.show_view(view=view)
        self.views.append(view)

    def cmd_execute_shell(self, term_type=None, kwdict={}):
        shellcommand = self.opts.shell__command
        self.cmd_execute(command_args=[shellcommand],
                  term_type=term_type, kwdict=kwdict)

    @actions.action(stock_id='gtk-terminal',
        default_accel='<Shift><Control>t')
    def act_terminal(self, action):
        """Start a shell in a terminal emulator."""
        directory = os.getcwd()
        proj = self.boss.call_command('projectmanager',
                                      'get_current_project')
        if proj is not None:
            directory = proj.source__directory
        self.cmd_execute_shell(kwdict={'directory': directory})

    def view_closed(self, view):
        self.views.remove(view)

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_tools" action="base_tools_menu">
                <placeholder name="ToolsMenu">
            <menuitem name="shell" action="terminal+terminal" />
                </placeholder>
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
            <toolitem  name="terminal" action="terminal+terminal" />
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
        """
        Feed text to the terminal, optionally coloured.
        """
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

import re

fre = re.compile(r'(/.+):([0-9]+):')
pre = re.compile(r'File \"(/.+)\"\, line ([0-9]+)\,')

class moo_terminal(pida_terminal):

    def init(self):
        import moo
        self.__term = moo.term.Term()
        self.__term.connect('child-died', self.cb_exited)
        
        self.it = self.__term.create_tag('a')
        self.it.set_attributes(moo.term.TEXT_FOREGROUND, moo.term.BLUE)
        self.pt = self.__term.create_tag('b')
        self.pt.set_attributes(moo.term.TEXT_FOREGROUND, moo.term.RED)
            
        self.__term.connect('new-line', self.cb_newline)
            
        self.__term.connect('populate-popup', self.cb_popup)

    def cb_popup(self, t, menu):
        if not t.get_selection():
            menu.get_children()[0].set_sensitive(False)
        x, y = t.window_to_buffer_coords(*t.get_pointer())
        i = t.get_iter_at_location(x, y)
        if i.has_tag(self.it) or i.has_tag(self.pt):
            e = i.copy()
            if i.has_tag(self.it):
                i.get_tag_start(self.it)
                e.get_tag_end(self.it)
                string = i.get_text(e)
                filename, ln, empty = string.split(':')
            elif i.has_tag(self.pt):
                i.get_tag_start(self.pt)
                e.get_tag_end(self.pt)
                string = i.get_text(e)
                filename, ln = pre.search(string).groups()
                
                
            menu.add(gtk.SeparatorMenuItem())
            a = gtk.Action('goto-line', 'Goto line', 'Goto the line',
                           gtk.STOCK_OK)
            mi = a.create_menu_item()
            menu.add(mi)
            menu.show_all()
            a.connect('activate', self.act_gotoline, filename, int(ln) - 1)

    def cb_newline(self, t):    
        cursor_i = t.get_iter_at_cursor()
        line_n = cursor_i.row - 1
        startline_i = t.get_iter_at_line(line_n)
        endline_i = startline_i.copy()
        endline_i.forward_to_line_end()
        line = startline_i.get_text(endline_i)
        self._line_received(line, line_n)

    def _line_received(self, line, line_n):
        for r, tag in [(fre, self.it), (pre, self.pt)]:
            match = r.search(line)
            if match:
                t = self.__term
                msl = t.get_iter_at_line_offset(line_n, match.start())
                esl = t.get_iter_at_line_offset(line_n, match.end())
                t.apply_tag(tag, msl, esl)

    def act_gotoline(self, action, file, line):
        self.service.boss.call_command('buffermanager', 'open_file_line',
            filename=file, linenumber=line)

    def get_line_at_click(self, x, y):
        pass

    def get_word_at_click(self, x, y):
        pass

    def cb_exited(self, term):
        self.feed('Child exited\r\n', '1;34')
        self.feed('Press any key to close.')
        self.__term.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.__term.connect('key-press-event', self.cb_press_any_key)

    def feed(self, text, color=None):
        """ Feed text to the terminal, optionally coloured."""
        if color is not None:
            text = '\x1b[%sm%s\x1b[0m' % (color, text)
        self.__term.feed(text)

    def cb_press_any_key(self, term, event):
        self.exited()

    def execute(self, command_args, **kw):
        self.__term.fork_argv(command_args, **kw)

    def configure(self, fg, bg, font):
        self.__term.set_font_from_string(font)
        self.__term.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(fg))
        self.__term.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(bg))

    def get_widget(self):
        return self.__term
    widget = property(get_widget)

    def translate_kwargs(self, **kw):
        kwdict = {}
        if 'directory' in kw:
            kwdict['working_dir'] = kw['directory']
        return kwdict

    def connect_title(self, callback):
        def title_changed(term, title):
            callback(title)
        self.__term.connect('set-window-title', title_changed)


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






