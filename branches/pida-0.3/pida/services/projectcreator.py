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

import pida.core.service as service

defs = service.definitions

import pida.pidagtk.gladeview as gladeview

import os
import gtk
import gobject

class project_creator_view(gladeview.glade_view):
    
    SHORT_TITLE = 'Create Project'
    LONG_TITLE = 'pIDA new project wizard'

    glade_file_name = 'project-creator.glade'

    def on_checkout_checkbox__clicked(self, checkbox):
        act = checkbox.get_active()
        self.get_widget('checkout_table').set_sensitive(act)

    def on_createdir_checkbox__clicked(self, checkbox):
        act = checkbox.get_active()
        self.get_widget('createdir_table').set_sensitive(act)

    def on_ok_button__clicked(self, button):
        name = self.get_widget('name_entry').get_text()
        combo = self.get_widget('projecttype_combo')
        model = combo.get_model()
        aiter = combo.get_active_iter()
        typename = model.get_value(aiter, 0)
        self.service.call('create', project_name=name,
                                    project_type = typename)

    def set_project_types(self, types):
        combo = self.get_widget('projecttype_combo')
        model = gtk.ListStore(gobject.TYPE_STRING)
        combo.set_model(model)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        for name in types:
            model.append([name])
        combo.set_active(0)
        combo.show_all()

class project_creator(service.service):

    single_view_type = project_creator_view
    single_view_book = 'view'

    def init(self):
        self.__projectsdir = os.path.join(self.boss.pida_home, 'projects')

    class project_created(defs.event):
        pass

    def cmd_create_interactive(self):
        view = self.create_single_view()
        types = self.boss.call_command('projecttypes',
            'get_project_type_names')
        view.set_project_types(types)

    def cmd_create(self, project_name, project_type):
        typedir = os.path.join(self.__projectsdir, project_type)
        if os.path.isdir(typedir):
            filepath = os.path.join(typedir, project_name)
            f = open(filepath, 'w')
            f.write('# Pida Project File\n')
            f.close()
            self.events.emit('project_created')
        else:
            self.log.info('project directory "%s" vanished', typedir)

Service = project_creator
