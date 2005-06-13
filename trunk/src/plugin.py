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


import gtk
import os
import fnmatch

def test(ptype):
    
    pi = ptype(None)
    w = gtk.Window()
    w.add(self.pi.win)
    w.show_all()
    gtk.main()

class Winparent(gtk.Window):
    def __init__(self, cb, child):
        self.cb = cb
        gtk.Window.__init__(self)
        self.set_transient_for(self.cb.cw)
        child.win.reparent(self)
        self.show()
        self.connect('destroy', child.attach)

class Transient(object):
    
    def __init__(self, cb):
        self.cb = cb
        self.win = gtk.VBox()

        self.tb = gtk.HBox()
        self.win.pack_start(self.tb, expand=False)
        
        self.close_but = self.cb.icons.get_button('close', 12)
        eb = gtk.EventBox()
        eb.add(self.close_but)
        self.tb.pack_start(eb, expand=False)
        self.cb.tips.set_tip(eb, 'Close mini window')
        self.close_but.connect('clicked', self.cb_close_but)

        self.label = gtk.Label()
        self.tb.pack_start(self.label, expand=False)

        sep = gtk.HSeparator()
        self.tb.pack_start(sep)

        self.frame = gtk.VBox()
        self.win.pack_start(self.frame)#, expand=False)
        self.populate_widgets()
    
    def populate_widgets(self):
        pass    

    def show(self, label):
        self.label.set_label(label)
        self.win.show_all()

    def hide(self):
        self.win.hide_all()

    def cb_close_but(self, *args):
        self.hide()    

class Messagebox(Transient):

    def populate_widgets(self):
        self.display_label = gtk.Label()
        self.display_label.set_line_wrap(True)
        self.frame.pack_start(self.display_label, expand=False)
        self.id = 0

    def message(self, msg):
        self.id = self.id + 1
        self.display_label.set_label(msg)
        self.show('Message (%s)' % self.id)
       
class Questionbox(Messagebox):
    
    def populate_widgets(self):
        Messagebox.populate_widgets(self)
        self.hbar = gtk.HBox()
        self.frame.pack_start(self.hbar, expand=False)
        self.entry = gtk.Entry()
        self.hbar.pack_start(self.entry)
        eb = gtk.EventBox()
        self.tb.pack_start(eb, expand=False)
        self.submit = self.cb.icons.get_button('apply', 12)
        eb.add(self.submit)
        self.cb.tips.set_tip(eb, 'ok')

    def question(self, msg, callback):
        def cb(*args):
            self.submit.disconnect(self.qid)
            self.hide()
            callback(self.entry.get_text())
        self.entry.set_text('')
        self.qid = self.submit.connect('clicked', cb)
        self.display_label.set_label(msg)
        self.show('Question (%s)' % self.id)
        
class Optionbox(Messagebox):
    def populate_widgets(self):
        Messagebox.populate_widgets(self)
        self.entry = gtk.combo_box_new_text()
        self.frame.pack_start(self.entry)
        self.submit = self.cb.icons.get_button('apply', 12)
        self.tb.pack_start(self.submit, expand=False)

    def option(self, msg, options, callback):
        def cb(*args):
            self.hide()
            callback(self.entry.get_active_text())
        self.entry.get_model().clear()
        for i in options:
            self.entry.append_text(i)
        self.entry.set_active(0)
        self.submit.connect('clicked', cb)
        self.display_label.set_label(msg)
        self.show('Option (%s)' % self.id)
 
class Toolbar(object):
    def  __init__(self, cb):
        self.cb = cb
        self.win = gtk.HBox()

    def add_button(self, stock, callback, tooltip='None Set!', cbargs=[]):
        evt = gtk.EventBox()
        but = self.cb.icons.get_button(stock)
        evt.add(but)
        self.cb.tips.set_tip(evt, tooltip)
        but.connect('clicked', callback, *cbargs)
        self.win.pack_start(evt, expand=False, padding=0)
        return but

    def add_separator(self):
        sep = gtk.VSeparator()
        self.win.pack_start(sep, padding=0, expand=False)

    def pack_start(self, *args, **kw):
        self.win.pack_start(*args, **kw)

    def show(self):
        self.win.show_all()

class Sepbar(object):
    def __init__(self, cb):
        self.cb = cb
        self.win = gtk.EventBox()
        exp = gtk.HSeparator()
        self.win.add(exp)
        self.win.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.win.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.win.connect('button-press-event', self.cb_press)
        self.cb_rclick = None
        self.cb_dclick = None

    def cb_press(self, eb, event):
        if event.button == 3:
            if self.cb_rclick:
                self.cb_rclick(event)
        elif event.type == gtk.gdk._2BUTTON_PRESS:
            if self.cb_dclick:
                self.cb_dclick(event)

    def connect(self, rclick, dclick):
        self.cb_rclick = rclick
        self.cb_dclick = dclick

