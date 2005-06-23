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

# GTK imports
import gtk
import gobject
# system imports
import os
import re
import ConfigParser
# Pida imports
import pida.plugin as plugin
import pida.gtkextra as gtkextra

VCS_NONE = 0
VCS_DARCS = 1
VCS_CVS = 2
VCS_SVN = 3

VCS = {VCS_NONE: 'None',
       VCS_DARCS: 'Darcs',
       VCS_CVS: 'CVS',
       VCS_SVN: 'SVN'}

CWD = '__current__working_directory__'

# Default attributes for projects
PROJECT_ATTRIBUTES = [
    ('directory',
     'The working directory the project is in',
     os.path.expanduser('~'),
     'folder'),
    ('project_executable',
     'The executable file for the project',
     '',
     'file'),
    ('environment',
     'The environment variable list',
     '',
     None)]

class ProjectRegistry(ConfigParser.ConfigParser):
    """
    A class to store, and serialize project data.
    """
    def __init__(self, cb, filename):
        """
        Constructor.

        @param cb: An instance of the main application class.
        @type cb: pida.main.Application

        @param filename: The filename for storing the data.
        @type filename: str
        """
        self.cb = cb
        ConfigParser.ConfigParser.__init__(self)
        self.filename = filename
        self.types = {}
        for attribute in PROJECT_ATTRIBUTES:
            self.types[attribute[0]] = attribute[3]

    def set_project(self, projname, **kw):
        """
        Set the attributes for a project.
        
        This method creates the project if it is not existing.

        @param projnmame: the name of the project
        @type projname: str
        
        @param **kw: The attributes as keywords
        """
        if not self.has_section(projname):
            self.add_section(projname)
        for attribute in PROJECT_ATTRIBUTES:
            name = attribute[0]
            if name in kw:
                self.set(projname, name, kw[name])
            else:
                default = attribute[2]
                self.set(projname, name, default)

    def delete(self, projname):
        """
        Delete the named section from the in memory object.
        """
        if self.has_section(projname):
            self.remove_section(projname)

    def load(self):
        """
        Load the disk data into memory.
        
        This method checks the loaded attributes, replacing bad/missing
        attributes with sensible defaults.
        """
        tempopts = ConfigParser.ConfigParser()
        if os.path.exists(self.filename):
            f = open(self.filename, 'r')
            tempopts.readfp(f)
            f.close()
            kw = {}
            for section in tempopts.sections():
                if not section == CWD and tempopts.has_option(section, 'directory'):
                    for option in tempopts.options(section):
                        kw[option] = tempopts.get(section, option)
                    self.set_project(section, **kw)

    def save(self):
        """
        Write the in-memory object to disk.
        """
        f = open(self.filename, 'w')
        self.write(f)
        f.close()

