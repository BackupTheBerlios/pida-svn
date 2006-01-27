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

# system import(s)
import os
import glob
import ConfigParser as configparser
import re

# gtk import(s)
import gtk

# pida core import(s)
import pida.core.base as base
import pida.core.service as service

# pidagtk import(s)
import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview

# registry types
defs = service.definitions

# markup definitions
NAME_MU = '<big>%s</big>'
DEF_MU = '<b>%s</b>'


class command_line_opener(base.pidaobject):
    """A single command line opener."""

    def __init__(self, name, commandline, fileglob, in_terminal=True):
        self.__name = name
        self.key = name
        self.__commandline = commandline
        self.__in_terminal = in_terminal
        self.glob = fileglob

    def matches_file(self, filename):
        return self.__re.match(filename)

    def build_command_line(self, filename):
        line = self.__commandline % filename
        return line

    def build_action(self, filename):
        action = gtk.Action(self.name, self.name, self.commandline, None)
        action.connect('activate', self.execute, filename)
        return action

    def build_menu_item(self, filename):
        action = self.build_action(filename)
        return action.create_menu_item()
 
    def execute(self, action, filename):
        commandline = self.build_command_line(filename)
        command_args = ['sh', '-c', commandline]
        self.boss.call_command('terminal', 'execute',
                               command_args=command_args)

    def get_name(self):
        return self.__name
    name = property(get_name)

    def get_commandline(self):
        return self.__commandline
    
    def set_commandline(self, commandline):
        self.__commandline = commandline

    commandline = property(get_commandline, set_commandline)

    def get_glob(self):
        return self.__glob
    
    def set_glob(self, fileglob):
        self.__glob = fileglob
        self.__re = re.compile(glob.fnmatch.translate(fileglob))

    glob = property(get_glob, set_glob)

class opener_list(tree.Tree):
    """Tree view used for opener list."""

    EDIT_BOX = True


class opener_view(contentview.content_view):
    """Opener configuration view."""

    LONG_TITLE = 'Open With Configuration'

    def init(self):
        self.__current = None
        self.widget.pack_start(self.__init_pane())
        self.widget.pack_start(self.__init_buttons(), expand=False)

    def set_openers(self, openers):
        self.__openers = openers
        self.__build_list()
        if len(self.__openers):
            self.__list.set_selected(self.__openers[0].name)

    def __build_list(self):
        self.__list.clear()
        for opener in self.__openers:
            self.__list.add_item(opener)
        self.__page.set_sensitive(len(self.__openers) > 0)

    def __init_pane(self):
        box = gtk.HPaned()
        self.__list = self.__init_list()
        box.pack1(self.__list)
        box.pack2(self.__init_page())
        return box

    def __init_list(self):
        names = opener_list()
        names.connect('clicked', self.cb_names_clicked)
        return names

    def __init_page(self):
        box = gtk.VBox()
        self.__page = box
        s1 = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        s2 = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self.__name_label = gtk.Label()
        box.pack_start(self.__name_label, expand=False)
        self.__name_label.set_alignment(0, 0.5)
        box2 = gtk.HBox(spacing=6)
        box.pack_start(box2, expand=False, padding=6)
        lb_command = gtk.Label()
        box2.pack_start(lb_command, expand=False)
        lb_command.set_markup(DEF_MU % 'Command Line')
        s1.add_widget(lb_command)
        lb_command.set_alignment(0, 0.5)
        self.__command_entry = gtk.Entry()
        box2.pack_start(self.__command_entry)
        s2.add_widget(self.__command_entry)
        box2 = gtk.HBox(spacing=6)
        box.pack_start(box2, expand=False, padding=6)
        lb_glob = gtk.Label()
        box2.pack_start(lb_glob, expand=False)
        lb_glob.set_markup(DEF_MU % 'Glob')
        s1.add_widget(lb_glob)
        lb_glob.set_alignment(0, 0.5)
        self.__glob_entry = gtk.Entry()
        box2.pack_start(self.__glob_entry)
        s2.add_widget(self.__glob_entry)
        return box

    def __init_buttons(self):
        box = gtk.HButtonBox()
        add = gtk.Button(stock=gtk.STOCK_ADD)
        box.pack_start(add)
        add.connect('clicked', self.cb_add_clicked)
        remove = gtk.Button(stock=gtk.STOCK_REMOVE)
        box.pack_start(remove)
        remove.connect('clicked', self.cb_remove_clicked)
        save = gtk.Button(stock=gtk.STOCK_SAVE)
        box.pack_start(save)
        save.connect('clicked', self.cb_save_clicked)
        return box

    def __set_page(self, opener):
        self.__current = opener
        self.__name_label.set_markup(NAME_MU % opener.name)
        self.__command_entry.set_text(opener.commandline)
        self.__glob_entry.set_text(opener.glob)
        
    def __new_item(self, name):
        item = command_line_opener(name, '', '*')
        self.__openers.append(item)
        self.__build_list()
        self.__list.set_selected(name)

    def __store_current(self):
        self.__current.commandline = self.__command_entry.get_text()
        self.__current.glob = self.__glob_entry.get_text()
    
    def __save_openers(self):
        self.service.save()

    def cb_add_clicked(self, button):
        self.__list.question(self.__new_item, 'Name?')

    def cb_remove_clicked(self, button):
        for i, opener in enumerate(self.__openers):
            if opener.name == self.__list.selected_key:
                self.__openers.pop(i)
                self.__build_list()
                break

    def cb_save_clicked(self, button):
        self.__store_current()
        self.__save_openers()
        
    def cb_names_clicked(self, tv, item):
        if self.__current is not None:
            self.__store_current()
        opener = item.value
        self.__set_page(opener)
        

