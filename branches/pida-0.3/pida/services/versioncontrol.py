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

import os

import pida.core.service as service

import pida.utils.vc as vc

defs = service.definitions
types = service.types

class version_control(service.service):

    class meld_integration(defs.optiongroup):
        """How much meld will be used."""
        class use_meld_for_statuses(defs.option):
            rtype = types.boolean
            default = True
        class use_meld_for_diff(defs.option):
            rtype = types.boolean
            default = True

    def init(self):
        self.__currentfile = None
        self.action_group.set_sensitive(False)
        self.__cached_vcs = {}

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
            vcs = self.call('get_vcs_for_directory', directory=directory)
            if vcs.NAME == 'Null':
                self.log.info('"%s" is not version controlled', directory)
            else:
                try:
                    commandargs = vcs.diff_command() + [filename]
                    self.boss.call_command('terminal', 'execute',
                                        command_args=commandargs,
                                        icon_name='vcs_diff',
                                        kwdict = {'directory':
                                                   directory})
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
                                                   directory})
            except NotImplementedError:
                self.log.info('"%s" is not version controlled', directory)
            return vcs

    def cmd_commit(self, directory):
        vcs = self.call('get_vcs_for_directory', directory=directory)
        if vcs.NAME == 'Null':
            self.log.info('"%s" is not version controlled', directory)
        else:
            def commit(message):
                commandargs = vcs.commit_command(message)
                self.boss.call_command('terminal', 'execute',
                                        command_args=commandargs,
                                        icon_name='vcs_commit',
                                        kwdict = {'directory':
                                                   directory})
            self.boss.call_command('tempfilecreator', 'get_input',
                                   callback_function=commit,
                                   title=vcs.NAME, prefix='commit')
            #try:
            #    commandargs = vcs.update_command()
            #    self.boss.call_command('terminal', 'execute',
            #                            command_args=commandargs,
            #                            icon_name='vcs_update',
            #                            kwdict = {'directory':
            #                                       directory})
            #except NotImplementedError:
            #    self.log.info('"%s" is not version controlled', directory)

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
                                               directory})
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
                                               directory})
            except NotImplementedError:
                self.log.info('Not implemented for %s' % vcs.NAME)


    def act_diff_file(self, action):
        self.call('diff_file', filename=self.__currentfile)

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_file" action="base_file_menu">
            <separator />
            <placeholder name="OpenFileMenu" />
            <placeholder name="SaveFileMenu" />
            <placeholder name="ExtrasFileMenu">
            <separator />
            <menuitem name="diff_file" action="versioncontrol+diff_file" />
            <separator />
            </placeholder>
            <placeholder name="GlobalFileMenu" />
            <separator />
            </menu>
            </menubar>
            """
        
        

Service = version_control
