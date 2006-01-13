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


import gtk
import filedialogs

NAME_MU = """<span weight="bold">%s</span>"""
DOC_MU = """<span>%s</span>"""

def get_widget(rtype):
    name = rtype.__name__
    if name in ['string']:
        return types.entry
    elif name in dir(types):
        return getattr(types, name)
    elif name.startswith('directory'):
        return types.directory
    elif name.startswith('file'):
        return types.file
    elif name.startswith('int'):
        return types.integer
    elif name.startswith('stringlist'):
        return types.list
    else:
        return types.entry

class registry_widget(gtk.VBox):
    """
    A widget holder which can save or load its state.
    
    This class is largely abstract, and must be overriden for useful use. See
    the examples below.
    """
    def __init__(self, widget, option):
        """
        Constructor
        
        @param cb: An instance of the application class
        @type cb: pida.main.Application

        @param widget: The actual widget for the holder.
        @type widget: gtk.Widget
        """
        gtk.VBox.__init__(self)
        self.__option = option
        # Build the widget
        # Containers
        container = gtk.HBox(spacing=6)
        self.pack_start(container)
        self.__name_label = gtk.Label()
        container.pack_start(self.__name_label, expand=False)
        self.__name_label.show()
        self.__name_label.set_alignment(0, 0.5)
        self.__name_label.set_markup(NAME_MU % self.get_name().capitalize())
        self.__widget = widget
        container.pack_start(widget, padding=2)
        container.show()
        self.__help_label = gtk.Label()
        self.pack_start(self.__help_label, expand=False)
        self.__help_label.show()
        self.__help_label.set_markup(DOC_MU % self.get_help())

    def get_name(self):
        """
        Return a beautified name for the configuration option.
        """
        return self.option.name.replace('_', ' ')
   
    def get_help(self):
        """
        Return the help for the option.
        """
        return self.option.doc

    def set_value(self, value):
        """
        Set the configuration value to the widget's value.

        @param value: The value to set the widget to.
        @type value: string
        """
        self.option.value = value
    
    def get_value(self):
        """
        Get the configuration value from the options database.
        """
        return self.option.value

    value = property(get_value, set_value)

    def get_name_label(self):
        return self.__name_label
    
    name_label = property(get_name_label)

    def get_widget(self):
        return self.__widget

    widget = property(get_widget)

    def get_option(self):
        return self.__option

    option = property(get_option)

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

