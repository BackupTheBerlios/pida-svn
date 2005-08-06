# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id$
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

# System imports
import os
import re

# GTK imports
import gtk

# vte terminal emulator widget
try:
    import vte
except ImportError:
    class Dummy(object):
        Terminal = object
        bad = True
    vte = Dummy

# Pida imports
import pida.base as base
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry

class Terminal(base.pidaobject, vte.Terminal):
    """ A terminal emulator widget that uses global config information. """
    def do_init(self):
        vte.Terminal.__init__(self)
        ## set config stuff
        # transparency
        trans = self.prop_main_registry.terminal.enable_transparency.value()
        if trans:
            self.set_background_transparent(trans)
        # colors
        # get the colour map
        cmap = self.get_colormap()
        # bg
        c = self.prop_main_registry.terminal.background_color.value()
        bgcol = cmap.alloc_color(c)
        # fg
        c = self.prop_main_registry.terminal.foreground_color.value()
        fgcol = cmap.alloc_color(c)
        # set to the new values
        self.set_colors(fgcol, bgcol, [])
        #font
        font = self.prop_main_registry.terminal.font.value()
        self.set_font_from_string(font)
        # set the default size really small
        self.set_size(60, 10)
        self.set_size_request(-1, 50)

    def feed(self, text, color=None):
        """ Feed text to the terminal, optionally coloured."""
        if color:
            # construct the ansi escape sequence
            text = '\x1b[%sm%s\x1b[0m' % (color, text)
        # call the superclass method
        vte.Terminal.feed(self, text)

class PidaTerminal(base.pidaobject):
    """ A terminal emulator widget aware of the notebook it resides in. """
    def do_init(self, icon, immortal=False):
        # the parent notebook
        # generate widgets
        self.win = gtk.VBox(self)
        self.win.show()
        # terminal widget
        self.term = Terminal()
        self.win.pack_start(self.term)
        self.term.show()
        # connect the terminal widget's signals
        self.term.connect('button_press_event', self.cb_button)
        self.term.connect('child-exited', self.cb_exited)
        # tab label
        # self.label = Tablabel(icon)
        self.icon = icon
        # can we be killed?
        self.immortal=immortal
        # a handler for right click matching
        # may be removed
        self.match = MatchHandler()
        # the PID of the child process
        self.pid = -1

    def start(self):
        pass

    def die(self):
        self.kill()

    def run_command(self, command, args=[], **kw):
        """ Fork a system command in the terminal """
        self.term.feed('Executing ')
        self.term.feed(command, '34;1')
        self.term.feed(' %s\r\n' % args)
        self.pid = self.term.fork_command(command, args, **kw)
        # give the terminal focus
        self.term.grab_focus()

    def popup(self, word):
        """ Popup the terminal context menu """
        menu = TerminalMenu(self.pida)
        menu.set_title(word)

    def kill(self):
        """ Attempt to forcibly teminate the child process, if running """
        if self.pid > 0:
            try:
                os.kill(self.pid, 15)
            except OSError:
                pass #"already terminated"

    def remove(self):
        """ Remove own page from parent notebook """
        self.do_action('closecontentpage')

    def right_press(self, x, y):
        """ Right click handler """
        word = self.word_from_coord(x, y)
        self.match.match(word)

    def word_from_coord(self, x, y):
        """ Retrieve the word in the terminal at cursor coordinates """
        def isin(term, cx, cy, *args):
            if cy == y:
                return True
            else:
                return False
        line = self.term.get_text_range(y, 0, y, -1, isin)
        if x <= len(line):
            p1, p2 = line[:x], line[x:]
            p1 = p1.split()[-1]
            p2 = p2.split()[0]
            word = ''.join([p1, p2])
            return word

            
    def char_from_coord(self, cx, cy):
        """ Character coordinates for cursor coordinates. """
        h = self.term.get_char_height()
        w = self.term.get_char_width()
        ya = self.term.get_adjustment().value
        x = int(cx/w)
        y = int((cy)/h + ya)
        return x, y

    def cb_button(self, terminal, event):
        """ Mouse button event handler. """
        if event.button == 3:
            if event.type == gtk.gdk.BUTTON_PRESS:
                cc = self.char_from_coord(event.x, event.y)
                self.right_press(*cc)

    def cb_exited(self, *a):
        """ Child exited event handler. """
        self.pid = -1
        self.term.feed('\r\nchild exited ', '1;34')
        self.term.feed('press any key to close')
        self.term.connect('commit', self.cb_anykey)
    
    def cb_anykey(self, *a):
        """ Any key event handler. """
        self.remove()