class Popup(object):
    def __init__(self, cb, *args):
        self.cb = cb
        self.menu = gtk.Menu(*args)
        self.init()
    
    def add_item(self, icon, text, cb, cbargs):
        mi = gtk.MenuItem()
        self.menu.append(mi)
        mi.connect('activate', cb, cbargs)
        hb = gtk.HBox()
        mi.add(hb)
        im = self.cb.icons.get_image(icon)
        hb.pack_start(im, expand=False, padding=4)
        lb = gtk.Label(text)
        hb.pack_start(lb, expand=False)

    def add_separator(self):
        ms = gtk.SeparatorMenuItem()
        self.menu.append(ms)

    def popup(self, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, 3, time)

    def clear(self):
        for mi in self.menu.get_children():
            self.menu.remove(mi)

    def init(self, *args):
        pass

POPUP_CONTEXTS = ['file', 'dir', 'terminal', 'string', 'url']

class ContextGenerator(object):

    def __init__(self, cb, name):
        self.cb = cb
        self.name = name
        self.aargs = []

    def generate(self):
        for sect in self.cb.shortcuts.get_shortcuts():
            name, command, glob, icon, ctx = sect
            for i, ct in enumerate(ctx):
                if POPUP_CONTEXTS[i] == self.name and ct == '1':
                    gmatch = None
                    if self.aargs:
                        gmatch = fnmatch.fnmatch(self.aargs[0], glob)
                    if not self.aargs or gmatch:
                        com, args = self.cargs_from_line(command)
                        self.add_item(icon, name,
                            self.cb_activate, [com, args, self.aargs])

    def cargs_from_line(self, line):
        el = line.split(' ')
        command = el.pop(0)
        el.insert(0, 'pida')
        return command, el

    def cb_activate(self, source, command, args, filename):
        pass

class ContextPopup(ContextGenerator, Popup):

    def __init__(self, cb, name):
        Popup.__init__(self, cb)
        ContextGenerator.__init__(self, cb, name)

    def popup(self, filename, time):
        self.aargs = [filename]
        self.clear()
        self.generate()
        self.add_separator()
        self.add_item('configure', 'Configure these shortcuts.',
                       self.cb_configure, [])
        Popup.popup(self, time)

    def add_item(self, stock, name, cb, cbargs):
        if stock.startswith('stock:'):
            stock = stock.replace('stock:', '', 1)
        Popup.add_item(self, stock, name, cb, cbargs)

    def cb_configure(self, *args):
        self.cb.action_showshortcuts()

    def cb_openvim(self, menu, (filename,)):
        self.cb.action_openfile(filename)

    def cb_activate(self, menu, (command, args, aargs)):
        #assume just filename for now
        fn = aargs.pop()
        if '<fn>' in args:
            args[args.index('<fn>')] = fn
        else:
            args.append(fn)
        self.cb.action_newterminal(command, args)
    
class ContextToolbar(ContextGenerator, Toolbar):
    def __init__(self, cb, name):
        Toolbar.__init__(self, cb)
        ContextGenerator.__init__(self, cb, name)
        self.generate()

    def add_item(self, stock, name, cb, cbargs):
        if stock.startswith('stock:'):
            stock = stock.replace('stock:', '', 1)
        self.add_button(stock, cb, name, cbargs)

    def cb_activate(self, button, command, args, aargs):
        self.cb.action_newterminal(command, args)
       
    def refresh(self):
        self.clear()
        self.generate()

    def clear(self):
        for i in self.win.get_children():
            self.win.remove(i)


