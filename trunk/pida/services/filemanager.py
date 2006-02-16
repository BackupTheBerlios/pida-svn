# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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
import pida.pidagtk.filemanager as filemanager
import pida.core.actions as actions

defs = service.definitions

import subprocess


from pida.utils.kiwiutils import gsignal
import gobject
import gtk
import os

STATE_IGNORED, STATE_NONE, STATE_NORMAL, STATE_NOCHANGE, \
STATE_ERROR, STATE_EMPTY, STATE_NEW, \
STATE_MODIFIED, STATE_CONFLICT, STATE_REMOVED, \
STATE_MISSING, STATE_MAX = range(12)

colours = {
            None: ('#000000', False, True),
            STATE_IGNORED: ('#909090', False, True),
            STATE_NONE: ('#60c060', True, True),
            STATE_NORMAL: ('#000000', False, False),
            STATE_ERROR: ('#900000', True, True),
            STATE_EMPTY: ('#000000', False, True),
            STATE_MODIFIED: ('#900000', True, False),
            STATE_CONFLICT: ('#c00000', True, True),
            STATE_REMOVED: ('#c06060', True, False),
            STATE_MISSING: ('#00c0c0', True, False),
            STATE_NEW: ('#0000c0', True, False),
            STATE_MAX: ('#c0c000', False, False),
        }

letters = {
            None: ' ',
            STATE_IGNORED: ' ',
            STATE_NONE: '?',
            STATE_NORMAL: ' ',
            STATE_ERROR: 'E',
            STATE_EMPTY: '!',
            STATE_MODIFIED: 'M',
            STATE_CONFLICT: 'C',
            STATE_REMOVED: 'D',
            STATE_MISSING: '!',
            STATE_NEW: 'A',
            STATE_MAX: '+'
            }

class GtkReader(gobject.GObject):

    gsignal('started')

    gsignal('finished', str)

    gsignal('plain-data', str)

    gsignal('status-data', str)

    def __init__(self, scriptpath):
        self.__dirq = []
        self.scriptpath = scriptpath
        self.current_directory = None
        gobject.GObject.__init__(self)

    def ls(self, directory):
        self.__dirq.append(directory)
        if len(self.__dirq) == 1:
            self._ls()

    def _ls(self):
        qlen = len(self.__dirq)
        if not qlen:
            return
        self.emit('started')
        p = subprocess.Popen(['python', self.scriptpath, self.__dirq[0]],
                 stdout=subprocess.PIPE)
        self.__watch = gobject.io_add_watch(p.stdout,
                       gobject.IO_IN, self.cb_read)
        gobject.io_add_watch(p.stdout.fileno(), gobject.IO_HUP, self.cb_hup)

    def _received(self, d):
        typ, data = d.split(' ', 1)
        if typ == '<p>':
            sig = 'plain-data'
        else:
            sig = 'status-data'
        self.emit(sig, data)

    def cb_read(self, fd, cond):
        d = fd.readline().strip()
        self._received(d)
        return True

    def cb_hup(self, fd, cond):
        def _f():
            gobject.source_remove(self.__watch)
            self.current_directory = self.__dirq.pop(0)
            self.emit('finished', self.current_directory)
            self._ls()
        gobject.idle_add(_f)


import pida.pidagtk.tree as tree

import pida.pidagtk.icons as icons
dir_icon = icons.icons.get('gtk-directory')

class FileSystemItem(object):

    def __init__(self, path):
        self.path = self.key = path
        self.name = os.path.basename(path)
        self.isdir = os.path.isdir(path)
        self.status = None
        self.isnotdir = not self.isdir

    def get_markup(self):
        col, b, i = colours[self.status]
        status = letters[self.status]
        sinf = ('<span weight="ultrabold">'
                '<tt>%s </tt></span>' %
                (status))
        fn = self.name
        if i:
            fn = '<i>%s</i>' % fn
        if b:
            fn = '<b>%s</b>' % fn
        return '<span color="%s">%s%s</span>' % (col, sinf, fn)
    markup = property(get_markup)

    

    def get_pixbuf(self):
        if self.isdir:
            return dir_icon
    pixbuf = property(get_pixbuf)

