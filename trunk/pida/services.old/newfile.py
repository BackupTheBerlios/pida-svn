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
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.icons as icons
import pida.pidagtk.filedialogs as filedialogs
import pida.pidagtk.tree as tree
import gtk

class TemplateTreeItem(tree.TreeItem):
    def __get_markup(self):
        return self.value.name
    markup = property(__get_markup)

class TemplateTree(tree.Tree):
    pass

class TemplateGroup(object):

    def __init__(self, name):
        self.name = name

class NewfileEditor(contentbook.ContentView):
    
    def populate(self):
        # General packing
        ls = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        vs = gtk.SizeGroup(gtk.SIZE_GROUP_VERTICAL)
        self.set_spacing(6)
        # filename box
        filename_box = gtk.HBox(spacing=6)
        self.pack_start(filename_box, expand=False)
        l = gtk.Label('Named')
        filename_box.pack_start(l, expand=False)
        vs.add_widget(l)
        self.filename_chooser = gtk.Entry()
        filename_box.pack_start(self.filename_chooser)
        filename_box.pack_start(gtk.Label('in Directory'), expand=False)
        self.directory_chooser = filedialogs.FolderButton()
        filename_box.pack_start(self.directory_chooser)
        
        templates_box = gtk.HBox()
        self.pack_start(templates_box)
        available_box = gtk.VBox()
        templates_box.pack_start(available_box, expand=False)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_NONE)
        templates_box.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        templates_box.pack_start(sw)
        templates_box = gtk.VBox()
        sw.add_with_viewport(templates_box)



        # license box
        license_box = gtk.HBox(spacing=6)
        templates_box.pack_start(license_box, expand=False)
        vs.add_widget(license_box)
        self.license_on = gtk.CheckButton(label='Use license')
        available_box.pack_start(self.license_on, expand=False)
        vs.add_widget(self.license_on)
        self.license_on.connect('toggled', self.cb_licenseon_toggled)
        self.license_chooser = gtk.combo_box_new_text()
        license_box.pack_start(self.license_chooser)

        # modeline box
        modeline_box = gtk.HBox(spacing=6)
        templates_box.pack_start(modeline_box, expand=False)
        vs.add_widget(modeline_box)
        self.modeline_on = gtk.CheckButton(label="Use Vim modeline")
        vs.add_widget(self.modeline_on)
        self.modeline_on.connect('toggled', self.cb_modelineon_toggled)
        available_box.pack_start(self.modeline_on, expand=False)
        self.modeline_chooserbox = gtk.HBox(spacing=6)
        modeline_box.pack_start(self.modeline_chooserbox)
        self.modeline_chooserbox.pack_start(gtk.Label(' Text width'), expand=False)
        widthadj = gtk.Adjustment(80, 40, 160, 1)
        self.modeline_textwidth_chooser = gtk.SpinButton(widthadj)
        self.modeline_chooserbox.pack_start(self.modeline_textwidth_chooser,
                                            expand=False)
        self.modeline_chooserbox.pack_start(gtk.Label(' Shift width'), expand=False)
        shiftadj = gtk.Adjustment(4, 1, 16, 1)
        self.modeline_shiftwidth_chooser = gtk.SpinButton(shiftadj)
        self.modeline_chooserbox.pack_start(self.modeline_shiftwidth_chooser,
                                            expand=False)
        self.modeline_chooserbox.pack_start(gtk.Label(' Tabstop'), expand=False)
        self.modeline_tabstop_chooser = gtk.SpinButton(shiftadj)
        self.modeline_chooserbox.pack_start(self.modeline_tabstop_chooser,
                                            expand=False)
        self.modeline_chooserbox.pack_start(gtk.Label(' Expand tab'), expand=False)
        self.modeline_expandtab_chooser = gtk.CheckButton()
        self.modeline_chooserbox.pack_start(self.modeline_expandtab_chooser)

        # availables box
        self.__available_list = TemplateTree()
        available_box.pack_start(self.__available_list)

        # Ok and cancel
        button_align = gtk.Alignment(1, 0.5)
        self.pack_start(button_align, expand=False)
        button_box = gtk.HBox()
        button_align.add(button_box)
        self.ok_button = icons.icons.get_text_button('yes', 'Ok')
        button_box.pack_start(self.ok_button)
        self.cancel_button = icons.icons.get_text_button('no', 'Cancel')
        button_box.pack_start(self.cancel_button)

    def cb_licenseon_toggled(self, checkbutton):
        self.license_chooser.set_sensitive(self.license_on.get_active())

    def cb_modelineon_toggled(self, checkbutton):
        self.modeline_chooserbox.set_sensitive(self.modeline_on.get_active())

    def get_newfile_options():
        license = None
        if self.license_on.get_active():
            license = self.license_chooser.get_active()
        return license

    def set_from_options(self, filename=None, directory=None, license=None,
                         modeline=None):
        self.__templates = self.boss.command('filetemplates', 'get-template-names')
        self.set_available()
        self.set_filename(filename, directory)
        self.set_license(license)
        self.set_modeline(modeline)

    def set_available(self):
        for group in self.__templates:
            g = TemplateTreeItem(group, TemplateGroup(group))
            parent = self.__available_list.add_item(g)
            for name in self.__templates[group]:
                item = TemplateTreeItem(name, TemplateGroup(name))
                self.__available_list.add_item(item, parent)


    def set_filename(self, filename, directory):
        dirpath = fname = ''
        if filename is not None:
            dirpath, fname = os.path.split(filename)
            self.directory_chooser.set_text(dirpath)
            self.filename_chooser.set_text(fname)
        elif directory is not None:
            self.directory_chooser.set_text(directory)

    def set_license(self, licensename):
        self.license_chooser.get_model().clear()
        for license in self.__templates['licenses']:
            self.license_chooser.append_text(license)
        if licensename is None:
            self.license_on.set_active(False)
            self.license_on.emit('toggled')
            self.license_chooser.set_active(0)
        else:
            self.license_on.set_active(True)
            self.license_on.emit('toggled')
            for row in self.license_chooser.get_model():
                if row[0] == license:
                    self.license_chooser.set_active_iter(row.iter)

    def set_modeline(self, modeline):
        if modeline is None:
            self.modeline_on.set_active(False)
            self.modeline_on.emit('toggled')
        else:
            self.modeline_on.set_active(True)
            self.modeline_on.emit('toggled')
            shitwidth, tabstop, expandtab, textwidth = modeline
            self.modeline_shiftwidth_chooser.set_value(shiftwidth)
            self.modeline_textwidth_chooser.set_value(textwidth)
            self.modeline_tabstop_chooser.set_value(tabstop)
            self.modeline_expandtab_chooser.set_active(expandtab)
            


class Newfile(service.ServiceWithSingleView):
    
    NAME = 'newfile'

    COMMANDS = [('create-interactive', [
                    ('licensname', False),
                    ('filename', False),
                    ('directory', False),
                    ]
                )]

    EDITOR_VIEW = NewfileEditor

    def cmd_create_interactive(self, licensename=None, filename=None,
                                     directory=None):
        self.create_editorview()
        self.editorview.set_from_options(license=licensename,
                                         filename=filename, directory=directory)

Service = Newfile
