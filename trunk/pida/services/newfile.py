# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Ali Afshar aafshar@gmail.com

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

import os

import pida.core.service as service

defs = service.definitions
types = service.types

import pida.pidagtk.contentview as contentview

import gtk

class new_file_options(gtk.VBox):
    
    def __init__(self):
        super(new_file_options, self).__init__(spacing=6)
        hb = gtk.HBox(spacing=6)
        self.pack_start(hb, expand=False)
        copycheck = gtk.CheckButton(label='License')
        copycheck.connect('toggled', self.cb_copy_toggled)
        hb.pack_start(copycheck, expand=False)
        self.__copy_combo = gtk.combo_box_new_text()
        hb.pack_start(self.__copy_combo)
        copycheck.set_active(False)
        self.__copy_combo.set_sensitive(False)
        hb = gtk.HBox(spacing=6)
        self.pack_start(hb, expand=False)
        copycheck = gtk.CheckButton(label='Comment Style')
        copycheck.connect('toggled', self.cb_comment_toggled)
        hb.pack_start(copycheck, expand=False)
        self.__comment_combo = gtk.combo_box_new_text()
        hb.pack_start(self.__comment_combo)
        copycheck.set_active(True)
        self.show_all()

    def cb_copy_toggled(self, tgl):
        self.__copy_combo.set_sensitive(tgl.get_active())

    def cb_comment_toggled(self, tgl):
        self.__comment_combo.set_sensitive(tgl.get_active())
            
class new_file(service.service):

    class locations(defs.optiongroup):
        """Options relating to the location of new files."""
        class start_in_current_project_directory(defs.option):
            """Whether files will be made in the current project directory."""
            rtype = types.boolean
            default = True

    def cmd_create_interactive(self, directory=None,
                               mkdir=False):
        if directory is None:
            directory = os.getcwd()
            if self.opt('locations', 'start_in_current_project_directory'):
                proj = self.boss.call_command('projectmanager',
                                              'get_current_project')
                if proj is not None:
                    directory = proj.source_directory
        if mkdir:
            def _callback(name):
                path = os.path.join(directory, name)
                os.mkdir(path)
            prompt = 'Directory Name'
            self.boss.call_command('window', 'input',
                               callback_function=_callback,
                                prompt=prompt)
        else:
            view = self.create_view()
            view.set_current_folder(directory)
            view.run()
            

    def cmd_create(self, filename):
        f = open(filename, 'w')
        f.close()

    def create_view(self):
        chooser = gtk.FileChooserDialog("Create New File",
                        self.boss.get_main_window(),
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                        gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        chooser.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        try:
            chooser.set_do_overwrite_confirmation(True)
        except AtributeError:
            pass
        chooser.connect('response', self.cb_response)
        options = new_file_options()
        #chooser.vbox.pack_start(options, expand=False)
        return chooser

    def cb_response(self, dlg, response):
        if response == gtk.RESPONSE_ACCEPT:
            filename = dlg.get_filename()
            self.call('create', filename=dlg.get_filename())
            self.boss.call_command('buffermanager', 'open_file',
                                   filename=filename)
        dlg.destroy()
        

Service = new_file
