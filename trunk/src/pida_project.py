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

import gtk
import plugin
#import tree
import ConfigParser
import os
import dialogs
import tree
import gtkextra
VCS_NONE = 0
VCS_DARCS = 1
VCS_CVS = 2
VCS_SVN = 3



VCS = {0: 'None', 1: 'Darcs', 2: 'CVS', 3: 'SVN'}

CWD = '__current__working_directory__'

class CommandMapper(object):
    def __init__(self, cb):
        self.cb = cb
        self.set()


class Darcs(CommandMapper):
        def set(self):
            self.command = '/usr/bin/darcs'
            self.args = ['darcs']
            self.commit = ['record']
            self.update = ['pull']

class Cvs(CommandMapper):
        def set(self):
            self.command = '/usr/bin/cvs'
            self.args = ['cvs']
            self.commit = ['commit']
            self.update = ['update']
            self.add = ['add']
            self.remove = ['remove']

class Svn(CommandMapper):
        def set(self):
            self.command = '/usr/bin/svn'
            self.args = ['svn']
            self.commit = ['commit']
            self.update = ['update']
            self.add = ['add']
            self.remove = ['remove']

def analyze_working_directory(dirname):
    exists = os.path.exists(dirname)
    vcs = 0
    if exists:
        for i in os.listdir(dirname):
            if i == '_darcs':
                vcs = VCS_DARCS
                break
            elif i == '.svn':
                vcs = VCS_SVN
                break
            elif i == 'CVS':
                vcs = VCS_CVS
                break
    return exists, vcs

import gobject