class FileTree(tree.IconTree):
    
    SORT_AVAILABLE = [('Directories first', 'isnotdir'),
                    ('File name', 'name'),
                    ('Version status', 'status')]

    SORT_CONTROLS = True

import pida.pidagtk.contentview as contentview

class FileBrowser(contentview.content_view):

    gsignal('file-activated', str)

    ICON_NAME = 'filemanager'
    LONG_TITLE = 'File manager'
    SHORT_TITLE = 'Files'
    HAS_CLOSE_BUTTON = False
    HAS_DETACH_BUTTON = False

    def init(self, scriptpath):
        gobject.GObject.__init__(self)
        self._reader = GtkReader(scriptpath)
        self._reader.connect('started', self.cb_started)
        self._reader.connect('finished', self.cb_finished)
        self._reader.connect('plain-data', self.cb_plain_data)
        self._reader.connect('status-data', self.cb_status_data)
        self._files = {}
        self._recent = {}
        self.cwd = None
        self.create_toolbar()
        self.create_actions()
        self.create_tree()

    def create_toolbar(self):
        self._toolbar= gtk.Toolbar()
        self.widget.pack_start(self._toolbar, expand=False)
        self._toolbar.set_icon_size(gtk.ICON_SIZE_MENU)

    def create_actions(self):
        self._homeact = gtk.Action('Home', 'Home',
                                   'Browse the project root', 'gtk-project')
        self.add_action_to_toolbar(self._homeact)
        self._homeact.connect('activate', self.cb_act_home)
        self._upact = gtk.Action('Up', 'Up', 'go up', gtk.STOCK_GO_UP)
        self.add_action_to_toolbar(self._upact)
        self._upact.connect('activate', self.cb_act_up)
        self._refreshact = gtk.Action('Refresh', 'Refresh',
            'Refresh the directory', gtk.STOCK_REFRESH)
        self.add_action_to_toolbar(self._refreshact)
        self._refreshact.connect('activate', self.cb_act_refresh)
        self._newfileact = gtk.Action('New', 'New',
                            'Create a new file here', gtk.STOCK_NEW)
        self.add_action_to_toolbar(self._newfileact)
        self._newfileact.connect('activate', self.cb_act_new_file)
        self._newdiract = gtk.Action('NewDir', 'New Directory',
                            'Create a new directory here', 'gtk-directory')
        self.add_action_to_toolbar(self._newdiract)
        self._newdiract.connect('activate', self.cb_act_new_dir)
        self._termact = gtk.Action('Terminal', 'Terminal',
                            'Open a terminal in this directory',
                            'gtk-terminal')
        self.add_action_to_toolbar(self._termact)
        self._termact.connect('activate', self.cb_act_terminal)
        self._searchact = gtk.Action('Search', 'Search',
                            'Search files for text',
                            'gtk-searchtool')
        self.add_action_to_toolbar(self._searchact)
        self._searchact.connect('activate', self.cb_act_search)

    def add_action_to_toolbar(self, action):
        toolitem = action.create_tool_item()
        self._toolbar.add(toolitem)
    
    def create_tree(self):
        self._view = FileTree()
        self._view.set_property('markup-format-string', '%(markup)s')
        self._view.connect('double-clicked', self.cb_double_click)
        self._view.connect('right-clicked', self.cb_right_click)
        self.widget.pack_start(self._view)
        return self._view

    def browse(self, directory=None):
        if directory is None:
            directory = os.path.expanduser('~')
        if directory in self._recent:
            self._view.clear()
            for fsi in self._recent[directory].values():
                self._view.add_item(fsi)
            self.cwd = directory
            self.long_title = self.cwd
        else:
            self._reader.ls(directory)

    def browse_up(self):
        directory = self.cwd
        if directory is not None and directory != '/':
            parent = os.path.dirname(directory)
            self.browse(parent)
   
    def forget(self, directory):
        if directory in self._recent:
            del self._recent[directory]
         
    def cb_started(self, reader):
        self._files = {}
        self._view.clear()

    def cb_finished(self, reader, cwd):
        self.cwd = cwd
        self._recent[self.cwd] = self._files
        self.long_title = self.cwd

   
        

    def cb_plain_data(self, reader, path):
        if path not in self._files:
            fsi = FileSystemItem(path)
            self._view.add_item(fsi)
            self._files[path] = fsi

    def cb_status_data(self, reader, path):
        path, status = path.split(' ', 1)
        try:
            f = self._files[path]
        except KeyError:
            f = FileSystemItem(path)
            self._files[path] = f
            self._view.add_item(f)
        f.status = int(status)
        f.reset_markup()

    def cb_double_click(self, tv, item):
        fsi = item.value
        if fsi.isdir:
            self.browse(fsi.path)
        else:
            self.emit('file-activated', fsi.path)
        
    def cb_act_up(self, action):
        self.browse_up()

    def cb_act_refresh(self, action):
        if self.cwd is not None:
            self.forget(self.cwd)
            self.browse(self.cwd)

    def cb_act_home(self, action):
        project = self.service.boss.call_command('projectmanager',
                                         'get_current_project')
        if project is not None:
            project_root = project.source_directory
            self.service.call('browse', directory=project_root)
        else:
            self.service.log.info('there is no project to go to its root')


    def cb_act_new_file(self, action):
        self.emit('newfile-clicked', self.cwd)
        self.service.boss.call_command('newfile', 'create_interactive',
                          directory=self.cwd)
    
    def cb_act_new_dir(self, action):
        self.service.boss.call_command('newfile', 'create_interactive',
                          directory=self.cwd, mkdir=True)

    def cb_act_terminal(self, action):
        self.service.boss.call_command('terminal',
                               'execute_shell',
                               kwdict={'directory': self.cwd})
    
    def cb_act_search(self, action):
        self.service.boss.call_command('grepper', 'find_interactive',
                               directories=[self.cwd])

    def _popup_file(self, path, event):
        menu = self.service.boss.call_command('contexts',
                'get_context_menu', ctxname='file',
                ctxargs=[path])
        menu.get_children()[0].hide()
        action = self.service.action_group.get_action('filemanager+open')
        mi = action.create_menu_item()
        menu.insert(mi, 0)
        menu.popup(None, None, None, event.button, event.time)

    def _popup_dir(self, path, event):
        menu = self.service.boss.call_command('contexts',
                'get_context_menu', ctxname='directory',
                ctxargs=[path])
        menu.popup(None, None, None, event.button, event.time)

    def cb_right_click(self, view, fileitem, event):
        if fileitem is None:
            return
        fsi = fileitem.value
        if os.path.isdir(fsi.path):
            self._popup_dir(fsi.path, event)
        else:
            self._popup_file(fsi.path, event)

