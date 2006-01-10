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
import gtk
import pida.pidagtk.icons as icons
import os

MENU_MU = """<span size="small">%s</span>"""

class Menubar(service.Service):

    NAME = "menubar"
    
    def init(self):
        self.__menu = gtk.MenuBar()
        self.__toplevels = {}

    def __create_item(self, text, icon, commandargs=None):
        item = gtk.MenuItem()
        box = gtk.HBox(spacing=4)
        if icon is not None:
            icon = icons.icons.get_image(icon)
            box.pack_start(icon, expand=False)
        if text != '':
            label = gtk.Label()
            label.set_markup(MENU_MU % text)
            box.pack_start(label, expand=False)
        item.add(box)
        if commandargs is not None:
            try:
                targetservice, command, argdict = commandargs
                def activated(menuitem):
                    self.boss.command(targetservice, command, **argdict)
                item.connect('activate', activated)
            except:
                raise TypeError, "commandargs is (service, command, argdict)"
        return item

    def __add_item(self, group, item):
        self.__toplevels[group].append(item)

    def __add(self, group, *args, **kw):
        item = self.__create_item(*args, **kw)
        self.__add_item(group, item)
        
    def __add_separator(self, group):
        item = gtk.SeparatorMenuItem()
        self.__toplevels[group].append(item)
        

    def populate(self):
        self.__generate_base_menu()

    def __generate_base_menu(self):
        # Is this really worse than a hunk of XML?
        toplevels = ['pida',
                     'actions',
                     'help',
                     ]

        for toplevel in toplevels:
            menuitem = self.__create_item(toplevel, None, None)
            self.__menu.append(menuitem)
            menu = gtk.Menu()
            menuitem.set_submenu(menu)
            self.__toplevels[toplevel] = menu
        
        items = [
                 ('pida', 'Options', 'configure',
                    ('configmanager', 'show-editor', {})),
                 ('pida', 'Scripts', 'scripts',
                    ('scripts', 'show-editor', {})),
                 ('pida', 'Contexts', 'contexts',
                    ('contexts', 'show-editor', {})),
                 ('pida', None),
                 ('pida', 'Manhole', 'manhole',
                    ('manhole', 'run', {})),
                 ('actions', 'Search', 'find',
                    ('grepper', 'find-interactive', {})),
                 ('actions', 'Terminal', 'terminal',
                    ('terminal', 'execute-vt-shell', {})),
                 ('actions', 'Python Shell', 'python',
                    ('terminal', 'execute-py-shell', {})),
                 ('actions', None),
                 ('actions', '~', 'filemanager',
                    ('filemanager', 'browse',
                        {'directory': os.path.expanduser('~')})),
                 ('actions', 'Web Browser', 'internet',
                    ('webbrowser', 'browse',
                        {}))]

        for itemargs in items:
            if itemargs[1] == None:
                self.__add_separator(itemargs[0])
            else:
                self.__add(*itemargs)
        

    def get_menu(self):
        return self.__menu
    view = property(get_menu)

Service = Menubar
