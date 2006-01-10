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

import pida.pidagtk.contentview as contentview
import pida.pidagtk.filedialogs as filedialogs

import os
import gtk
import gobject

class project_creator_view(contentview.content_view):
    
    SHORT_TITLE = 'Create Project'
    LONG_TITLE = ''

    ICON_NAME = 'project'

    def init(self):
        self.widget.set_border_width(6)
        title = gtk.Label()
        self.widget.pack_start(title, expand=False, padding=6)
        title.set_markup('<big><b>Create new project</b></big>')
        title.set_alignment(0, 0.5)
        lsz = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        wsz = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False, padding=3)
        name_label = gtk.Label('Name')
        hb.pack_start(name_label, expand=False, padding=3)
        lsz.add_widget(name_label)
        name_label.set_alignment(0, 0.5)
        self.__name_entry = gtk.Entry()
        hb.pack_start(self.__name_entry)
        wsz.add_widget(self.__name_entry)
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False, padding=3)
        file_label = gtk.Label('Save in')
        hb.pack_start(file_label, expand=False, padding=3)
        lsz.add_widget(file_label)
        file_label.set_alignment(0, 0.5)
        self.__file_chooser = filedialogs.FolderButton()
        hb.pack_start(self.__file_chooser)
        wsz.add_widget(self.__file_chooser)
        #self.__file_chooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False, padding=3)
        type_label = gtk.Label('Type')
        hb.pack_start(type_label, expand=False, padding=3)
        lsz.add_widget(type_label)
        type_label.set_alignment(0, 0.5)
        self.__type_combo = gtk.combo_box_new_text()
        hb.pack_start(self.__type_combo)
        wsz.add_widget(self.__type_combo)
        bb = gtk.HButtonBox()
        self.widget.pack_start(bb, expand=False)
        self.__ok_but = gtk.Button(stock=gtk.STOCK_OK)
        bb.pack_start(self.__ok_but, padding=6)
        self.__ok_but.connect('clicked', self.on_ok_button__clicked)
        self.__cancel_but = gtk.Button(stock=gtk.STOCK_CANCEL)
        bb.pack_start(self.__cancel_but, padding=6)
        self.__cancel_but.connect('clicked', self.on_cancel_button__clicked)

    def on_ok_button__clicked(self, button):
        project_name = self.__name_entry.get_text()
        project_dir = self.__file_chooser.get_filename()
        typename = self.__type_combo.get_active_text()
        self.service.call('create', project_name=project_name,
                                    project_directory=project_dir,
                                    project_type_name=typename)
        self.close()

    def on_cancel_button__clicked(self, button):
        self.close()

    def set_project_types(self, types):
        self.__type_combo.get_model().clear()
        for typename in types:
            self.__type_combo.append_text(typename)
        self.__type_combo.set_active(0)
        self.__type_combo.show_all()

    def set_project_dir(self, path):
        self.__file_chooser.set_filename(path)

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
        view.set_project_dir(self.__projectsdir)

    def cmd_create(self, project_name, project_directory, project_type_name):
        project_file_name = os.path.join(project_directory,
                                         '%s.pidaproject' % project_name)
        f = open(project_file_name, 'w')
        f.write('#%s\n[general]\nsource_directory=%s\n' %
                (project_type_name, os.path.dirname(project_file_name)))
        f.close()
        self.boss.call_command('projectmanager', 'add_project',
            project_file=project_file_name)
        class dummy_project:
            name = project_name
        self.boss.call_command('projectmanager', 'edit', projects=None,
                                current_project = dummy_project())

Service = project_creator