class file_manager(service.service):

    class FileBrowser(defs.View):
        view_type = FileBrowser
        book_name = 'content'

    class directory_changed(defs.event):
        """Called when the current directory is changed."""

    def init(self):
        self.__content = None
        import pkg_resources
        fn = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('pida'),
                'forkscripts/ls.py')
        self.plugin_view = self.create_view('FileBrowser', scriptpath=fn)

    @actions.action(
    default_accel='<Control><Shift>f',
    label='Focus the file manager'
    )
    def act_grab_focus(self, action):
        self.call('browse', directory=self.cmd_get_current_directory())

    def act_open(self, action):
        """Open the current file in the editor."""
        self.boss.call_command('buffermanager', 'open_file',
                               filename=self.plugin_view.selected)

    def cmd_browse(self, directory=None):
        #if self.plugin_view is None:
        #    self.create_plugin_view()
        self.plugin_view.connect('file-activated',
                                  self.cb_single_view_file_activated)
        if directory is None:
            directory = os.path.expanduser('~')
        self.plugin_view.browse(directory)
        self.plugin_view.raise_page()

    def cmd_get_current_directory(self):
        return self.plugin_view.cwd

    def cb_single_view_file_activated(self, view, filename):
        
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)

    def get_plugin_view(self):
        return self.get_first_view('FileBrowser')
    splugin_view = property(get_plugin_view)

        
Service = file_manager
