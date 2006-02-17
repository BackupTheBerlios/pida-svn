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

import gtk
import gobject

import pida.core.service as service
import pida.core.actions as actions
import pida.pidagtk.contentview as contentview

import pida.utils.vc as vc

defs = service.definitions
types = service.types

class CommitView(contentview.content_view):

    SHORT_TITLE = 'Commit'
    ICON_NAME = 'vcs_commit'
    HAS_CONTROL_BOX = False

    def init(self):
        self._text = gtk.TextView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self._text)
        self.widget.pack_start(sw)
        bb = gtk.HButtonBox()
        self.widget.pack_start(bb, expand=False)
        bb.set_layout(gtk.BUTTONBOX_END)
        _ok = gtk.Button(stock=gtk.STOCK_OK)
        _ok.connect('clicked', self.on_ok__clicked)
        _cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        _cancel.connect('clicked', self.on_cancel__clicked)
        bb.pack_start(_cancel)
        bb.pack_start(_ok)

    def on_ok__clicked(self, button):
        text = self._get_text()
        self._callback(text)

    def on_cancel__clicked(self, button):
        self.close()

    def grab_focus(self):
        self._text.grab_focus()

    def set_callback(self, callback):
        self._callback = callback
        self._text.get_buffer().set_text('')

    def _get_text(self):
        e = self._text.get_buffer().get_end_iter()
        s = self._text.get_buffer().get_start_iter()
        return self._text.get_buffer().get_text(s, e)

