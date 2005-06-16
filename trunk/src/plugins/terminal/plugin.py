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

# gtk
import gtk

# vte terminal emulator widget
import vte

# Pida plug in base
import pida.plugin as plugin
import pida.gtkextra as gtkextra
# will vanish, superceded by plugin.ContextMenu
class TerminalMenu(gtk.Menu):
    def __init__(self, cb):
        self.cb = cb
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

class Match(object):
    RE = re.compile('.+')
    
    def __init__(self, cb):
        self.cb = cb
        self.menu = TerminalMenu(self.cb)
        self.generate_menu()

    def check(self, word):
        return self.RE.search(word)

    def popup(self, word):
        self.word = word
        self.menu.popup(None, None, None, 3, 0)

    def add_match_command(self, name, cmd, args):
        self.menu.add_item(name, self.cb_newcommand, cmd, args)

    def cb_newcommand(self, menu, cmd, args):
        args = list(args)
        args.append(self.word)
        self.cb.action_newterminal(cmd, args)

class DefaultMatch(Match):
    def generate_menu(self):
        self.add_match_command('dict',
                                '/usr/bin/dict', ['dict'])

class URLMatch(Match):
    RE = re.compile('http')
    def generate_menu(self):
        obrowser = self.cb.opts.get('commands', 'browser')
        self.add_match_command('external',
                                obrowser, ['browser'])

class NumberMatch(Match):
    RE = re.compile('[0-9].+')
    def generate_menu(self):
        self.menu.add_item('jump to', self.cb_jump)
        self.menu.add_item('kill 15', self.cb_kill)
    
    def cb_jump(self, *args):
        self.cb.action_gotoline(int(self.word.strip(',.:')))
        
    def cb_kill(self, *args):
        os.kill(int(self.word), 15)

class MatchHandler(object):
    def __init__(self, cb):
        self.cb = cb
        self.matches = [NumberMatch(self.cb), 
                        URLMatch(self.cb),
                        DefaultMatch(self.cb)]

    def match(self, word):
        for m in self.matches:
            if m.check(word):
                m.popup(word)
                break

class Terminal(vte.Terminal):
    ''' A terminal emulator widget that uses global config information. '''
    def __init__(self, cb):
        self.cb = cb
        vte.Terminal.__init__(self)
        ## set config stuff
        # transparency
        v = self.cb.opts.get('terminal','transparency_enable')
        trans = int(v)
        if trans:
            self.set_background_transparent(trans)
        # colors
        # get the colour map
        cmap = self.get_colormap()
        # bg
        c = self.cb.opts.get('terminal', 'colour_background')
        bgcol = cmap.alloc_color(c)
        # fg
        c = self.cb.opts.get('terminal', 'colour_foreground')
        fgcol = cmap.alloc_color(c)
        # set to the new values
        self.set_colors(fgcol, bgcol, [])
        #font
        self.set_font_from_string(self.cb.opts.get('terminal', 'font_default'))
        # set the default size really small
        self.set_size(40, 20)

    def feed(self, text, color=None):
        ''' Feed text to the terminal, optionally coloured.'''
        if color:
            # construct the ansi escape sequence
            text = '\x1b[%sm%s\x1b[0m' % (color, text)
        # call the superclass method
        vte.Terminal.feed(self, text)

class PidaTerminal(gtk.VBox):
    ''' A terminal emulator widget aware of the notebook it resides in. '''
    def __init__(self, cb, notebook, icon, immortal=False):
        self.cb = cb
        # the parent notebook
        self.notebook = notebook
        # generate widgets
        gtk.VBox.__init__(self)
        self.show()
        # terminal widget
        self.term = Terminal(self.cb)
        self.pack_start(self.term)
        self.term.show()
        # connect the terminal widget's signals
        self.term.connect('button_press_event', self.cb_button)
        self.term.connect('child-exited', self.cb_exited)
        # tab label
        self.label = Tablabel(self.cb, icon)
        # can we be killed?
        self.immortal=immortal
        # a handler for right click matching
        # may be removed
        self.match = MatchHandler(self.cb)
        # the PID of the child process
        self.pid = -1

    def run_command(self, command, args=[], **kw):
        ''' Fork a system command in the terminal '''
        self.term.feed('Executing ')
        self.term.feed(command, '34;1')
        self.term.feed(' %s\r\n' % args)
        self.pid = self.term.fork_command(command, args, **kw)
        self.term.grab_focus()

    def popup(self, word):
        menu = TerminalMenu(self.cb)
        menu.set_title(word)

    def kill(self):
        ''' Attempt to forcibly teminate the child process, if running '''
        if self.pid > 0:
            try:
                os.kill(self.pid, 15)
            except OSError:
                pass #"already terminated"

    def remove(self):
        ''' Remove own page from parent notebook '''
        index = self.notebook.page_num(self)
        if self.immortal:
            return False
        else:
            self.notebook.remove_page(index)
            return True

    def right_press(self, x, y):
        ''' Right click handler '''
        word = self.word_from_coord(x, y)
        self.match.match(word)

    def word_from_coord(self, x, y):
        ''' Retrieve the word in the terminal at cursor coordinates '''
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
        ''' Character coordinates for cursor coordinates. '''
        h = self.term.get_char_height()
        w = self.term.get_char_width()
        ya = self.term.get_adjustment().value
        x = int(cx/w)
        y = int((cy)/h + ya)
        return x, y

    def cb_button(self, terminal, event):
        ''' Mouse button event handler. '''
        if event.button == 3:
            if event.type == gtk.gdk.BUTTON_PRESS:
                cc = self.char_from_coord(event.x, event.y)
                self.right_press(*cc)

    def cb_exited(self, *a):
        ''' Child exited event handler. '''
        self.pid = -1
        self.term.feed('\r\nchild exited ', '1;34')
        self.term.feed('press any key to close')
        self.term.connect('commit', self.cb_anykey)
    
    def cb_anykey(self, *a):
        ''' Any key event handler. '''
        self.remove()

