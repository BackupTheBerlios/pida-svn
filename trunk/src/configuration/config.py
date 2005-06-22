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

"""Provides the widgets for dynamically generating a configuration editor."""

# GTK import
import gtk
# System imports
import textwrap
#Pida imports
import pida.gtkextra as gtkextra

class ConfigWidget(object):
    """
    A widget holder which can save or load its state.
    
    This class is largely abstract, and must be overriden for useful use. See
    the examples below.
    """
    def __init__(self, cb, widget, section, key):
        """
        Constructor
        
        @param cb: An instance of the application class
        @type cb: pida.main.Application

        @param widget: The actual widget for the holder.
        @type widget: gtk.Widget

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        # The application class
        self.cb = cb
        # A local referenec to the options object
        self.opts = self.cb.opts
        # Store information about the configuration we will need.
        self.section = section
        self.key = key
        # Build the widget
        # Containers
        self.win = gtk.VBox()
        hb = gtk.HBox()
        self.win.pack_start(hb)
        # Name label
        self.name_l = gtk.Label()
        self.name_l.set_markup('<span weight="bold">'
                               '%s</span>' % self.get_name())
        hb.pack_start(self.name_l, padding=4, expand=True)
        self.name_l.set_size_request(100, -1)
        # Actual widget
        self.widget = widget
        hb.pack_start(widget, padding=4)
        hb2 = gtk.HBox()
        self.win.pack_start(hb2)
        # Help label
        self.help_l = gtk.Label()
        self.help_l.set_markup(self.get_help())
        hb2.pack_start(self.help_l, expand=False, padding=4)

    def get_name(self):
        """
        Return a beautified name for the configuration option.
        """
        return ' '.join(self.key.split('_')[::-1])
   
    def get_help(self):
        """
        Return the help for the option.
        """
        help = self.opts.help[(self.section, self.key)]
        return '\n'.join(textwrap.wrap(help, 60))

    def set_value(self, value):
        """
        Set the configuration value to the widget's value.

        @param value: The value to set the widget to.
        @type value: string
        """
        self.opts.set(self.section, self.key, value)
    
    def value(self):
        """
        Get the configuration value from the options database.
        """
        return self.opts.get(self.section, self.key)

    def load(self):
        """
        Called to load data from the options database into the widget.
        """
        pass

    def save(self):
        """
        Called to save data from the widget into the opitons database.
        """
        pass

class ConfigEntry(ConfigWidget):
    """
    An entry widget for plain configuration strings.
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtk.Entry()
        ConfigWidget.__init__(self, cb, widget, section, key)

    def load(self):
        """
        Set the entry widget text to the option database value.
        """
        self.widget.set_text(self.value())

    def save(self):
        """
        Set the option database value to the widgets text.
        """
        self.set_value(self.widget.get_text())

class ConfigBoolen(ConfigWidget):
    """
    A checkbox widget forr boolean configuration values.
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtk.CheckButton(label="Yes")
        ConfigWidget.__init__(self, cb, widget, section, key)
       
    def stob(self, s):
        """
        Convert a string to a boolean. 
        
        This method is deprecated and should not be used
        """
        return s.lower().startswith('t')
 
    def load(self):
        """
        Load the checkbox active status from the options database.
        """
        enabled = bool(int(self.value()))
        self.widget.set_active(enabled)

    def save(self):
        """
        Save the checkbox active state to the options database.
        """
        val = str(int(self.widget.get_active()))
        self.set_value(val)

class ConfigFont(ConfigWidget):
    """
    A font selection dialogue that takes its values from the config database.
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtk.FontButton()
        ConfigWidget.__init__(self, cb, widget, section, key)
        
    def load(self):
        """
        Load th font value from the options database.
        """
        fn = self.value()
        self.widget.set_font_name(fn)

    def save(self):
        """
        Save the font value to the options database.
        """
        self.set_value(self.widget.get_font_name())


class ConfigFile(ConfigWidget):
    """
    A widget that represents a file selection entry and dialogue button.
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtkextra.FileButton(cb)
        ConfigWidget.__init__(self, cb, widget, section, key)
        
    def load(self):
        """
        Load the filename from the options database.
        """
        fn = self.value()
        self.widget.set_filename(fn)

    def save(self):
        """
        Save the filename to the options database.
        """
        self.set_value(self.widget.get_filename())

class ConfigFolder(ConfigFile):
    """
    A widget that represents a directory entry and dialogue button.
    
    (Note called "Folder" because GTK calls it a "Folder").
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtkextra.FolderButton(cb)
        ConfigWidget.__init__(self, cb, widget, section, key)
       
class ConfigColor(ConfigWidget):
    """
    A widget for a colour selection button and dialogue.
    """
    def __init__(self, cb, section, key):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param section: The configuration section that the widget is for.
        @type section: string

        @param key: The configuration key that the widget is for
        @type key: string
        """
        widget = gtk.ColorButton()
        ConfigWidget.__init__(self, cb, widget, section, key)

    def load(self):
        """
        Load the colour from the options database.
        """
        cn = self.value()
        col = self.widget.get_colormap().alloc_color(cn)
        self.widget.set_color(col)

    def save(self):
        """
        Save the colour to the options database.
        """
        c = self.widget.get_color()
        v = gtk.color_selection_palette_to_string([c])
        self.set_value(v)

class ListTree(gtk.TreeView):
    """
    A treeview control for switching a notebook's tabs.
    """
    def __init__(self, cb, configeditor):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application

        @param configeditor: The configuration editor that the list is used
            for.
        @type configeditor: pida.config.ConfigEditor
        """
        self.cb = cb
        self.configeditor = configeditor
        self.store = gtk.ListStore(str, int)
        gtk.TreeView.__init__(self, self.store)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", renderer, markup=0)
        self.append_column(column)
        self.set_headers_visible(False)
        self.connect('cursor-changed', self.cb_select)

    def cb_select(self, *args):
        """
        Callback when an item in the list is selected.
        """
        path = self.store.get_iter(self.get_cursor()[0])
        tid = self.store.get_value(path, 1)
        # call the config editor's callback
        self.configeditor.cb_select(tid)

    def populate(self, names):
        """
        Populate the list with the required names.
        """
        self.store.clear()
        for name, i in names:
            s = '%s' % name
            self.store.append((s, i))

class ConfigEditor(object):
    """
    A top-level window containing dynamically generated controls for
    configuration information from the Pida options database.
    """
    def __init__(self, cb):
        """
        Constructor.
        
        @param cb: An instance of the application class.
        @type cb: pida.main.Application
        """
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
        """
        Load the initial database options into the config editor, and generate
        the required widgets.
        """
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
                ctype = TYPES[self.get_type(section, option)]
                cw = ctype(self.cb, section, opt)
                box.pack_start(cw.win, expand=False, padding=4)
                self.controls[(section, opt)] = cw
                box.pack_start(gtk.HSeparator(), expand=False, padding=4)
        self.tree.populate(pages)

    def get_type(self, section, option):
        return self.opts.types[(section, opt)]

    def load(self):
        """
        Load the configuration information from the database.
        """
        for section in self.opts.sections():
            for opt in self.opts.options(section):
                self.controls[(section, opt)].load()

    def save(self):
        """
        Save the configuration information to the database.
        """
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
