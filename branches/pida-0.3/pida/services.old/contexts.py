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
import pida.pidagtk.listedtab as listedtab
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.toolbar as toolbar
import pida.core.registry as registry
import pida.pidagtk.icons as icons
import gtk
import os
import os.path

REG_KEY = 'scripts'
REG_DOC = 'The scripts for this context'

REGISTRY_SCHEMA = [(REG_KEY, REG_DOC, '', registry.RegistryItem)]

CONTEXTS = [('file', 'When an action is in the context of a single file'),
            ('directory', 'When an action is in the context of a directory')]

CONTEXTS_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "conf", "contexts.conf")

class Context(object):
    scripts = None

class ContextView(contentbook.TabView):

    ICON = 'contexts'

class DefaultContext(object):
    
    COMMANDS = []

    def get_contexts(self, globaldict):
        args = self.globals_modifier(globaldict)
        for name, icon, stext, ltext in self.COMMANDS:
            funcname = 'command_%s' % name
            if hasattr(self, funcname):
                func = getattr(self, funcname)
                yield name, icon, ltext, func, args

    def get_toolbar(self, globaldict):
        tb = toolbar.Toolbar()
        callbacks = {}
        for name, icon, ltext, func, args in self.get_contexts(globaldict):
            callbacks[name] = func
            tb.add_button(name, icon, ltext)
        def clicked(toolbar, name):
            callbacks[name](args)
        tb.connect('clicked', clicked)
        return tb

    def get_menu(self, globaldict):
        print globaldict
        callbacks = {}
        def clicked(menuitem, name):
            callbacks[name](args)
        menu = gtk.Menu()
        for name, icon, ltext, func, args in self.get_contexts(globaldict):
            callbacks[name] = func
            menuitem = gtk.MenuItem()
            menubox = gtk.HBox(spacing=4)
            icon = icons.icons.get_image(icon)
            menubox.pack_start(icon, expand=False)
            label = gtk.Label(ltext)
            label.set_alignment(0, 0.5)
            menubox.pack_start(label)
            menuitem.add(menubox)
            menu.append(menuitem)
            menuitem.connect('activate', clicked, name)
        menu.show_all()
        return menu

    def globals_modifier(globaldict):
        return globaldict
            

class FileContext(DefaultContext):

    COMMANDS = [('filemanager', 'filemanager', 'File Manager',
                'Open a file manager in the parent directory of this file'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal in the parent directory of this file'),
                ('diff', 'vcs_diff', 'Version Control Diff',
                 'Get the diff on this file')]

    def globals_modifier(self, globaldict):
        return globaldict['filename']

    def command_filemanager(self, filename):
        self.boss.command('filemanager', 'browse',
            directory=self.get_parent_directory(filename))

    def command_terminal(self, filename):
        self.boss.command('terminal', 'execute-vt-shell',
        kwargs={'directory': self.get_parent_directory(filename)})

    def command_diff(self, filename):
        self.boss.command('versioncontrol', 'diff-file',
                          filename=filename)

    def get_parent_directory(self, filename):
        directory = os.path.split(filename)[0]
        return directory


class DirectoryContext(DefaultContext):
    
    COMMANDS = [('filemanager', 'filemanager', 'File Manager',
                 'Browse this directory'),
                ('up', 'up', 'Up',
                 'Browse the parent directoy'),
                ('find', 'find', 'Find',
                 'Find files in this directory'),
                ('new', 'new', 'New',
                 'Create a new file in this directory'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal in the parent directory of this file')]

    def globals_modifier(self, globaldict):
        return globaldict['directory']

    def command_filemanager(self, directory):
        self.boss.command('filemanager', 'browse', directory=directory)

    def command_find(self, directory):
        self.boss.command('grepper', 'find-interactive',
                           directories=[directory])

    def command_new(self, directory):
        self.boss.command('newfile', 'create-interactive',
                          directory=directory)

    def command_terminal(self, directory):
        self.boss.command('terminal', 'execute-vt-shell',
                          kwargs={'directory': directory})

    def command_up(self, directory):
        if directory != '/':
            parent = os.path.split(directory)[0]
            self.boss.command('filemanager', 'browse', directory=parent)

class Contexts(service.ServiceWithListedTab):

    NAME = 'contexts'
    COMMANDS = [('get-toolbar', [('contextname', True),
                ('globaldict', True)]),
                ('get-menu', [('contextname', True),
                ('globaldict', True)]),
                ('show-editor', [])]
    OPTIONS = [('filename', 'The contexts file.',
                CONTEXTS_CONF, registry.File)]

    EDITOR_VIEW = ContextView

    ICON = 'contexts'

    def init(self):
        self.__registry = registry.Registry()
        self.__filename = None
        self.__defaults = {}
        self.__defaults['file'] = FileContext()
        self.__defaults['file'].boss = self.boss
        self.__defaults['directory'] = DirectoryContext()
        self.__defaults['directory'].boss = self.boss

    def cmd_get_toolbar(self, contextname, globaldict):
        print globaldict
        default_tb = self.cmd_get_default_toolbar(contextname, globaldict)
        custom_tb = self.cmd_get_custom_toolbar(contextname, globaldict)
        box = gtk.HBox()
        if default_tb is not None:
            box.pack_start(default_tb, expand=False)
        box.pack_start(gtk.VSeparator(), expand=False)
        if custom_tb is not None:
            box.pack_start(custom_tb, expand=False)
        box.show_all()
        return box

    def cmd_get_menu(self, contextname, globaldict):
        menu = gtk.Menu()
        return self.__defaults[contextname].get_menu(globaldict)

    def cmd_get_default_toolbar(self, contextname, globaldict={}):
        return self.__defaults[contextname].get_toolbar(globaldict)

    def cmd_get_custom_toolbar(self, contextname, globaldict={}):
        group = self.__registry.get_group(contextname)
        if group is not None:
            tb = toolbar.Toolbar()
            scripts = group.get('scripts').value().split(',')
            scripts = [script.strip() for script in scripts]
            def clicked(clickedtb, name):
                self.boss.command('scripts', 'execute', scriptname=name,
                                  globaldict=globaldict)
            tb.connect('clicked', clicked)
            for script in scripts:
                tb.add_button(script, 'scripts',
                    'Click to execute script: %s' % script)
            return tb

    def reset(self):
        if self.registry_filename != self.__filename:
            self.reload()

    def reload(self):
            self.__filename = self.registry_filename
            if os.path.exists(self.__filename):
                groupdocs = dict(CONTEXTS)
                self.__registry.load_file_with_schema(
                    self.__filename, REGISTRY_SCHEMA, groupdocs)
            else:
                self.__registry.filename= self.__filename
                for context, doc in CONTEXTS:
                    group = self.__registry.add_group(context, doc)
                    opt = group.add(*REGISTRY_SCHEMA[0])
                    opt.setdefault()
                self.__registry.save()
    
    def __adapt_registry(self):
        for group in self.__registry.iter_groups():
            p = Context()
            p.name = group._name
            p.scripts = group.get('scripts').value().split(',')
            yield p

    def __get_registry_filename(self):
        return self.options.get('filename').value()
    registry_filename = property(__get_registry_filename)

    def cmd_show_editor(self):
        self.create_editorview(self.__registry)

    def cb_show_editor(self, button):
        self.cmd_show_editor()

Service = Contexts
