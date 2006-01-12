# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com
#Copyright (c) 2006 Bernard Pratz aka Guyzmo, guyzmo@m0g.net

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

# gtk import(s)
import gtk

# pida import(s)
import pida.pidagtk.tree as tree
import pida.pidagtk.gladeview as gladeview
import pida.pidagtk.progressbar as progressbar

# pida utils import(s)
import pida.utils.pastebin as pastebin

# pida core import(s)
import pida.core.registry as registry
import pida.core.service as service

types = service.types
defs = service.definitions


class paste_editor_view(gladeview.glade_view):
    '''Create and edit a new paste'''

    SHORT_TITLE = 'Create a paste'
    LONG_TITLE = 'Create a paste so you can post it'
    ICON = 'paste'

    # UI loading

    glade_file_name = 'paste-editor.glade'

    def init_glade(self):
        '''Initiate the interface using glade'''
        self.__options = {}
        self.__inputs = {}
        self.__options_bar = self.get_widget('hseparator_combo')
        self.__list_sites = self.get_widget('list_sites')
        for site in pastebin.BINS.keys():
            self.__list_sites.append_text(site)
        self.__list_sites.connect('changed', self.cb_list_site_change)
        self.__list_sites.set_active(0)
        self.__title_entry = self.get_widget('post_title_entry')
        self.__nickname_entry = self.get_widget('post_name_entry')
        self.__title_entry.set_text('') # TODO: Use options
        self.__nickname_entry.set_text('') # TODO: Use options
        self.__text_entry = self.get_widget('post_text_entry')
        self.__pulse_bar = progressbar.progress_bar()
        self.widget.pack_start(self.__pulse_bar, expand=False)
        self.__pulse_bar.set_size_request(-1, 12)
        self.__pulse_bar.set_pulse_step(0.01)

    def set_paste_bin(self, pbin):
        '''Sets a pastebin to the view in order to get informations'''
        self.__pastebin = pbin
        self.__pack_combos()
        self.__pack_inputs()

    def create_list_box(self, str1, str2, int1, int2):
        '''Returns a ComboBox object'''
        return gtk.combo_box_new_text()
    # private interface

    def __pack_combos(self):
        '''Populate all comboboxes'''
        hb = self.__options_bar
        [hb.remove(child) for child in
            hb.get_children()]
        if self.__pastebin.OPTIONS != None:
            for option in self.__pastebin.OPTIONS.keys():
                label = gtk.Label(option)
                label.show()
                hb.add(label)
                self.__options[option] = gtk.combo_box_new_text()
                for value in self.__pastebin.OPTIONS[option]:
                    if len(value):
                        self.__options[option].append_text(value)
                self.__options[option].set_active(0)
                self.__options[option].show()
                hb.add(self.__options[option])
            hb.show_all()
    
    def __pack_inputs(self):
        '''Populates all inputs'''
        if self.__pastebin.INPUTS != None:
            vb = self.get_widget('vb_entries')
            for name in self.__pastebin.INPUTS.keys():
                hb = gtk.HBox
                name = gtk.Label(name)
                name.show()
                hb.add(name)
                self.__inputs[name] = gtk.Entry()
                self.__inputs[name].set_text(self.__pastebin.INPUTS[name])
                self.__inputs[name].show()
                hb.add(self.__inputs[name])
                vb.add(hb)

    def __clear(self):
        '''Clears the interface'''
        self.__title_entry.set_text("")
        self.__nickname_entry.set_text("")
        if self.__pastebin.INPUTS != None:
            for name in self.__pastebin.INPUTS.keys():
                self.__inputs[name].set_text("")
        if self.__pastebin.OPTIONS != None:
            for option in self.__pastebin.OPTIONS.keys():
                self.__options[option].set_active(0)
        self.__text_entry.get_buffer().set_text("")

    # public api

    def pulse(self):
        '''Starts the pulse'''
        self.__pulse_bar.show_pulse()

    # UI callbacks

    def on_post_button__clicked(self,but):
        '''Post the paste'''
        self.__pastebin.set_title(self.__title_entry.get_text())
        self.__pastebin.set_name(self.__nickname_entry.get_text())
        self.__pastebin.set_pass('') ## TODO: USE OPTIONS
        self.__pastebin.set_text(self.__text_entry.get_buffer().get_text(
                    self.__text_entry.get_buffer().get_start_iter(),
                    self.__text_entry.get_buffer().get_end_iter()))
        if self.__pastebin.OPTIONS != None:
            options = {}
            for option in self.__pastebin.OPTIONS.keys():
                options[option] = self.__options[option].get_active_text()
            self.__pastebin.set_options(options)
        if self.__pastebin.INPUTS != None:
            inputs = {}
            for name in self.__pastebin.INPUTS.keys():
                inputs[name] = self.__inputs[name].get_text()
            self.__pastebin.set_inputs(inputs)
        self.__pastebin.set_editor(self)
        but.set_sensitive(False)
        self.service.plugin_view.raise_page()
        self.service.call('post_paste', paste=self.__pastebin)

    def on_clear_button__clicked(self,but):
        '''Clears the paste'''
        self.__clear()
        
    def on_close_button__clicked(self,but):
        '''Quits the paste editor without modification'''
        self.close()

    def cb_list_site_change(self, list):
        '''Callback function called on pastebin sites list change'''
        self.__list_selected = self.__list_sites.get_active_text()
        pbin = pastebin.BINS[self.__list_selected]()
        #self.boss.call_command('pasteeditor','create_paste',paste=pbin)
        #self.multi_view_type = paste_editor_view
        self.set_paste_bin(pbin)