class Plugin(object):
    ICON = 'fullscreen'
    DICON = 'fullscreen', 'Detach window.'
    NAME = 'Plugin'
    DETACHABLE = False

    def __init__(self, cb):
        self.cb = cb
        
        # main box
        self.win = gtk.VBox()
        self.win.show()
        
        # tool bar        
        self.bar = gtk.HBox()
        self.win.pack_start(self.bar, expand=False)
        self.bar.show()


        ## The control bar
        self.ctlbar = gtk.HBox()
        self.bar.pack_start(self.ctlbar)
        self.ctlbar.show()
    
        #self.vtgicon = self.cb.icons.get_image('stock_apply', 10)
        #self.vtsicon = self.cb.icons.get_image('stock_cancel', 10)

        #self.vtbut = gtk.ToggleToolButton(stock_id=None)
        #self.ctlbar.pack_start(self.vtbut, expand=False)
        #self.vtbut.connect('toggled', self.cb_toggledview)

        # detach button
        eb = gtk.EventBox()
        self.dtbut = gtk.ToggleToolButton(stock_id=None)
        eb.add(self.dtbut)
        self.ctlbar.pack_start(eb, expand=False)
        ic = self.cb.icons.get_image(self.DICON[0], 10)
        self.dtbut.set_icon_widget(ic)
        self.dtbut.connect('toggled', self.cb_toggledetatch)
        self.cb.tips.set_tip(eb, self.DICON[1])

        #label
        self.label = gtk.Label(self.NAME)
        self.ctlbar.pack_start(self.label, expand=False)
        
        #expander
        self.sepbar = Sepbar(self.cb)
        self.sepbar.connect(self.cb_sep_rclick, self.cb_sep_dclick)
        self.ctlbar.pack_start(self.sepbar.win, padding=6)

        # shortcut bar
        self.shortbar = gtk.HBox()
        self.bar.pack_start(self.shortbar, expand=False)

        ## custom tool bar
        #self.cusbar = gtk.HBox()
        #self.bar.pack_start(self.cusbar, expand=False)

        self.cusbar = Toolbar(self.cb)
        self.bar.pack_start(self.cusbar.win, expand=False)

        self.transwin = gtk.VBox()
        self.transwin.show()
        self.win.pack_start(self.transwin, expand=False)

        #message dialog
        self.msgbox = Messagebox(self.cb)
        self.transwin.pack_start(self.msgbox.win, expand=False)

        #question dialog
        self.qstbox = Questionbox(self.cb)
        self.transwin.pack_start(self.qstbox.win, expand=False)

        #option dialog
        self.optbox = Optionbox(self.cb)
        self.transwin.pack_start(self.optbox.win, expand=False)

        ## content area
        self.frame = gtk.VBox()
        self.win.pack_start(self.frame)
       

        # The popup menu
        self.popup = Popup(self.cb)

        self.populate_widgets()
        self.connect_widgets()

        self.frame.show_all()
        self.win.show_all()

    def cb_sep_rclick(self, event):
        self.popup.popup(event.time)

    def cb_sep_dclick(self, event):
        pass

    def populate_widgets(self):
        pass

    def connect_widgets(self):
        pass

    def message(self, message):
        self.msgbox.message(message)

    def question(self, message, callback):
        self.qstbox.question(message, callback)

    def option(self, message, opts, callback):
        self.optbox.option(message, opts, callback)

    def query(self, message, options, callback):
        if len(options):
            self.option(message, options, callback)
        else:
            self.question(message, callback)

    def attach(self, *a):
        self.win.reparent(self.oldparent)
        self.dwin.destroy()
    
    def detatch(self):
        self.oldparent = self.win.get_parent()
        self.dwin = Winparent(self.cb, self)

    def add(self, widget, *args):
        self.frame.pack_start(widget, *args)

    def add_button(self, stock, callback, tooltip='None Set!', cbargs=[]):
        self.popup.add_item(stock, tooltip, callback, cbargs)
        return self.cusbar.add_button(stock, callback, tooltip, cbargs)

    
    def add_separator(self):
        self.popup.add_separator()
        self.cusbar.add_separator()
        
    def cb_alternative(self):
        pass
    
    def cb_sepbar_rclick(self):
        pass

    def cb_sepbar_rclick(self):
        pass

    def cb_toggledview(self, *a):
        self.check_visibility()
    
    def cb_toggledetatch(self, *a):
        if self.dtbut.get_active():
            if self.DETACHABLE:
                self.detatch()
            else:
                self.cb_alternative()
                self.dtbut.set_active(False)
        else:
            if self.DETACHABLE:
                self.attach()
        

    def cb_shrink(self, *a):
        self.shrink()

    def cb_grow(self, *a):
        self.grow()

    def grow(self):
        nh = self.win.size_request()[1] + 64
        nh = 64 * divmod(nh, 64)[0]
        self.win.set_size_request(-1, nh)       

    def shrink(self):
        nh = self.win.size_request()[1] - 64
        if nh < 64:
            nh = 64
        else:
            nh = 64 * divmod(nh, 64)[0]
        self.win.set_size_request(-1, nh)      

    def check_visibility(self):
        #self.set_visibility(not self.vtbut.get_active())
        self.set_visibility(True)
    
    def set_visibility(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.ctlbar.show_all()

    def hide(self):
        self.frame.hide_all()
        #self.frame.set_size_request(0, 0)
        self.cusbar.hide_all()
        #self.vtbut.set_icon_widget(self.vtgicon)

    def show(self):
        self.frame.show_all()
        #self.frame.set_size_request(-1, -1)
        self.cusbar.show_all()
        #self.vtbut.set_icon_widget(self.vtsicon)
    
    def log(self, message, level):
        text = '%s: %s' % (self.NAME, message)
        self.cb.action_log(self.NAME, message, level)

    def debug(self, message):
        self.log(message, 0)

    def info(self, message):
        self.log(message, 1)

    def warn(self, message):
        self.log(message, 2)

    def error(self, message):
        self.log(message, 3)

    def evt_init(self):
        self.msgbox.hide()
        self.optbox.hide()
        self.qstbox.hide()
