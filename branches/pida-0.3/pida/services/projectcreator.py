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
    LONG_TITLE = ''

    glade_file_name = 'project-creator.glade'

    def init_glade(self):
        self.__name_entry = self.get_widget('name_entry')
        self.__file_chooser = self.get_widget('filename_chooser')
        self.__type_combo = self.get_widget('projecttype_combo')

    def on_ok_button__clicked(self, button):
        project_name = self.__name_entry.get_text()
        project_dir = self.__file_chooser.get_filename()
        typename = self.get_combo_active_text(self.__type_combo)
        self.service.call('create', project_name=project_name,
                                    project_directory=project_dir,
                                    project_type_name=typename)

    def get_combo_active_text(self, combo):
        model = combo.get_model()
        aiter = combo.get_active_iter()
        return model.get_value(aiter, 0)

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
    single_view_book = 'content'

    def init(self):
        self.__projectsdir = os.path.join(self.boss.pida_home, 'projects')

    class project_created(defs.event):
        pass

    def cmd_create_interactive(self):
        view = self.create_single_view()
        types = self.boss.call_command('projecttypes',
            'get_project_type_names')
        view.set_project_types(types)

    def cmd_create(self, project_name, project_directory, project_type_name):
        project_file_name = os.path.join(project_directory,
                                         '%s.pidaproject' % project_name)
        f = open(project_file_name, 'w')
        f.write('#%s\n' % project_type_name)
        f.close()
        self.boss.call_command('projectmanager', 'add_project',
            project_file=project_file_name)

Service = project_creator
