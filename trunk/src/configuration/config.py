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
import textwrap
import pida.gtkextra as gtkextra

class ConfigWidget(object):
    def __init__(self, cb, widget, section, key):
        self.cb = cb
        self.setopts()
        self.section = section
        self.key = key

        self.win = gtk.VBox()
       
        hb = gtk.HBox()
        self.win.pack_start(hb)

        self.name_l = gtk.Label()
        self.name_l.set_markup('<span weight="bold">'
                               '%s</span>' % self.get_name())
        hb.pack_start(self.name_l, padding=4, expand=True)
        self.name_l.set_size_request(100, -1)

        self.widget = widget
        hb.pack_start(widget, padding=4)

        hb2 = gtk.HBox()
        self.win.pack_start(hb2)

        self.help_l = gtk.Label()
        self.help_l.set_markup(self.get_help())
        hb2.pack_start(self.help_l, expand=False, padding=4)

    def setopts(self):
        self.opts = self.cb.opts

    def get_name(self):
        return ' '.join(self.key.split('_')[::-1])
   
    def get_help(self):
        help = self.opts.help[(self.section, self.key)]
        return '\n'.join(textwrap.wrap(help, 60))

    def set_value(self, value):
        self.opts.set(self.section, self.key, value)
    
    def value(self):
        return self.opts.get(self.section, self.key)

    def load(self):
        pass

    def save(self):
        pass

class ConfigEntry(ConfigWidget):
    def __init__(self, cb, section, key):
        widget = gtk.Entry()
        ConfigWidget.__init__(self, cb, widget, section, key)

    def load(self):
        self.widget.set_text(self.value())

    def save(self):
        self.set_value(self.widget.get_text())

class ConfigBoolen(ConfigWidget):
    def __init__(self, cb, section, key):
        widget = gtk.CheckButton(label="Yes")
        ConfigWidget.__init__(self, cb, widget, section, key)
       
    def stob(self, s):
        return s.lower().startswith('t')
 
    def load(self):
        enabled = bool(int(self.value()))
        self.widget.set_active(enabled)

    def save(self):
        val = str(int(self.widget.get_active()))
        self.set_value(val)

class ConfigFont(ConfigWidget):
    def __init__(self, cb, section, key):
        widget = gtk.FontButton()
        ConfigWidget.__init__(self, cb, widget, section, key)
        
    def load(self):
        fn = self.value()
        self.widget.set_font_name(fn)

    def save(self):
        self.set_value(self.widget.get_font_name())


class ConfigFile(ConfigWidget):
    def __init__(self, cb, section, key):
        widget = gtkextra.FileButton(cb)
        ConfigWidget.__init__(self, cb, widget, section, key)
        
    def load(self):
        fn = self.value()
        self.widget.set_filename(fn)

    def save(self):
        self.set_value(self.widget.get_filename())

class ConfigFolder(ConfigFile):
    def __init__(self, cb, section, key):
        widget = gtkextra.FolderButton(cb)
        ConfigWidget.__init__(self, cb, widget, section, key)
       
class ConfigColor(ConfigWidget):
    def __init__(self, cb, section, key):
        widget = gtk.ColorButton()
        ConfigWidget.__init__(self, cb, widget, section, key)
    def load(self):
        cn = self.value()
        col = self.widget.get_colormap().alloc_color(cn)
        self.widget.set_color(col)
    def save(self):
        c = self.widget.get_color()
        v = gtk.color_selection_palette_to_string([c])
        self.set_value(v)


class ListTree(gtk.TreeView):

    def __init__(self, cb, ce):
        self.cb = cb
        self.ce = ce
        self.store = gtk.ListStore(str, int)
        gtk.TreeView.__init__(self, self.store)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", renderer, markup=0)
        self.append_column(column)
        self.set_headers_visible(False)
        self.connect('cursor-changed', self.cb_select)

    def cb_select(self, *args):
        path = self.store.get_iter(self.get_cursor()[0])
        tid = self.store.get_value(path, 1)
        self.ce.cb_select(tid)

    def populate(self, names):
        self.store.clear()
        for name, i in names:
            s = '%s' % name
            self.store.append((s, i))