class version_control(service.service):

    display_name = 'Version Control Integration'

    class CommitMessage(defs.View):
        view_type = CommitView
        book_name = 'view'

    class meld_integration(defs.optiongroup):
        """How much meld will be used."""
        class use_meld_for_statuses(defs.option):
            """Whether Meld will be used for file listings."""
            rtype = types.boolean
            default = False
        class use_meld_for_diff(defs.option):
            """Whether Meld (visual diff) will be used for file diffs."""
            rtype = types.boolean
            default = False

    def init(self):
        self.__currentfile = None
        self.action_group.set_sensitive(False)
        self.__cached_vcs = {}
        self._commit_view = None

    def bnd_buffermanager_document_changed(self, document):
        self.__currentfile = document.filename
        self.action_group.set_sensitive(True)

    def cmd_get_vcs_for_directory(self, directory):
        vcs = vc.Vc(directory)
        workdir = vcs.get_working_directory(directory)
        if workdir in self.__cached_vcs:
            vcs = self.__cached_vcs[workdir]
        else:
            self.__cached_vcs[workdir] = vcs
        return vcs

    def cmd_forget_directory(self, directory):
        vcs = vc.Vc(directory)
        workdir = vcs.get_working_directory(directory)
        if workdir in self.__cached_vcs:
            del self.__cached_vcs[workdir]

    def cmd_statuses(self, directory):
        if self.opt('meld_integration', 'use_meld_for_statuses'):
            self.boss.call_command('meldembed', 'browse',
                                    directory=directory)
        else:
            print 'not using meld'

    def cmd_get_statuses(self, directory):
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            try:
                statuses = vcs.listdir(directory)
                return statuses
            except NotImplementedError:
                self.log.info('"%s" is not version controlled', directory)

    def cmd_diff_file(self, filename):
        if self.opt('meld_integration', 'use_meld_for_diff'):
            self.boss.call_command('meldembed', 'diff',
                                    filename=filename)
        else:
            directory = os.path.dirname(filename)
            basename = os.path.basename(filename)
            vcs = self.call('get_vcs_for_directory', directory=directory)
            if vcs.NAME == 'Null':
                self.log.info('"%s" is not version controlled', directory)
            else:
                try:
                    commandargs = vcs.diff_command() + [basename]
                    self.boss.call_command('terminal', 'execute',
                                        command_args=commandargs,
                                        icon_name='vcs_diff',
                                        term_type='dumb',
                                        kwdict = {'directory':
                                                   directory},
                                        short_title='Differences')
                except NotImplementedError:
                    self.log.info('Not implemented for %s' % vcs.NAME)

    def cmd_update(self, directory):
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            try:
                commandargs = vcs.update_command()
                self.boss.call_command('terminal', 'execute',
                                        command_args=commandargs,
                                        icon_name='vcs_update',
                                        kwdict = {'directory':
                                                   directory},
                                        short_title='Update')
                self._update_filemanager(directory)
            except NotImplementedError:
                self.log.info('"%s" is not version controlled', directory)
            return vcs

    def cmd_commit(self, directory):
        if os.path.isdir(directory):
            pathargs = []
        else:
            pathargs = [directory]
            directory = os.path.dirname(directory)
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            def commit(message):
                commandargs = vcs.commit_command(message) + pathargs
                self.boss.call_command('terminal', 'execute',
                                        command_args=commandargs,
                                        icon_name='vcs_commit',
                                        kwdict = {'directory':
                                                   directory},
                                        short_title='Commit')
                self._update_filemanager(directory)
            if self._commit_view is None:
                self._commit_view = self.create_view('CommitMessage')
                self._commit_view.show()
            else:
                self._commit_view.raise_page()
            self._commit_view.grab_focus()
            self._commit_view.set_callback(commit)
            self._commit_view.long_title = ('Commit message for %s on %s'
                                            % (vcs.NAME, directory))

    def cmd_add_file(self, filename):
        directory = os.path.dirname(filename)
        basename = os.path.basename(filename)
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            try:
                commandargs = vcs.add_command() + [basename]
                self.boss.call_command('terminal', 'execute',
                                    command_args=commandargs,
                                    icon_name='vcs_add',
                                    kwdict = {'directory':
                                               directory},
                                    short_title='Add')
                self._update_filemanager(directory)
            except NotImplementedError:
                self.log.info('Not implemented for %s' % vcs.NAME)

    def cmd_remove_file(self, filename):
        directory = os.path.dirname(filename)
        basename = os.path.basename(filename)
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            try:
                commandargs = vcs.remove_command() + [basename]
                self.boss.call_command('terminal', 'execute',
                                    command_args=commandargs,
                                    icon_name='vcs_add',
                                    kwdict = {'directory':
                                               directory},
                                    short_title='Remove')
                self._update_filemanager(directory)
            except NotImplementedError:
                self.log.info('Not implemented for %s' % vcs.NAME)

    def cmd_revert_file(self, filename):
        directory = os.path.dirname(filename)
        basename = os.path.basename(filename)
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            try:
                commandargs = vcs.revert_command() + [basename]
                self.boss.call_command('terminal', 'execute',
                                    command_args=commandargs,
                                    icon_name='undo',
                                    kwdict = {'directory':
                                               directory},
                                    short_title='Revert')
                self._update_filemanager(directory)
            except NotImplementedError:
                self.log.info('Not implemented for %s' % vcs.NAME)
        
    def _update_filemanager(self, directory):
        def browse():
            self.call('forget_directory', directory=directory)
            self.boss.call_command('filemanager', 'refresh',
                                    cwd=directory)
        gobject.timeout_add(200, browse)

    @actions.action(label='Differences',
                    stock_id='vcs_diff',
                    default_accel='<Shift><Control>d',
                    is_important=False)
    def act_diff_file(self, action):
        self.call('diff_file', filename=self.__currentfile)

    def view_closed(self, view):
        self._commit_view = None

    def get_menu_definition(self):
        return """
            <toolbar>
            </toolbar>
            <menubar>
            <menu name="base_file" action="base_file_menu">
            <placeholder name="SubSaveFileMenu" >
            <menuitem name="diff_file" action="versioncontrol+diff_file" />
            </placeholder>
            </menu>
            </menubar>
            """
        
        

Service = version_control