class paste_tree(tree.Tree):
    '''Tree listing all the pastes'''
    EDIT_BUTTONS = False
    SORT_BY = 'date'

    markup_format_string = ('<span size="small"><b>%(title)s</b> ('
            '<span foreground="#0000c0">%(syntax)s</span>)\n'
            '%(url)s</span>')
        
    def __init__(self):
        '''Initializes the tree'''
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', self.markup_format_string)
                
    def push_paste(self, paste):
        '''Adds a paste to the Tree'''
        self.add_item(paste, key=paste.date)

    def del_paste(self):
        '''Deletes the currently selected paste'''
        self.del_item()


class paste_history_view(gladeview.glade_view):
    SHORT_TITLE = 'Paste History'
    LONG_TITLE = 'Paste History'
    ICON_NAME = 'paste'
    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = True

    glade_file_name = 'paste-history.glade'

    def create_paste_tree(self, str1, str2, int1, int2):
        '''Returns a paste_tree object'''
        return paste_tree()

    def init_glade(self):
        '''Constructor of the Paste History View.'''
        self.__history_tree = self.get_widget('paste_tree')
        self.__x11_clipboard = gtk.Clipboard(selection="PRIMARY")
        self.__gnome_clipboard = gtk.Clipboard(selection="CLIPBOARD")
        self.__registry = registry.registry()
        self.__tree_selected = None
        self.__history_tree.connect('clicked', self.cb_paste_clicked)
        self.__history_tree.connect('double-clicked', self.cb_paste_db_clicked)
        self.__history_tree.connect('middle-clicked', self.cb_paste_m_clicked)
        self.__history_tree.connect('right-clicked', self.cb_paste_r_clicked)
        self.__uim = gtk.UIManager()
        self.__uim.insert_action_group(self.service.action_group, 0)
        self.__uim.add_ui_from_string("""
            <popup>
            <menuitem name="1" action="pastemanager+new_paste" />
            <separator />
            <menuitem name="2" action="pastemanager+view_paste" />
            <menuitem name="3" action="pastemanager+copy_url_to_clipboard" />
            <separator />
            <menuitem name="5" action="pastemanager+remove_paste" />
            </popup>
            """)
        self.__popup_menu = self.__uim.get_widget('/popup')

    def set(self, pastes):
        '''Sets the paste list to the tree view.
           First reset it, then rebuild it.
        '''
        self.__history_tree.clear()
        for paste in pastes:
            self.__history_tree.push_paste(paste)
        self.__tree_selected = None

    def on_add__clicked(self, but):
        '''Callback function bound to the toolbar button new that creates a new
        paste to post'''
        self.service.boss.call_command('pastemanager','create_paste')

    def copy_current_paste(self):
        '''Callback function bound to the toolbar button view that copies the
        selected paste'''
        if self.__tree_selected != None:
            self.__x11_clipboard.set_text(self.__tree_selected.get_url())
            self.__gnome_clipboard.set_text(self.__tree_selected.get_url())

    def view_current_paste(self):
        '''Callback function bound to the toolbar button view that shows the
        selected paste'''
        if self.__tree_selected != None:
            self.service.boss.call_command('pastemanager','view_paste',
                paste=self.__tree_selected)
        else:
            print "ERROR: No paste selected"

    def remove_current_paste(self):
        '''Callback function bound to the toolbar button delete that removes the
        selected paste'''
        if self.__tree_selected != None:
            self.service.boss.call_command('pastemanager','delete_paste',
                paste=self.__tree_selected)
        else:
            print "ERROR: No paste selected"

    def cb_paste_clicked(self,paste,tree_item):
        '''Callback function called when an item is selected in the TreeView'''
        self.__tree_selected = tree_item.value

    def cb_paste_db_clicked(self,paste,tree_item):
        '''Callback function called when an item is double clicked, and copy it
        to the gnome/gtk clipboard'''
        if self.__tree_selected != None:
            # self.__gnome_clipboard.set_text(self.__tree_selected.get_url())
            # aa: view the paste
            self.service.call('view_paste', paste=self.__tree_selected)

    def cb_paste_m_clicked(self,paste,tree_item):
        '''Callback function called when an item is middle clicked, and copy it
        to the mouse buffer clipboard'''
        if self.__tree_selected != None:
            self.__x11_clipboard.set_text(self.__tree_selected.get_url())

    def cb_paste_r_clicked(self, paste, tree_item, event):
        sensitives = (tree_item is not None)
        for action in ['pastemanager+remove_paste',
                       'pastemanager+view_paste',
                       'pastemanager+copy_url_to_clipboard']:
            self.service.action_group.get_action(action).set_sensitive(sensitives)
        self.__popup_menu.popup(None, None, None, event.button, event.time)
        