class Plugin(plugin.Plugin):
  
    def configure(self, reg):
        ### Terminal emulator options
        
        self.registry = reg.add_group('terminal',
            'Options for the built in terminal emulator.')

        self.registry.add('internal',
            registry.Boolean,
            True,
            'Determines whether Pida will use its builtin terminal emulator '
            '(otherwise will use Xterm).')
        
        self.registry.add('font',
                       registry.Font,
                       'Monospace 10',
                       'The font for newly started terminals.')

        self.registry.add('enable_transparency',
                       registry.Boolean,
                       0,
                       'Determines whether terminals will appear transparent')
                       
        self.registry.add('background_color',
                registry.Color,
                '#000000',
                'The background colour for terminals')

        self.registry.add('foreground_color',
                registry.Color,
                '#d0d0d0',
                'The foreground colour for terminals')
    
    def evt_terminal(self, commandline, **kw):
        if not hasattr(vte, 'bad') and self.registry.internal.value():
            self.termmap_internal(commandline, **kw)
        else:
            self.termmap_xterm(commandline, **kw)

    __call__ = evt_terminal
 
    def termmap_internal(self, commandline, **kw):
        icon = 'terminal'
        if 'icon' in kw:
            icon = kw['icon']
            del kw['icon']
        child = PidaTerminal(icon)
        args = commandline.split()
        command = args.pop(0)
        args.insert(0, 'PIDA')
        self.do_action('newcontentpage', child)
        child.run_command(command, args, **kw)
        return child

    def termmap_xterm(self, commandline, **kw):
        xterm = 'xterm'
        self.termmap_external(xterm, commandline, **kw)

    def termmap_external(self, termpath, commandline, **kw):
        commandargs = [termpath, '-hold', '-e', commandline]
        self.do_action('fork', commandargs)

# will vanish, superceded by plugin.ContextMenu
class TerminalMenu(base.pidaobject, gtk.Menu):
    def do_init(self):
        gtk.Menu.__init__(self)

    def add_item(self, name, callback, *args):
        item = gtk.MenuItem(label=name)
        item.connect('activate', callback, *args)
        item.show()
        self.append(item)

    def set_title(self, title):
        item = gtk.MenuItem(label=title)
        item.show()
        self.prepend(item)        

class Match(base.pidaobject):
    RE = re.compile('.+')
    
    def do_init(self):
        self.menu = TerminalMenu()
        self.generate_menu()

    def check(self, word):
        try:
            return self.RE.search(word)
        except TypeError:
            return None

    def popup(self, word):
        self.word = word
        self.menu.popup(None, None, None, 3, 0)

    def add_match_command(self, name, cmd, args):
        self.menu.add_item(name, self.cb_newcommand, cmd, args)

    def cb_newcommand(self, menu, cmd, args):
        args = list(args)
        args.append(self.word)
        self.do_action('newterminal', ' '.join([cmd] + args))

class DefaultMatch(Match):
    def generate_menu(self):
        self.add_match_command('dict',
                                '/usr/bin/dict', [])

class URLMatch(Match):
    RE = re.compile('http')
    def generate_menu(self):
        obrowser = self.prop_main_registry.commands.browser.value()
        self.add_match_command('external',
                                obrowser, [])

class NumberMatch(Match):
    RE = re.compile('[0-9].+')
    def generate_menu(self):
        self.menu.add_item('jump to', self.cb_jump)
        self.menu.add_item('kill 15', self.cb_kill)
    
    def cb_jump(self, *args):
        self.do_edit('gotoline', int(self.word.strip(',.:')))
        
    def cb_kill(self, *args):
        os.kill(int(self.word), 15)

class MatchHandler(base.pidaobject):
    def do_init(self):
        self.matches = [NumberMatch(),
                        URLMatch(),
                        DefaultMatch()]

    def match(self, word):
        for m in self.matches:
            if m.check(word):
                m.popup(word)
                break