class FileTree(gtkextra.Tree):
    COLUMNS = [('name', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup'),
                ('file', gobject.TYPE_STRING, None, False,
                'text')]

    def init(self):
        tb = gtk.VBox()
        self.toolbar.pack_start(tb, expand=False)
        
        self.dir_label = gtk.Label()
        tb.pack_start(self.dir_label)
        
        ctrls = gtkextra.Toolbar(self.cb)
        tb.pack_start(ctrls.win)

        ctrls.add_button('up', self.cb_but,
            'Go to the parent directory', ['up'])
        ctrls.add_button('new', self.cb_but,
            'Create a new file, and edit it in vim.', ['new'])
        ctrls.add_button('open', self.cb_but,
            'Open the file in vim.', ['open'])
        ctrls.add_button('delete', self.cb_but,
            'Delete the file.', ['delete'])
        ctrls.add_separator()
        ctrls.add_button('terminal', self.cb_but,
            'Open a shell in the current directory', ['terminal'])
        #self.view.connect('row-expanded', self.cb_expand)
        self.view.connect('test-expand-row', self.cb_expand)
        
        self.filemenu = gtkextra.ContextPopup(self.cb, 'file')
        self.dirmenu = gtkextra.ContextPopup(self.cb, 'dir')

        self.root = None
        
    def set_root(self, path, parent=None):
        def small(s):
            return '<span size="small">%s</span>' % s
        def smallblue(s):
            dircol = self.cb.opts.get('project browser', 'color_directory')
            return '<span size="small" foreground="%s">%s</span>' % (dircol,s)
        if path == 'None':
            return
        dirs = []
        files = []
        try:
            flist = os.listdir(path)
        except OSError:
            flist = []
        for fn in flist:
            fp = os.path.join(path, fn)
            if os.path.isdir(fp):
                dirs.append((smallblue('%s%s' % (fn, os.path.sep)), fp))
            else:
                files.append((small(fn), fp))
        if not parent:
            self.root = path
            self.set_dir_label(path)
            #self.add_item([smallblue('../'), os.path.split(path)[0]])
        dirs.sort()
        for d in dirs:
            par = self.add_item(d, parent)
            self.add_item([small('empty...'), ''], par)
        files.sort()
        for f in files:
            par = self.add_item(f, parent)
        self.update()
        return len(dirs + files)
   
    def refresh(self):
        self.clear()
        self.set_root(self.root)
        self.update() 
    
    def up(self):
        self.clear()
        parent = os.path.split(self.root)[0]
        self.set_root(parent)
        self.update()
    
    def get_selected_root(self, fn):
        root = self.root
        if fn:
            if os.path.isdir(fn):
                root = fn
            else:
                root, f = os.path.split(fn)
        return root

    def set_dir_label(self, path):
        s = '<span size="small" weight="bold">%s</span>'
        path = path.replace(os.path.expanduser('~'), '~')
        self.dir_label.set_markup(s % path)

    def cb_expand(self, tv, parent, path):
        child = self.model.iter_children(parent)
        if self.get(child, 1) == '':
            root = self.get(parent, 1)
            if self.set_root(root, parent):
                self.model.remove(child)
         
    def l_cb_activated(self, tv, path, niter):
        niter = self.model.get_iter(path)
        isdir = self.model.iter_has_child(niter)
        if isdir:
            self.toggle_expand(self.selected_path())
            return False
        #elif self.selected(0).count('../'):
        #    root = self.selected(1)
        #    self.clear()
        #    self.set_root(root, None)
        #    return False
        else:
            return True

    def l_cb_rightclick(self, ite, time):
        fn = self.get(ite, 1)
        if os.path.isdir(fn):
            self.dirmenu.popup(fn, time)
        else:
            self.filemenu.popup(fn, time)
        

    def cb_but(self, but, command):
        fn = self.selected(1)
        com = getattr(self, 'cb_but_%s' % command,
                lambda fn: (False, 'Unknown Command:\n"%s"' % command))
        com(fn)

    def cb_but_open(self, fn):
        if fn:
            if not os.path.isdir(fn):
                self.cb.action_openfile(fn)

    def cb_but_new(self, fn):
        root = self.get_selected_root(fn)
        def create(nn):
            newfn = os.path.join(root, nn)
            open(newfn, 'w').close()
            self.refresh()
            self.cb.action_openfile(newfn)
        self.pcb.question('Name of the file?', create)

    def cb_but_delete(self, fn):
        if fn:
            os.remove(fn)
            self.refresh()

    def cb_but_up(self, fn):
        self.up()

    def cb_but_terminal(self, fn):
        root = self.get_selected_root(fn)
        shell = self.cb.opts.get('commands', 'shell')
        self.cb.action_newterminal(shell, ['shell'], directory=root)
        

class ProjectTree(gtkextra.Tree):
    COLUMNS = [('Name', gobject.TYPE_STRING, gtk.CellRendererText, False,
                'text'),
               ('Display', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup')]
   
    def init(self):
        self.view.set_reorderable(True)
          
    def set_active(self, i):
        for node in self.model:
            if node[0] == i:
                self.view.set_cursor(node.path)
                return True
        return False

class Projecteditor(gtkextra.Transient):
    def populate_widgets(self):
        gtkextra.Transient.populate_widgets(self)

        self.fr = self.frame

        self.name_label = gtk.Label('Name of project')
        self.fr.pack_start(self.name_label, expand=False)

        self.name_entry = gtk.Entry()
        def cb(*args):
            self.wd_file_but.entry.grab_focus()
        self.name_entry.connect('activate', cb)
        self.fr.pack_start(self.name_entry)
        
        sep = gtk.HSeparator()
        self.fr.pack_start(sep)
                
        wdl = ('Relative paths are taken relative to the current working '
               'directory.')

        self.wd_label = gtk.Label('Working directory')
        self.fr.pack_start(self.wd_label, expand=False)


        self.wd_file = dialogs.FolderDialog(self.cb, lambda *a: None)
        self.wd_file_but = dialogs.FolderButton(self.cb)
        self.fr.pack_start(self.wd_file_but, expand=False)
        
        sep = gtk.HSeparator()
        self.fr.pack_start(sep)


        self.bbox = gtk.HBox()
        self.fr.pack_start(self.bbox)
        
        sep = gtk.HSeparator()
        self.bbox.pack_start(sep)

        self.cancel = self.cb.icons.get_button('cancel', 14)
        eb = gtk.EventBox()
        eb.add(self.cancel)
        self.bbox.pack_start(eb, expand=False)
        self.cb.tips.set_tip(eb, 'Cancel project addition')
        self.cancel.connect('clicked', self.cb_hide)

        eb = gtk.EventBox()
        self.submit = self.cb.icons.get_button('apply', 14)
        eb.add(self.submit)
        self.cb.tips.set_tip(eb, 'Submit project addition')
        self.bbox.pack_start(eb, expand=False)

    def cb_hide(self, *args):
        self.hide()


    def new(self):
        self.name_entry.set_text('')
        self.wd_file_but.set_filename(os.path.expanduser('~'))
        self.show('New Project')
        self.name_entry.grab_focus()

class Plugin(plugin.Plugin):
    NAME = 'Projects'
    ICON = 'project'
    DICON = 'terminal', 'Open a terminal in this directory.'

    def populate_widgets(self):
        #self.tree = tree.Tree(self.cb, self.beautify)
        #self.tree.show()
        #self.tree.view.connect('cursor-changed', self.cb_changed)
        #self.add(self.tree)

        vp = gtk.VPaned()
        self.add(vp)

        self.projects = ProjectTree(self.cb)
        self.projects.connect_select(self.cb_projchanged)
        self.projects.connect_rightclick(self.cb_proj_rclick)
        vp.pack1(self.projects.win, resize=True, shrink=True)

        self.files = FileTree(self.cb)
        self.files.pcb = self

        self.files.connect_activate(self.cb_files_activate)
        vp.pack2(self.files.win, resize=True, shrink=True)


        self.add_button('remove', self.cb_cvs,
                        'Remove file from version control.', ['remove', True])
        self.add_button('add', self.cb_cvs,
                        'Add file to to version control', ['add', True])
        self.add_button('up', self.cb_cvs,
                        'Commit changes to version control', ['commit'])
        self.add_button('down', self.cb_cvs,
                        'Update changes from version control', ['update'])

        sep = gtk.VSeparator()
        self.cusbar.pack_start(sep, expand=False)

        self.add_button('delete', self.cb_project_del,
                        'Remove project from workspace.')
        self.add_button('new', self.cb_project_new,
                        'Add project to workbench.')


        self.editor = Projecteditor(self.cb)
        self.transwin.pack_start(self.editor.win, expand=False)
        self.editor.submit.connect('clicked', self.cb_project_edited)
        self.editor.wd_file_but.entry.connect('activate', self.cb_project_edited)
    
        self.dirmenu = gtkextra.ContextPopup(self.cb, 'dir')

        self.config = ConfigParser.ConfigParser()

        self.maps = {1: Darcs(self.cb),
                     2: Cvs(self.cb),
                     3: Svn(self.cb)}


    def cb_cvs(self, but, command, inc_filename=False):
        self.cvs_command(command, inc_filename)

    def cb_proj_rclick(self, ite, time):
        n = self.projects.get(ite, 0)
        wd = self.config.get(n, 'directory')
        self.dirmenu.popup(wd, time)

    def cvs_command(self, command, inc_filename):
        name = self.projects.selected(0)
        vcs = self.config.get(name, 'version_control')
        for vc in VCS:
            if VCS[vc] == vcs:
                if vc in self.maps:
                    map = self.maps[vc]
                    if hasattr(map, command):
                        com = map.command
                        args = map.args + getattr(map, command)
                        dir = self.config.get(name, 'directory')
                        if inc_filename:
                            rfn = self.files.selected(1)
                            if rfn:
                                fn = rfn.replace(dir, '').lstrip('/')
                                args.append(fn)
                            else:
                                self.message('No file is selected.\n'
                                             'Please select a file,\n'
                                             'and try again.')
                                return
                        print args
                        self.cb.action_newterminal(com, args, directory=dir)
                    else:
                        self.message('Unsupported command:\n'
                                     '"%s" (%s)' % (command, vcs))
    
                
                

    def cb_project_edited(self, *a):
        name = self.editor.name_entry.get_text()
        #wd = self.editor.wd_entry.get_text()
        wd = self.editor.wd_file_but.get_filename()
        self.add_project(name, wd)
        self.editor.hide()

    def cb_details(self):
        self.editor.show()

    def add_project(self, name, dir):
        if self.config.has_section(name):
            self.message('Name already exists') 
        else:
            exists, vcs = analyze_working_directory(dir)
            if not exists:
                try:
                    os.mkdir(dir)
                    exists = True
                except OSError:
                    exists = False
            exists, vcs = analyze_working_directory(dir)
            if exists:
                self.config.add_section(name)
                self.config.set(name, 'directory', dir)
                self.config.set(name, 'version_control', VCS[vcs])
                self.write()
                self.refresh()
            else:
                self.message('Unable to create working directory.')

    def analyse_project(self, name):
        wd = self.config.get(name, 'directory')
        exists, vcs = analyze_working_directory(wd)
        if exists:
            self.config.set(name, 'version_control', VCS[vcs])
        elif name == CWD:
            self.config.set(name, 'version_control', 'None')
        else:
            print 'removing section'
            self.config.remove_section(name)

    def load(self):
        fn = self.cb.opts.get('files', 'data_project')
        if os.path.exists(fn):
            f = open(fn, 'r')
            self.config.readfp(f)
            f.close()
        if not self.config.has_section(CWD):
            self.config.add_section(CWD)
        self.config.set(CWD, 'directory', 'None')
        self.write()

    def write(self):
        fn = self.cb.opts.get('files', 'data_project')
        f = open(fn, 'w')
        self.config.write(f)
        f.close()
        
    def refresh(self):
        act = self.projects.selected(0) 
        self.projects.clear()
        for name in self.config.sections():
            self.analyse_project(name)
            self.projects.add_item([name, self.beautify(name)])
        if act:
            self.projects.set_active(act)
        else:
            self.projects.set_active(CWD)

    def set_current(self, cwd):
        self.config.set(CWD, 'directory', cwd)
        self.analyse_project(CWD)
        self.write()
        self.refresh()

    def beautify(self, section):
        vcs = self.config.get(section, 'version_control')
        wd = self.config.get(section, 'directory')
        wd = wd.replace(os.path.expanduser('~'), '~')
        if section == CWD:
            section = '<span foreground="#c00000">Currrent Directory</span>'
        b = ('<span size="small"><b>%s</b> ('
            '<span foreground="#0000c0">%s</span>)\n'
            '%s</span>') % (section, vcs, wd)
        return b
       
    #def cb_changed(self, path):
    #    i = self.tree.get_selected_id()
    #    path = self.config.get(i, 'directory')
    #    self.files.clear()
    #    self.files.set_root(path)
 
    def cb_projchanged(self, tv):
        name = self.projects.selected(0)
        path = self.config.get(name, 'directory')
        self.files.clear()
        self.files.set_root(path)

    def cb_files_activate(self, tv, path, niter):
        fn = self.files.selected(1)
        self.cb.action_openfile(fn)

    def evt_started(self, *args):
        self.editor.hide()
        self.load()
        self.refresh()
       
    def evt_bufferchange(self, nr, name):
        cwd = os.path.split(name)[0]
        if cwd != self.config.get(CWD, 'directory'):
            self.set_current(cwd)
            if self.projects.selected(0) == '__current__':
                self.cb_changed(cwd)

    def evt_projectexecute(self, arg):
        name = self.projects.selected(0)
        if self.config.has_option(name, 'project_executable'):
            ex = self.config.get(name, 'project_executable')
            py = self.cb.opts.get('commands', 'python')
            self.cb.action_newterminal(py, ['python', ex])
        else:
            self.cb.action_log('Execution Failed',
            'No main file defined for project.', 3)
            

    def cb_project_del(self, *args):
        a = self.projects.selected(0)
        self.config.remove_section(a)
        self.write()
        self.refresh()

    def cb_project_new(self, *args):
        self.editor.new()

    def cb_terminal_proj(self, *a):
        name = self.projects.selected(0)
        wd = self.config.get(name, 'directory')
        shell = self.cb.opts.get('commands', 'shell')
        self.cb.action_newterminal(shell, ['shell'], directory=wd)

    cb_alternative = cb_terminal_proj

