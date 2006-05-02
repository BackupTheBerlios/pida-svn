# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

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

import pida.core.service as service

import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview

defs = service.definitions

class ActionWrapper(object):
    
    def __init__(self, action):
        self.action = action
        self.name = action.get_name()
        self.key = self.name
        self.label = action.get_property('label')
        self.tooltip = action.get_property('tooltip')

class KeyboardConfigurator(contentview.content_view):

    HAS_CLOSE_BUTTON = False
    HAS_DETACH_BUTTON = False

    def init(self):
        self.__list = tree.Tree()
        self.widget.pack_start(self.__list)
        self.__list.set_property('markup-format-string',
            '<b>%(label)s</b>\n%(tooltip)s')
        self.__list.connect('double-clicked', self.cb_activated)
        self.__list.long_title = 'Keyboard Shortcuts Configuration'
        self.__list.sort_by(['name'])

    def add_action(self, action):
        act = ActionWrapper(action)
        self.__list.add_item(act)

    def cb_activated(self, tv, item):
        actwrap = item.value
        self.create_entry(actwrap)
        
    def create_entry(self, actwrap):
        d = gtk.Dialog(parent=None,
                       flags=gtk.DIALOG_MODAL,
                       title='Enter new keypress',
                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
                       )
        action = actwrap.action
        e = gtk.Entry()
        e.show()
        d.vbox.pack_start(e, expand=False)
        key, mod = gtk.accel_map_lookup_entry(action.accel_path)
        accel = gtk.accelerator_name(key, mod)
        e.set_text(accel)
        def _response(dlg, response):
            d.hide()
            if response == gtk.RESPONSE_ACCEPT:
                newaccel = e.get_text()
                action.set_accel(newaccel)
                actwrap.reset_markup()
                key, mod = gtk.accelerator_parse(newaccel)
                gtk.accel_map_change_entry(action.accel_path, key, mod, True)
            d.destroy()
        d.connect('response', _response)
        d.run()

class KeyboardShortcuts(service.service):


    class ShortcutsView(defs.View):
        view_type = KeyboardConfigurator
        book_name = 'ext'

    def reset(self):
        self.actions = self.boss.call_command('window', 'get_action_groups')

    def act_keyboard_shortcuts(self, action):
        self.call('edit')

    def cmd_edit(self):
        view = self.create_view('ShortcutsView')
        self.show_view(view=view)
        for actiongroup in self.actions:
            for action in actiongroup.list_actions():
                if hasattr(action, 'keyval') and action.keyval:
                    view.add_action(action)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_edit" action="base_edit_menu">
                    <placeholder name="SubPreferencesMenu">
                    <separator />
                    <menuitem
                     name="editkeys"
                     action="keyboardshortcuts+keyboard_shortcuts" />
                    </placeholder>    
                </menu>
                </menubar>
              """



Service = KeyboardShortcuts
