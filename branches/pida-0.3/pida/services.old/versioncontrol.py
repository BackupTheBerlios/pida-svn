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
import pida.core.registry as registry

VCS_NONE = 0
VCS_DARCS = 1
VCS_CVS = 2
VCS_SVN = 3
VCS_MERC = 4

VCS_NAMES = {0: '', 1: 'darcs', 2: 'CVS', 3: 'Subversion', 4: 'Mercurial'}

class VersionControl(service.ServiceWithSingleView):
    
    NAME = 'versioncontrol'
    COMMANDS = [('call', [('command', True),
                          ('directory', True)]),
                ('get-statuses', [('directory', True),
                                  ('datacallback', True)]),
                ('get-vcs-for-directory', [('directory', True)]),
                ('up', [('directory', True)]),
                ('commit-directory', [('directory', True), ('message', False)]),
                ('commit-files', [('files', True)]),
                ('commit-current-file', []),
                ('diff-file', [('filename', True)]),
                ('diff-current-file', []),
                ('status', [('directory', True)]),
                ]

    OPTIONS = [('use-meld-for-diff',
                'Whether to display diff with meld, if available',
                True, registry.Boolean),
                ('use-meld-for-statuses',
                'Whether to display direcory statuses with meld if available',
                True, registry.Boolean)]
    
    def init(self):
        self.__vcs = create_vcs_maps()

    def call_visual(self, basecmd, command, directory, files=[]):
        iconname = 'vcs_%s' % command
        self.boss.command('terminal', 'execute', viewbook=False,
                           cmdargs=[basecmd] + list(command) + files,
                           spkwargs={'cwd': directory}, icon=iconname)

    def call_hidden(self, basecmd, command, directory, datacallback, files=[],
                    msg=[]):
        self.boss.command('terminal', 'execute-hidden',
                           cmdargs=[basecmd] + list(command) + msg + files,
                           kwargs={'cwd': directory},
                           datacallback=datacallback)
        
    def cmd_call(self, command, directory):
        self.call(command, directory, True)

    def call(self, command, directory, files=[], msg=[], visual=True,
             cbfunc=lambda *a: None):
        vcstype = get_vcs_for_directory(directory)
        if vcstype != VCS_NONE:
            vcs = self.__vcs[vcstype]
            if command in vcs.commands:
                action = vcs.commands[command]
                basecmd = vcs.base_command
                if visual:
                    self.call_visual(basecmd, action, directory, files)
                else:
                    self.call_hidden(basecmd, action, directory, cbfunc, files)
            else:
                self.log_warn('Bad command: %s' % command)
        else:
            self.log_warn('Not a version controlled directory %s.' % directory)

    def cmd_get_statuses(self, directory, datacallback):
        def cb(status_data):
            L = (line.split() for line in status_data.splitlines())
            D = {}
            try:
                for st, fn in L:
                    D[fn] = st
                datacallback(D)
            except:
                datacallback({})
        self.call('status', directory, False, cb)

    def cmd_get_vcs_for_directory(self, directory):
        vcs = get_vcs_for_directory(directory)
        return vcs, VCS_NAMES[vcs]

    def cmd_up(self, directory):
        self.call('update', directory)
        
    def cmd_message_and_commit(self, directory):
        pass

    def cmd_commit_directory(self, directory, message=None):
        if message is not None:
            self.call('commit', directory, msg=['-m', message])
        else:
            self.call('commit', directory)

    def cmd_commit_files(self, files):
        #self.call('up', directory)
        print files
        self.call('commit', os.path.dirname(files[0]), files)

    def cmd_commit_current_file(self):
        buf = self.boss.command('buffermanager', 'get-currentbuffer')
        self.cmd_commit_files([buf.filename])

    def cmd_status(self, directory):
        vcs = self.cmd_get_vcs_for_directory(directory)[0]
        if (vcs in [VCS_SVN, VCS_CVS, VCS_DARCS] and
                self.options.get('use-meld-for-statuses').value()):
            self.boss.command('meld', 'browse', directory=directory)
        else:
            self.call('status', directory)

    def cmd_diff_file(self, filename):
        directory = os.path.dirname(filename)
        vcs = self.cmd_get_vcs_for_directory(directory)[0]
        if (vcs in [VCS_SVN, VCS_CVS] and
                self.options.get('use-meld-for-diff').value()):
            self.boss.command('meld', 'diff-file', filename=filename)
        else:
            self.call('diff', directory=directory, files=[filename])

    def cmd_diff_current_file(self):
        buf = self.boss.command('buffermanager', 'get-currentbuffer')
        self.cmd_diff_file(buf.filename)

Service = VersionControl


def vcs_commands(**kw):
    return kw

class IVCSType(object):
    base_command = None
    default_args = []
    commands = vcs_commands(commit=("commit", ),
                            update=("update", ),
                            status=('status', ))
    extra_commands = vcs_commands()

class Darcs(IVCSType):
    base_command = 'darcs'
    commands = vcs_commands(commit=("record", ),
                            update=("pull", ),
                            status=('whatsnew', '--summary'))

class Subversion(IVCSType):
    base_command = 'svn'
    commands = vcs_commands(commit=("commit", ),
                            update=("update", ),
                            status=('status', ),
                            rstatus=('status', ),
                            up=('up', ),
                            diff=('diff', ))

class CVS(IVCSType):
    commands = vcs_commands(commit=("commit", ),
                            update=("update", ),
                            status=('status', ),
                            rstatus=('status', ),
                            up=('up', ))

class Mercurial(IVCSType):
    pass


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
            elif i == '.hg':
                vcs = VCS_MERC
    return vcs

def create_vcs_maps():
    return {VCS_DARCS: Darcs(),
            VCS_SVN: Subversion(),
            VCS_CVS: CVS(),
            VCS_MERC: Mercurial()}