class ProjectEditor(object):
    def __init__(self, cb, project_registry):
        self.cb = cb
        self.project_registry = project_registry
        
        self.win = gtk.Window()
        self.win.set_title('PIDA Project Editor')
        self.win.set_size_request(600,480)
        self.win.set_transient_for(self.cb.cw)

        mainbox = gtk.HBox()
        self.win.add(mainbox)

        leftbox = gtk.VBox()
        mainbox.pack_start(leftbox)

        self.projects = ProjectTree(self.cb)
        leftbox.pack_start(self.projects.win)
        self.projects.connect_select(self.cb_project_select)
        self.projects.populate(self.project_registry)

        rightbox = gtk.VBox()
        mainbox.pack_start(rightbox)

        attrbox = gtk.VBox()
        rightbox.pack_start(attrbox)


        hbox = gtk.HBox()
        attrbox.pack_start(hbox, expand=False, padding=4)
        namelabel = gtk.Label('name')
        hbox.pack_start(namelabel, expand=False, padding=4)
        self.nameentry = gtk.Entry()
        hbox.pack_start(self.nameentry)

        self.attribute_widgets = {}
        for attribute in PROJECT_ATTRIBUTES:
            hbox = gtk.HBox()
            attrbox.pack_start(hbox, expand=False, padding=4)
            name = attribute[0]
            namelabel = gtk.Label(name)
            hbox.pack_start(namelabel, expand=False, padding=4)
            entry = gtk.Entry()
            hbox.pack_start(entry)
            self.attribute_widgets[name] = entry
        
        # Button Bar
        cb = gtk.HBox()
        rightbox.pack_start(cb, expand=False, padding=2)
        
        # separator
        sep = gtk.HSeparator()
        cb.pack_start(sep)
        
        # reset button
        revert_b = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        cb.pack_start(revert_b, expand=False)
        revert_b.connect('clicked', self.cb_revert)

        # cancel button
        delete_b = gtk.Button(stock=gtk.STOCK_DELETE)
        cb.pack_start(delete_b, expand=False)
        delete_b.connect('clicked', self.cb_delete)
        
        # apply button
        new_b = gtk.Button(stock=gtk.STOCK_NEW)
        cb.pack_start(new_b, expand=False)
        new_b.connect('clicked', self.cb_new)
        
        # save button
        save_b = gtk.Button(stock=gtk.STOCK_SAVE)
        cb.pack_start(save_b, expand=False)
        save_b.connect('clicked', self.cb_save)
    
    def new(self):
        self.nameentry.set_text('')
        for attribute in PROJECT_ATTRIBUTES:
            attrname = attribute[0]
            self.attribute_widgets[attrname].set_text('')

    def show(self):
        self.win.show_all()

    def display(self, projectname):
        if self.project_registry.has_section(projectname):
            self.nameentry.set_text(projectname)
            for attribute in PROJECT_ATTRIBUTES:
                attrname = attribute[0]
                val = self.project_registry.get(projectname, attrname)
                self.attribute_widgets[attribute[0]].set_text(val)
            
    def projects_changed(self):
        self.project_registry.save()
        self.projects.populate(self.project_registry)
        self.cb.evt('projectschanged')
            
    def cb_project_select(self, *args):
        projname = self.projects.selected(0)
        self.display(projname)
         
    def cb_new(self, *args):
        self.new()

    def cb_revert(self, *args):
        self.project_registry.load()
        self.projects_changed()

    def cb_save(self, *args):
        name = self.nameentry.get_text()
        if name:
            kw = {}
            for attrname in self.attribute_widgets:
                kw[attrname] = self.attribute_widgets[attrname].get_text()
            self.project_registry.set_project(name, **kw)
            self.projects_changed()

    def cb_delete(self, *args):
        projname = self.projects.selected(0)
        self.project_registry.delete(projname)
        self.projects_changed()
        self.projects.view.set_cursor(self.projects.model[0].path)

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
        if not parent and path == self.root:
            return
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
        if self.cb.opts.get('project browser', 'tree_exclude') != '0':
            pattern = re.compile(self.cb.opts.get('project browser', 'pattern_exclude'))
            flist = [fn for fn in flist if not pattern.match(fn)]
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
        if self.projects.selected(0) == CWD:
            self.set_root(self.config.get(CWD, 'directory'))
        else:
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
   
    def populate(self, project_registry, cwd=None):
        self.project_registry = project_registry
        act = self.selected(0)
        self.clear()
        if cwd:
            self.add_item([CWD, self.beautify('<span foreground="#c00000">'
                                              'Current Directory</span>', cwd)])
        for name in self.project_registry.sections():
            wd = self.project_registry.get(name, 'directory')
            self.add_item([name, self.beautify(name, wd)])
        if act:
            self.set_active(act)
          
    def beautify(self, name, directory):
        vcs = get_vcs_name_for_directory(directory)
        wd = directory
        wd = wd.replace(os.path.expanduser('~'), '~')
        b = ('<span size="small"><b>%s</b> ('
            '<span foreground="#0000c0">%s</span>)\n'
            '%s</span>') % (name, vcs, wd)
        return b
        
    def set_active(self, i):
        for node in self.model:
            if node[0] == i:
                self.view.set_cursor(node.path)
                return True
        return False

    def change_cwd(self, cwd):
        niter = self.model[0].iter
        if self.get(niter, 0) == CWD:
            self.set(niter, 1, self.beautify('<span foreground="#c00000">'
                                              'Current Directory</span>', cwd))
            if self.selected(0) == CWD:
                self.cb_selected()