class ConfigEditor(object):
    def __init__(self, cb):
        self.cb = cb

        # main window
        self.win = gtk.Window()
        self.win.set_title('PIDA Configuration Editor')
        self.win.set_transient_for(self.cb.cw)
        self.win.connect('destroy', self.cb_cancel)

        # top container
        hbox = gtk.HBox()
        self.win.add(hbox)

        self.lmodel = gtk.ListStore(str, int)
        self.tree = ListTree(self.cb, self)

        hbox.pack_start(self.tree, expand=False, padding=6)

        vbox = gtk.VBox()
        hbox.pack_start(vbox)
        
        # notebook
        self.nb = gtk.Notebook()
        vbox.pack_start(self.nb, padding=4)
        self.nb.set_show_tabs(False)

        # Button Bar
        cb = gtk.HBox()
        vbox.pack_start(cb, expand=False, padding=2)
        
        # separator
        sep = gtk.HSeparator()
        cb.pack_start(sep)

        # cancel button
        self.cancel_b = gtk.Button(stock=gtk.STOCK_CANCEL)
        cb.pack_start(self.cancel_b, expand=False)
        self.cancel_b.connect('clicked', self.cb_cancel)
        
        # reset button
        self.reset_b = gtk.Button(stock=gtk.STOCK_UNDO)
        cb.pack_start(self.reset_b, expand=False)
        self.reset_b.connect('clicked', self.cb_reset)

        # apply button
        self.apply_b = gtk.Button(stock=gtk.STOCK_APPLY)
        cb.pack_start(self.apply_b, expand=False)
        self.apply_b.connect('clicked', self.cb_apply)
        
        # save button
        self.save_b = gtk.Button(stock=gtk.STOCK_SAVE)
        cb.pack_start(self.save_b, expand=False)
        self.save_b.connect('clicked', self.cb_save)
        
        self.controls = {}
        self.setopts()
        self.initialize()

    def setopts(self):
        self.opts = self.cb.opts

    def initialize(self):
        pages = []
        sects =  self.opts.sections()
        sects.sort()
        for section in sects:
            box = gtk.VBox()
            sectlab = ''.join([section[0].upper(), section[1:]])
            tid = self.nb.append_page(box, gtk.Label(sectlab))
            pages.append((sectlab, tid))
            opts = self.opts.options(section)
            opts.sort()
            for opt in opts:
                ctype = TYPES[self.opts.types[(section, opt)]]
                cw = ctype(self.cb, section, opt)
                box.pack_start(cw.win, expand=False, padding=4)
                self.controls[(section, opt)] = cw
                box.pack_start(gtk.HSeparator(), expand=False, padding=4)
        self.tree.populate(pages)

    def load(self):
        for section in self.opts.sections():
            for opt in self.opts.options(section):
                self.controls[(section, opt)].load()

    def save(self):
        for section in self.opts.sections():
            for opt in self.opts.options(section):
                self.controls[(section, opt)].save()
        self.opts.write()
        self.cb.evt('reset')

    def show(self):
        self.load()
        self.win.show_all()

    def hide(self):
        self.win.hide_all()
        self.win.destroy()

    def cb_select(self, tid):
        self.nb.set_current_page(tid)

    def cb_reset(self, *args):
        self.show()

    def cb_apply(self, *args):
        self.save()

    def cb_cancel(self, *args):
        self.hide()

    def cb_save(self, *args):
        self.save()
        self.hide()

TYPES = {None: ConfigEntry,
         'boolean': ConfigBoolen,
         'font': ConfigFont,
         'file': ConfigFile,
         'dir': ConfigFolder,
         'color':ConfigColor}

if __name__ == '__main__':
    w = ConfigEditor(None)
    w.show()
    gtk.main()