class paste_manager(service.service):
    """Service that manages the pastes and the pastebins"""

    plugin_view_type = paste_history_view

    multi_view_type = paste_editor_view
    multi_view_book = 'ext'

    # life cycle

    def start(self):
        '''Initialization'''
        self.__pastes = []

    def reset(self):
        '''Reset'''
        self.__pastes = []

    def stop(self):
        pass

    # private interface

    def __add_paste(self, paste):
        '''Adds a paste to the list'''
        self.__pastes.append(paste)

    def __send_paste(self, paste):
        '''Trigger the paste's posting'''
        paste.paste()

    def __del_paste(self, paste):
        '''Remove paste 'paste' from the list'''
        self.__pastes.remove(paste)

    def __get_paste(self, paste_id):
        '''Returns a paste depending on paste_id (deprecated)'''
        for paste in self.__pastes:
            if (paste.get_id == paste_id):
                return paste

    def __refresh(self):
        self.plugin_view.set(self.pastes)

    # external interface

    def get_pastes(self):
        '''Returns an iterator on the paste list'''
        for paste in self.__pastes:
            yield paste
    pastes = property(get_pastes)

    def push(self, paste):
        '''Add a paste to the pastelist and refresh'''
        self.__add_paste(paste)
        self.__refresh()

    # commands

    def cmd_create_paste(self, paste=None):
        '''Command to create a new paste
        
           Opens a new editor
        '''
        view = self.create_multi_view()

    def cmd_post_paste(self, paste):
        '''Post the paste paste'''
        paste.set_mgr(self)
        paste.paste()

    def cmd_view_paste(self, paste):
        '''View a paste'''
        #self.boss.call_command('pasteeditor','view_paste',paste=paste)
        self.boss.call_command('webbrowse', 'browse', url=paste.url)

    def cmd_delete_paste(self, paste):
        '''Delete a paste'''
        self.__del_paste(paste)
        self.__refresh()

    def cmd_get_pastes(self):
        '''Get all pastes'''
        return self.pastes

    # ui actions

    def act_new_paste(self, action):
        self.call('create_paste')

    def act_remove_paste(self, action):
        self.plugin_view.remove_current_paste()

    def act_copy_url_to_clipboard(self, action):
        self.plugin_view.copy_current_paste()

    def act_view_paste(self, action):
        self.plugin_view.view_current_paste()

    def get_menu_definition(self):
        return """<menubar>
                  <menu name="base_tools" action="base_tools_menu">
                  <separator />
                  <menuitem name="newpaste" action="pastemanager+new_paste" />
                  <separator />
                  </menu>
                  </menubar>
               """

Service = paste_manager