class Plugin(plugin.Plugin):
    NAME = 'Projects'
    ICON = 'project'
    DICON = 'terminal', 'Open a terminal in this directory.'

    def populate_widgets(self):
        self.vcsbar = gtk.EventBox()
        self.add(self.vcsbar, expand=False)

        vp = gtk.VPaned()
        self.add(vp)

        self.projects = ProjectTree(self.cb)
        self.projects.connect_select(self.cb_project_select)
        self.projects.connect_rightclick(self.cb_project_rclick)
        vp.pack1(self.projects.win, resize=True, shrink=True)

        self.files = FileTree(self.cb)
        self.files.pcb = self

        self.files.connect_activate(self.cb_files_activate)
        vp.pack2(self.files.win, resize=True, shrink=True)

        sep = gtk.VSeparator()
        self.cusbar.pack_start(sep, expand=False)

        self.add_button('new', self.cb_project_new,
                        'Add project to workbench.')
        self.add_button('editor', self.cb_project_edit,
                        'Edit projects on workbench.')
   
        self.dirmenu = gtkextra.ContextPopup(self.cb, 'dir')

        self.current_directory = os.getcwd()
    
        conffile = fn = self.cb.opts.get('files', 'data_project')
        
        self.config = ProjectRegistry(self.cb, conffile)
        self.config.load()
        self.projects.populate(self.config, self.current_directory)

        self.editor = None

        self.maps = create_vcs_maps(self.cb, self.cb_vcs_command)

    def vcs_command(self, vcsmap, command):
        commandname = 'command_%s' % command
        commandfunc = getattr(vcsmap, commandname, None)
        if commandfunc:
            kw = {}
            projname = self.projects.selected(0)
            if projname == CWD:
                kw['dir'] = self.current_directory
                kw['env'] = []
            else:
                kw['dir'] = self.config.get(projname, 'directory')
                envs = self.config.get(projname, 'environment')
                kw['env'] = envs.split(';')
            kw['filename'] = self.files.selected(0)
            commandfunc(**kw)
        else:
            self.message('Unsupported command %s' % command)

    def show_editor(self):
        if self.editor:
            del self.editor
        self.editor = ProjectEditor(self.cb, self.config)
        self.editor.show()
       
    def cb_vcs_command(self, but, vcsmap, command):
        self.vcs_command(vcsmap, command)

    def cb_project_select(self, *args):
        name = self.projects.selected(0)
        path = None
        if name == CWD:
            path = self.current_directory
        else:
            path = self.config.get(name, 'directory')
        if path != self.files.root:
            self.files.clear()
            self.files.set_root(path)
        vcs = get_vcs_for_directory(path)

        curbar = self.vcsbar.get_child()
        if curbar:
            self.vcsbar.remove(curbar)
        if vcs in self.maps:
            newbar = self.maps[vcs].toolbar.win
            self.vcsbar.add(newbar)
            self.vcsbar.show_all()

    def cb_project_rclick(self, ite, time):
        n = self.projects.get(ite, 0)
        wd = self.config.get(n, 'directory')
        self.dirmenu.popup(wd, time)

    def cb_files_activate(self, tv, path, niter):
        fn = self.files.selected(1)
        self.cb.action_openfile(fn)
       
    def cb_project_new(self, *args):
        self.show_editor()
        self.editor.new()

    def cb_project_edit(self, *args):
        self.show_editor()

    def cb_alternative(self, *a):
        name = self.projects.selected(0)
        wd = self.config.get(name, 'directory')
        shell = self.cb.opts.get('commands', 'shell')
        self.cb.action_newterminal(shell, ['shell'], directory=wd)

    def evt_projectschanged(self, *a):
        self.config.load()
        self.projects.populate(self.config, self.current_directory)

    def evt_bufferchange(self, nr, name):
        cwd = os.path.split(name)[0]
        self.current_directory = cwd
        self.projects.change_cwd(cwd)

    def evt_projectexecute(self, arg):
        name = self.projects.selected(0)
        if self.config.has_option(name, 'project_executable'):
            ex = self.config.get(name, 'project_executable')
            py = self.cb.opts.get('commands', 'python')
            self.cb.action_newterminal(py, ['python', ex])
        else:
            self.cb.action_log('Execution Failed',
            'No main file defined for project.', 3)

class VersionControlSystem(object):
    COMMAND = ''
    ARGS = []

    def __init__(self, cb, callbackfunc):
        self.cb = cb
        self.callbackfunc = callbackfunc
        self.toolbar = gtkextra.Toolbar(self.cb)
        self.add_default_buttons()
        self.add_custom_buttons()

    def add_default_buttons(self):
        self.add_button('remove', 'remove',
                        'Remove file from version control.')
        self.add_button('add', 'add',
                        'Add file to to version control')
        self.add_button('commit', 'commit',
                        'Commit changes to version control')
        self.add_button('down', 'update',
                        'Update changes from version control')

    def add_custom_buttons(self):
        pass

    def add_button(self, icon, command, tooltip):
        cargs = [self, command]
        return self.toolbar.add_button(icon, self.callbackfunc, tooltip, cargs)

    def launch(self, args, **kw):
        args = self.ARGS + args
        self.cb.action_newterminal(self.COMMAND, args,
                                   directory=kw['dir'], envv=kw['env'])

class Darcs(VersionControlSystem):
    COMMAND = '/usr/bin/darcs'
    ARGS = ['darcs']

    def command_commit(self, **kw):
        self.launch(['record'], **kw)

    def command_send(self, **kw):
        self.launch(['send'], **kw)
        
class Subversion(VersionControlSystem):
    COMMAND = '/usr/bin/svn'
    ARGS = ['svn']

    def command_update(self, **kw):
        self.launch(['update'], **kw)
    
    def command_commit(self, **kw):
        self.launch(['commit'], **kw)

def create_vcs_maps(cb, callbackfunc):
    return {VCS_DARCS: Darcs(cb, callbackfunc),
            VCS_SVN: Subversion(cb, callbackfunc)}

def get_vcs_for_directory(dirname):
    vcs = 0
    if os.path.exists(dirname) and os.path.isdir(dirname):
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
    return vcs

def get_vcs_name_for_directory(dirname):
    return VCS[get_vcs_for_directory(dirname)]
