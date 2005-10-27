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
import pida.core.registry as registry
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.filedialogs as filedialogs

class Grepper(service.Service):

    NAME = 'grepper'

    COMMANDS = [('find-interactive', []),
                ('find', [('path', True), ('pattern', True)])]

    OPTIONS = [('start-detailed',
                'Whether the search dialog will start with the detailed view.',
                False, registry.Boolean)]

    def populate(self):
        self.boss.command('topbar', 'add-button', icon='find',
                           tooltip='Search for files or text',
                           callback=self.cb_search_clicked)
        self.__view = None

    def cmd_find_interactive(self):
        self.__create_view()

    def cmd_find(self, path, pattern):
        pass

    def __create_view(self):
        if self.__view is None:
            self.__view = GrepView()
            self.__view.set_details_expanded(self.options.get(
                'start-detailed').value())
            self.__view.connect('removed', self.cb_view_closed)
            self.boss.command('viewbook', 'add-page', contentview=self.__view)
        self.__view.raise_tab()

    def cb_search_clicked(self, button):
        self.cmd_find_interactive()

    def cb_view_closed(self, view):
        assert(view is self.__view)
        self.__view.destroy()
        self.__view = None
        

import gtk

EXPANDER_LABEL_MU = '<span size="x-small">Details</span>'
DIR_ENTRY_MU = '<span size="small">Search Path </span>'
CURRENT_ONLY_MU = '<span size="small"> Search only current buffer</span>'


class GrepView(contentbook.ContentView):

    ICON = 'find'
    ICON_TEXT = 'Find '

    HAS_SEPARATOR = False

    def populate(self):
        
        label_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        entry_size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

        hb = gtk.HBox()
        self.bar_area.pack_start(hb, expand=True, padding=2)
        self.__pattern_entry = gtk.Entry()
        hb.pack_start(self.__pattern_entry)
        entry_size_group.add_widget(self.__pattern_entry)

        self.__details_expander = gtk.Expander(label=EXPANDER_LABEL_MU)
        self.__details_expander.set_use_markup(True)

        self.pack_start(self.__details_expander, expand=False)

        details_box = gtk.VBox()
        self.__details_expander.add(details_box)


        hb = gtk.HBox()
        details_box.pack_start(hb, expand=False)
        l = gtk.Label()
        hb.pack_start(l, expand=False)
        l.set_markup(CURRENT_ONLY_MU)
        self.__only_current = gtk.CheckButton()
        hb.pack_start(self.__only_current)
        self.__only_current.connect('toggled', self.cb_only_current_toggled)
        self.__only_current.set_active(True)
        self.__dir_box = gtk.HBox()
        hb.pack_start(self.__dir_box)
        l = gtk.Label()
        l.set_markup(DIR_ENTRY_MU)
        self.__dir_box.pack_start(l, expand=False)
        label_size_group.add_widget(l)    
        self.__path_entry = filedialogs.FolderButton()
        self.__dir_box.pack_start(self.__path_entry)
        entry_size_group.add_widget(self.__path_entry)

        self.add_button('apply', 'apply', 'Start the search')
        

    def set_details_expanded(self, expanded):
        self.__details_expander.set_expanded(expanded)

    def cb_only_current_toggled(self, checkbutton):
        self.__dir_box.set_sensitive(not checkbutton.get_active())
        



Service = Grepper