class open_with(service.service):
    """Open files by glob with configurable applications."""
    
    display_name = 'Open With'

    single_view_type = opener_view
    single_view_book = 'ext'

    def init(self):
        self.__datafile = os.path.join(self.boss.pida_home,
                                       'data', 'openwith')
        self.__openers = []
        self.__load_openers()

    def __load_openers(self):
        if os.path.exists(self.__datafile):
            f = open(self.__datafile)
            parser = configparser.ConfigParser()
            try:
                parser.readfp(f)
            except:
                return
            for group in parser.sections():
                if parser.has_option(group, 'exec'):
                    commandline = parser.get(group, 'exec')
                else:
                    commandline = ''
                if parser.has_option(group, 'glob'):
                    fileglob = parser.get(group, 'glob')
                else:
                    fileglob = '*'
                opener = command_line_opener(group, commandline, fileglob)
                self.__openers.append(opener)

    def __save_openers(self):
        f = open(self.__datafile, 'w')
        for opener in self.__openers:
            f.write('[%s]\n' % opener.name)
            f.write('exec=%s\n' % opener.commandline)
            f.write('glob=%s\n\n' % opener.glob)
        f.close()
    save = __save_openers
        
    def cmd_get_openers(self, filename):
        for opener in self.__openers:
            if opener.matches_file(filename):
                yield opener

    def cmd_get_openers_menu(self, filename):
        menu = gtk.Menu()
        for opener in self.call('get_openers', filename=filename):
            mi = opener.build_menu_item(filename)
            menu.add(mi)
        menu.add(gtk.SeparatorMenuItem())
        act = self.action_group.get_action('openwith+configure_open_with')
        menu.add(act.create_menu_item())
        menu.show_all()
        return menu

    def cmd_configure(self):
        view = self.create_single_view()
        view.set_openers(self.__openers)

    def act_configure_open_with(self, action):
        self.call('configure')

    def get_menu_definition(self):
        return """<menubar>
                  <menu name="base_tools" action="base_tools_menu">
                  <menu name="service_conf" action="base_service_conf_menu">
    
                  <menuitem name="newpaste"
                        action="configure_openwith+open_with" />
                  <separator />
                  </menu>
                  </menu>
                  </menubar>
               """

Service = open_with

