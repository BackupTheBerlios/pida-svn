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

"""
The PIDA File browser.

The PIDA filebrowser functions as a normal listed file browser with added
version control status information for all the version control systems
supported in PIDA.

In order to open a file in the editor, it should be double-clicked. There is
an additional context menu for various actions that can be performed on the
selected file system item. This context menu contains the "Open With" menu.
"""

import os, glob
import mimetypes
import threading
import gtk
import gobject

import pida.pidagtk.tree as tree
import pida.pidagtk.icons as icons
import pida.core.service as service
import pida.core.actions as actions
from pida.model import attrtypes as types
from pida.utils.kiwiutils import gsignal
import pida.pidagtk.contentview as contentview

mime_icons = {}
dir_icon = icons.icons.get('gtk-directory')
pida_icon = contentview.create_pida_icon().scale_simple(16, 16,
                                        gtk.gdk.INTERP_NEAREST)

defs = service.definitions

STATE_IGNORED, STATE_NONE, STATE_NORMAL, STATE_NOCHANGE, \
STATE_ERROR, STATE_EMPTY, STATE_NEW, \
STATE_MODIFIED, STATE_CONFLICT, STATE_REMOVED, \
STATE_MISSING, STATE_MAX = range(12)

colours = {
            None: ('#909090', False, True),
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

busy_cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
normal_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)

class FileSystemItem(object):

    def __init__(self, path):
        self.path = self.key = path
        self.name = os.path.basename(path)
        self.isdir = os.path.isdir(path)
        self.status = STATE_NORMAL
        self.statused = False
        self.isnotdir = not self.isdir
        self.extension = self.name.rsplit('.')[-1]
        if self.extension == self.name:
            self.extension = ''
        self.mt = None
        self.icon = None

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
        if self.icon is not None:
            return self.icon
        elif self.isdir:
            self.icon = dir_icon
            return dir_icon
        else:
            self.mt = mimetypes.guess_type(self.path)[0]
            self.icon = icons.icons.get_mime_image(self.mt)
            if self.icon:
                return self.icon
            elif self.name.endswith('.pida'):
                self.icon = pida_icon
                return self.icon
            
    pixbuf = property(get_pixbuf)


class FileTree(tree.IconTree):
    
    SORT_AVAILABLE = [('Directories first', 'isnotdir'),
                    ('File name', 'name'),
                    ('Version Control status', 'status'),
                    ('File Extension', 'extension')]

    SORT_CONTROLS = True

import pida.utils.vc as vc


class StatusLister(object):

    def __init__(self, view, counter, counter_check, show_hidden,
                       hidden_globs):
        self.counter = counter
        self._view = view
        self._results = {}
        self._no_statuses = False
        self.show_hidden = show_hidden
        self.check_counter = counter_check
        # this is one of the leetest things I ever did
        p = glob.re.compile('|'.join(map(glob.fnmatch.translate, hidden_globs)))
        self.hidden_globs = p

    
    def add_item(self, path, status):
        if not self.check_counter(self.counter):
            return
        try:
            fsi = self._results[path]
            fsi.status = status
            self.reset_item(fsi) 
        except KeyError:
            fsi = FileSystemItem(path)
            fsi.status = status
            fsi.statused = False
            self._results[path] = fsi
            self.add_view_item(fsi)
        return fsi
        
    def list(self, directory):
        self._busy()
        pt = threading.Thread(target=self.plain_ls, args=(directory,))
        st = threading.Thread(target=self.status_ls, args=(directory,))
        pt.start()
        st.start()
        def _finish(pt, st):
            pt.join()
            st.join()
            self.finished()
            self._unbusy()
        threading.Thread(target=_finish, args=(pt, st)).start()
    
    def _busy(self):
        if self._view.view.window:
            self._view.view.window.set_cursor(busy_cursor)
            
    def _unbusy(self):
        if self._view.view.window:
            self._view.view.window.set_cursor(normal_cursor)
    
    def plain_ls(self, directory):
        for name in os.listdir(directory):
            if self.is_hidden(name): continue
            self.add_item(os.path.join(directory, name), STATE_NORMAL)
    
    def status_ls(self, directory):
        vcdir = vc.Vc(directory)
        if vcdir.NAME == 'Null':
            self._no_statuses = True
        else:
            statuses = vcdir.listdir(directory)
            for status in statuses:
                if self.is_hidden(status.name): continue
                item = self.add_item(status.path, status.state)
                if item:
                    item.statused = True

    def finished(self):
        if not self.check_counter(self.counter):
            return
        if not self._no_statuses:
            for res in self._results.values():
                if not res.statused:
                    res.status = STATE_IGNORED
                    self.reset_item(res)
        # need to scroll for some bizarre reason
        def scroll():
            self._view.view.scroll_to_cell((0,))
        gobject.idle_add(scroll)
        
    def reset_item(self, item):
        def _reset_item():
            item.reset_markup()
        gobject.idle_add(_reset_item)

    def add_view_item(self, item):
        def _add_item():
            self._view.add_item(item)
        gobject.idle_add(_add_item)

    def is_hidden(self, name):
        if self.show_hidden:
            return False
        else:
            if name.startswith('.'):
                return True
            else:
                return self.hidden_globs.match(name)