class Tablabel(gtk.EventBox):
    ''' A label for a notebook tab. '''
    def __init__(self, cb, stockid):
        self.cb = cb
        # Construct widgets
        gtk.EventBox.__init__(self)
        self.set_visible_window(True)
        # Get the requested icon
        self.image = self.cb.icons.get_image(stockid, 14)
        self.add(self.image)
        # Different styles for highligting labels
        self.hst = self.style.copy()
        self.dst = self.style
        col = self.get_colormap().alloc_color('#FF8080')
        for i in xrange(5):
            self.hst.bg[i] = col
        self.show_all()

    def read(self):
        ''' Called to unhighlight the tab label '''
        self.set_style(self.dst)
   
    def unread(self):
        ''' Highlight the tab label '''
        self.set_style(self.hst)

class Logterminal(PidaTerminal):
    ''' A terminal for logging. '''

    def __init__(self, *args):
        PidaTerminal.__init__(self, *args)
        self.term.set_font_from_string(self.cb.opts.get('terminal',
                                                        'font_log'))
        self.term.feed('Log started at ')
        self.term.feed('Level %s\r\n' % self.level(), '32;1')
    
    def level(self):
        return int(self.cb.opts.get('log', 'level'))

    def write_log(self, message, details='', level=0):
        if level >= self.level():
        
            self.term.feed('%s ' % level, '32;1')
            self.term.feed('%s ' % message, '34;1')
            self.term.feed('%s\r\n' % self.truncate(details))

    def truncate(self, message):
        return message[:36]


        
class Plugin(plugin.Plugin):
    ''' The terminal emulator plugin '''
    NAME = "Shell"
    DETACHABLE = True
    def populate_widgets(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.set_scrollable(True)
        self.notebook.set_property('show-border', False)
        self.notebook.set_property('tab-border', 2)
        self.notebook.set_property('enable-popup', True)
        self.add(self.notebook)

        self.add_separator()
        self.add_button('terminal', self.cb_new,
                        'Open a new shell')
        self.add_button('close', self.cb_close,
                        'Close current tab.')
       
        self.panes = {}
        self.toolbar_popup.add_separator()
        self.toolbar_popup.add_item('configure',
                            'Configure this shortcut bar',
                            self.cb_conf_clicked, [])

        self.ctxbar = gtkextra.ContextToolbar(self.cb, 'terminal')
        self.shortbar.pack_start(self.ctxbar.win)

        self.logterm = self.new_log()

    def cb_conf_clicked(self, *args):
        self.cb.action_showshortcuts()

    def connect_widgets(self):
        self.notebook.connect('switch-page', self.cb_switch)

    def add_terminal(self, ttype, icon, immortal=False):
        child = ttype(self.cb, self.notebook, icon, immortal)
        child.show_all()
        self.notebook.append_page(child, tab_label=child.label)
        self.notebook.set_current_page(-1)
        self.notebook.show_all()
        return child

    def remove_terminal(self, index):
        child = self.notebook.get_nth_page(index)
        child.kill()
        return child.remove()

    def new_command(self, command, args, icon, **kw):
        child = self.add_terminal(PidaTerminal, icon, False)
        child.run_command(command, args, **kw)
        return child 

    def new_shell(self):
        shell = self.cb.opts.get('commands', 'shell')
        self.new_command(shell, ['shell'], 'terminal')

    def new_log(self):
        icon = 'warning'
        return self.add_terminal(Logterminal, icon, True)

    def evt_newterm(self, command, args, **kw):
        self.new_command(command, args, 'terminal', **kw)

    def evt_log(self, message, details, level=0):
        self.logterm.write_log(message, details, level)

    def evt_question(self, prompt, callback):
        self.new_question(prompt, callback)

    def evt_shortcutschanged(self):
        self.ctxbar.refresh()
        self.ctxbar.show()

    def cb_new(self, *args):
        self.new_shell()

    def cb_close(self, *args):
        if not self.remove_terminal(self.notebook.get_current_page()):
            self.error('cannot remove log window')

    def cb_changed(self, terminal):
        cpage = self.notebook.get_nth_page(self.notebook.get_current_page())
        if terminal != cpage:
            terminal.label.unread()

    def cb_switch(self, notebook, p, id, *args):
        self.notebook.get_nth_page(id).label.read()

    def cb_browser(self, *args):
        self.new_browser('http://www.google.com/palm/')



