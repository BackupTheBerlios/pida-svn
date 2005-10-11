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
import gobject

class ListedTab(gtk.HBox):

    __gsignals__ = {'clicked' : (
                    gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_PYOBJECT,))}

    def __init__(self):
        self.__filename = None

    def __set_filename(self, filename):
        self.__filename = filename
    
    def __get_filename(self):
        return self.__filename

    
    def do_init(self, project_registry):
        self.project_registry = project_registry
        
        self.win = gtk.Window()
        self.win.set_title('PIDA Project Editor')
        self.win.set_size_request(600,480)
        self.win.set_transient_for(self.pida.mainwindow)

        mainbox = gtk.HBox()
        self.win.add(mainbox)

        leftbox = gtk.VBox()
        mainbox.pack_start(leftbox)

        self.projects = ProjectTree()
        leftbox.pack_start(self.projects.win)
        self.projects.connect_select(self.cb_project_select)
        self.projects.populate(self.project_registry)

        rightbox = gtk.VBox()
        mainbox.pack_start(rightbox)

        attrbox = gtk.VBox()
        rightbox.pack_start(attrbox)


        hbox = gtk.HBox()
        attrbox.pack_start(hbox, expand=False, padding=4)
        namelabel = gtk.Label('name')
        hbox.pack_start(namelabel, expand=False, padding=4)
        self.nameentry = gtk.Entry()
        hbox.pack_start(self.nameentry)

        self.attribute_widgets = {}
        for attribute in PROJECT_ATTRIBUTES:
            hbox = gtk.HBox()
            attrbox.pack_start(hbox, expand=False, padding=4)
            name = attribute[0]
            namelabel = gtk.Label(name)
            hbox.pack_start(namelabel, expand=False, padding=4)
            entry = attribute[3]()
            hbox.pack_start(entry)
            self.attribute_widgets[name] = entry
        
        # Button Bar
        cb = gtk.HBox()
        rightbox.pack_start(cb, expand=False, padding=2)
        
        # separator
        sep = gtk.HSeparator()
        cb.pack_start(sep)
        
        # reset button
        revert_b = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        cb.pack_start(revert_b, expand=False)
        revert_b.connect('clicked', self.cb_revert)

        # cancel button
        delete_b = gtk.Button(stock=gtk.STOCK_DELETE)
        cb.pack_start(delete_b, expand=False)
        delete_b.connect('clicked', self.cb_delete)
        
        # apply button
        new_b = gtk.Button(stock=gtk.STOCK_NEW)
        cb.pack_start(new_b, expand=False)
        new_b.connect('clicked', self.cb_new)
        
        # save button
        save_b = gtk.Button(stock=gtk.STOCK_SAVE)
        cb.pack_start(save_b, expand=False)
        save_b.connect('clicked', self.cb_save)
    
    def new(self):
        self.nameentry.set_text('')
        for attribute in PROJECT_ATTRIBUTES:
            attrname = attribute[0]
            self.attribute_widgets[attrname].set_text('')

    def show(self):
        self.win.show_all()

    def display(self, projectname):
        if self.project_registry.has_section(projectname):
            self.nameentry.set_text(projectname)
            for attribute in PROJECT_ATTRIBUTES:
                attrname = attribute[0]
                val = self.project_registry.get(projectname, attrname)
                self.attribute_widgets[attribute[0]].set_text(val)
            
    def projects_changed(self):
        self.project_registry.save()
        self.projects.populate(self.project_registry)
        self.do_evt('projectschanged')
            
    def cb_project_select(self, *args):
        projname = self.projects.selected(0)
        self.display(projname)
         
    def cb_new(self, *args):
        self.new()

    def cb_revert(self, *args):
        self.project_registry.load()
        self.projects_changed()

    def cb_save(self, *args):
        name = self.nameentry.get_text()
        if name:
            kw = {}
            for attrname in self.attribute_widgets:
                kw[attrname] = self.attribute_widgets[attrname].get_text()
            self.project_registry.set_project(name, **kw)
            self.projects_changed()

    def cb_delete(self, *args):
        projname = self.projects.selected(0)
        self.project_registry.delete(projname)
        self.projects_changed()
        self.projects.view.set_cursor(self.projects.model[0].path)