class FileBrowser(contentview.content_view):

    gsignal('file-activated', str)

    ICON_NAME = 'filemanager'
    LONG_TITLE = 'File manager'
    SHORT_TITLE = 'Files'
    HAS_CLOSE_BUTTON = False
    HAS_DETACH_BUTTON = False
    HAS_TITLE = False
    HAS_CONTROL_BOX = False

    def init(self, scriptpath):
        gobject.GObject.__init__(self)
        self.cwd = None
        self.create_toolbar()
        self.create_actions()
        self.create_tree()
        self.counter = 0

    def create_toolbar(self):
        self._toolbar= gtk.Toolbar()
        self.widget.pack_start(self._toolbar, expand=False)
        self._toolbar.set_icon_size(gtk.ICON_SIZE_MENU)
        self._toolbar.set_style(gtk.TOOLBAR_ICONS)

    def create_actions(self):
        self._tips = gtk.Tooltips()
        self._homeact = gtk.Action('Home', 'Home',
                                   'Browse the project root', 'gtk-project')
        self.add_action_to_toolbar(self._homeact)
        self._homeact.connect('activate', self.cb_act_home)
        self._upact = gtk.Action('Up', 'Up',
            'Browse the parent directory', gtk.STOCK_GO_UP)
        self.add_action_to_toolbar(self._upact)
        self._upact.connect('activate', self.cb_act_up)
        self._refreshact = gtk.Action('Refresh', 'Refresh',
            'Refresh the directory', gtk.STOCK_REFRESH)
        self.add_action_to_toolbar(self._refreshact)
        self._refreshact.connect('activate', self.cb_act_refresh)
        self._hidden_act = gtk.ToggleAction('ShowHidden', 'ShowHidden',
            'Show the hidden files', 'gtk-hidden')
        self._hidden_act.connect('toggled', self.cb_show_hidden)
        self.add_action_to_toolbar(self._hidden_act)
        self._newfileact = gtk.Action('New', 'New',
                            'Create a new file here', gtk.STOCK_NEW)
        #self.add_action_to_toolbar(self._newfileact)
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
        toolitem.set_tooltip(self._tips, action.props.tooltip)
        return toolitem
    
    def create_tree(self):
        self._view = FileTree()
        self._view.set_property('markup-format-string', '%(markup)s')
        self._view.connect('double-clicked', self.cb_double_click)
        self._view.connect('right-clicked', self.cb_right_click)
        self.widget.pack_start(self._view)
        return self._view

    def check_counter(self, counter):
        return counter == self.counter

    def browse(self, directory=None):
        if directory is None:
            directory = os.path.expanduser('~')
        self.service.events.emit('directory_changed', directory=directory)
        self.counter = self.counter + 1
        lister = StatusLister(self._view, self.counter, self.check_counter,
                              self.get_show_hidden(), self.get_hidden_mask())
        self._view.clear()
        self.cwd = directory
        lister.list(directory)

    def browse_up(self):
        directory = self.cwd
        if directory is not None and directory != '/':
            parent = os.path.dirname(directory)
            self.browse(parent)
   
    def refresh(self):
        if self.cwd is not None:
            self._visrect = self._view.view.get_visible_rect()
            self.browse(self.cwd)

    def cb_double_click(self, tv, item):
        fsi = item.value
        if fsi.isdir:
            self.browse(fsi.path)
        else:
            self.emit('file-activated', fsi.path)
        
    def cb_act_up(self, action):
        self.browse_up()

    def cb_act_refresh(self, action):
        self.refresh()

    def cb_act_home(self, action):
        project = self.service.boss.call_command('projectmanager',
                                         'get_current_project')
        if project is not None:
            project_root = project.source__directory
            self.service.call('browse', directory=project_root)
        else:
            self.service.log.info('there is no project to go to its root')

    def cb_show_hidden(self, action):
        self.refresh()
    
    def get_show_hidden(self):
        return self._hidden_act.get_active()
    
    def get_hidden_mask(self):
        mask = self.service.opts.hidden__mask
        globs = [s for s in mask.split(';') if s]
        return globs

    def cb_act_new_file(self, action):
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

gobject.type_register(FileBrowser)

class FileManagerOptions:

    class hidden:
        """Options relating to hidden files"""
        label = 'Hidden Files'
        class mask:
            label = 'Hidden file mask (; separated)'
            rtype = types.string
            default = ''
    __markup__ = lambda self: 'File Browser'

class file_manager(service.service):

    config_definition = FileManagerOptions

    class FileBrowser(defs.View):
        view_type = FileBrowser
        book_name = 'content'

    class directory_changed(defs.event):
        """Called when the current directory is changed."""

    def init(self):
        self.__content = None
        self.plugin_view = self.create_view('FileBrowser', scriptpath=None)
        self.plugin_view.connect('file-activated',
                                  self.cb_single_view_file_activated)

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
        if directory is None:
            directory = os.path.expanduser('~')
        self.plugin_view.browse(directory)
        self.plugin_view.raise_page()

    def cmd_get_current_directory(self):
        return self.plugin_view.cwd

    def cmd_refresh(self, cwd=None):
        if cwd is not None and self.plugin_view.cwd == cwd:
            self.plugin_view.refresh()

    def cb_single_view_file_activated(self, view, filename):
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)

    def get_plugin_view(self):
        return self.get_first_view('FileBrowser')
    splugin_view = property(get_plugin_view)

        
Service = file_manager