class types(object):

    class entry(registry_widget):
        """
        An entry widget for plain configuration strings.
        """
        def __init__(self, option):
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
            registry_widget.__init__(self, widget, option)
        def load(self):
            """
            Set the entry widget text to the option database value.
            """
            self.widget.set_text('%s' % self.value)

        def save(self):
            """
            Set the option database value to the widgets text.
            """
            self.set_value(self.widget.get_text())

    class password_entry(registry_widget):
        """
        An entry widget for hidden configuration strings.
        """
        def __init__(self, option):
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
            widget.set_visibility(False)
            registry_widget.__init__(self, widget, option)


    class boolean(registry_widget):
        """
        A checkbox widget forr boolean configuration values.
        """
        def __init__(self, option):
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
            registry_widget.__init__(self, widget, option)
           
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
            self.widget.set_active(self.value)

        def save(self):
            """
            Save the checkbox active state to the options database.
            """
            self.set_value(self.widget.get_active())

    class font(registry_widget):
        """
        A font selection dialogue that takes its values from the config database.
        """
        def __init__(self, option):
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
            registry_widget.__init__(self, widget, option)
            
        def load(self):
            """
            Load th font value from the options database.
            """
            fn = self.value
            self.widget.set_font_name(fn)

        def save(self):
            """
            Save the font value to the options database.
            """
            self.set_value(self.widget.get_font_name())

    class file(registry_widget):
        """
        A widget that represents a file selection entry and dialogue button.
        """
        def __init__(self, option):
            """
            Constructor.
            
            @param cb: An instance of the application class.
            @type cb: pida.main.Application

            @param section: The configuration section that the widget is for.
            @type section: string

            @param key: The configuration key that the widget is for
            @type key: string
            """
            widget = filedialogs.FileButton()
            #widget.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
            registry_widget.__init__(self, widget, option)
            
        def load(self):
            """
            Load the filename from the options database.
            """
            fn = self.option.value
            self.widget.set_filename(fn)

        def save(self):
            """
            Save the filename to the options database.
            """
            self.set_value(self.widget.get_filename())

    class directory(file):
        """
        A widget that represents a directory entry and dialogue button.
        
        (Note called "Folder" because GTK calls it a "Folder").
        """
        def __init__(self, option):
            """
            Constructor.
            
            @param cb: An instance of the application class.
            @type cb: pida.main.Application

            @param section: The configuration section that the widget is for.
            @type section: string

            @param key: The configuration key that the widget is for
            @type key: string
            """
            widget = filedialogs.FolderButton()
            #widget.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
            registry_widget.__init__(self, widget, option)
           
    class color(registry_widget):
        """
        A widget for a colour selection button and dialogue.
        """
        def __init__(self, option):
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
            registry_widget.__init__(self, widget, option)

        def load(self):
            """
            Load the colour from the options database.
            """
            cn = self.value
            col = self.widget.get_colormap().alloc_color(cn)
            self.widget.set_color(col)

        def save(self):
            """
            Save the colour to the options database.
            """
            c = self.widget.get_color()
            v = gtk.color_selection_palette_to_string([c])
            self.set_value(v)

    class integer(entry):
        MIN = 0
        MAX = 99
        STEP = 1
        
        def __init__(self, option):
            if hasattr(option, 'lower'):
                adjvals = option.lower, option.upper, option.step
            else:
                adjvals = self.MIN, self.MAX, self.STEP
            adj = gtk.Adjustment(0, *adjvals)
            widget = gtk.SpinButton(adj)
            registry_widget.__init__(self, widget, option)

        def load(self):
            """
            Set the entry widget text to the option database value.
            """
            self.widget.set_value(self.value)

        def save(self):
            """
            Set the option database value to the widgets text.
            """
            self.set_value(int(self.widget.get_value()))

    class list(entry):
        def __init__(self, option):
            widget = gtk.combo_box_new_text()
            if hasattr(option, 'choices'):
                for choice in getattr(option, 'choices'):
                    widget.append_text(choice)
            registry_widget.__init__(self, widget, option)
                    
        def load(self):
            for i, row in enumerate(self.widget.get_model()):
                if row[0] == self.value:
                    self.widget.set_active(i)
                    break

        def save(self):
            actiter = self.widget.get_active_iter()
            act = None
            if actiter:
                act = self.widget.get_model().get_value(actiter, 0)
            self.set_value(act)

    class listtree(gtk.TreeView):
        """
        A treeview control for switching a notebook's tabs.
        """
        def __init__(self, configeditor):
            """
            Constructor.
            
            @param cb: An instance of the application class.
            @type cb: pida.main.Application

            @param configeditor: The configuration editor that the list is used
                for.
            @type configeditor: pida.config.ConfigEditor
            """
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

    class embedfile(registry_widget):
        def __init__(self, option):
            tagtable = gtk.TextTagTable()
            tag = gtk.TextTag('default')
            tag.set_property('font', 'Monospace 8')
            tagtable.add(tag)
            buffer = gtk.TextBuffer(tagtable)
            widget = gtk.TextView(buffer)
            registry_widget.__init__(self, widget, option)

        def load(self):
            filename = self.value
            f = open(filename)
            buf = self.widget.get_buffer()
            buf.set_text('')
            buf.insert_with_tags_by_name(buf.get_start_iter(), f.read(), 'default')
            f.close()

        def save(self):
            filename = self.value
            f = open(filename, 'w')
            f.write(self.widget.get_buffer().get_text())
            f.close()


if __name__ == '__main__':
    w = ConfigEditor()
    w.show()
    gtk.main()
