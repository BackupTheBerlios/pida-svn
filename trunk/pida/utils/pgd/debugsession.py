# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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
import sys

from winpdb import rpdb2
from console import Terminal


def get_debugee_script_path():
    import pkg_resources
    req = pkg_resources.Requirement.parse('pgd')
    try:
        sfile = pkg_resources.resource_filename(req, 'pgd/winpdb/rpdb2.py')
    except pkg_resources.DistributionNotFound:
        sfile = os.path.join(
            os.path.dirname(__file__),
            'winpdb',
            'rpdb2.py')
        if sfile.endswith('c'):
            sfile = sfile[:-1]
    return sfile


class SessionManagerInternal(rpdb2.CSessionManagerInternal):
    
    def _spawn_server(self, fchdir, ExpandedFilename, args, rid):
        """
        Start an OS console to act as server.
        What it does is to start rpdb again in a new console in server only mode.
        """
        debugger = get_debugee_script_path()
        baseargs = ['python', debugger, '--debugee', '--rid=%s' % rid]
        if fchdir:
            baseargs.append('--chdir')
        if self.m_fAllowUnencrypted:
            baseargs.append('--plaintext')
        if self.m_fRemote:
            baseargs.append('--remote')
        if os.name == 'nt':
            baseargs.append('--pwd=%s' % self.m_pwd)
        if 'PGD_DEBUG' in os.environ:
            baseargs.append('--debug')
        baseargs.append(ExpandedFilename)
        cmdargs = baseargs + args.split()
        python_exec = sys.executable
        self.terminal.fork_command(python_exec, cmdargs)
        

class SessionManager(rpdb2.CSessionManager):
    
    def __init__(self, app):
        self.app = app
        self.options = app.options
        self.main_window = app.main_window
        self.delegate = self._create_view()
        self._CSessionManager__smi = self._create_smi()

    def _create_smi(self):
        smi = SessionManagerInternal(
                                  self.options.pwd,
                                  self.options.allow_unencrypted,
                                  self.options.remote,
                                  self.options.host)
        smi.terminal = self
        return smi

    def _create_view(self):
        view = Terminal(self.app)
        self.main_window.attach_slave('outterm_holder', view)
        return view

    def fork_command(self, *args, **kw):
        self.delegate.terminal.fork_command(*args, **kw)

    def launch_filename(self, filename):
        self.app.launch(filename)
        
class RunningOptions(object):

    def set_options(self, command_line,
                  fAttach,
                  fchdir,
                  pwd,
                  fAllowUnencrypted,
                  fRemote,
                  host):
        self.command_line = command_line
        self.attach = fAttach
        self.pwd = pwd
        self.allow_unencrypted = fAllowUnencrypted
        self.remote = fRemote
        self.host = host


def connect_events(self):
    event_type_dict = {rpdb2.CEventState: {}}
    self.session_manager.register_callback(self.update_state, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventStackFrameChange: {}}
    self.session_manager.register_callback(self.update_frame, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventThreads: {}}
    self.session_manager.register_callback(self.update_threads, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventNoThreads: {}}
    self.session_manager.register_callback(self.update_no_threads, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventNamespace: {}}
    self.session_manager.register_callback(self.update_namespace, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventThreadBroken: {}}
    self.session_manager.register_callback(self.update_thread_broken, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventStack: {}}
    self.session_manager.register_callback(self.update_stack, event_type_dict, fSingleUse = False)
    event_type_dict = {rpdb2.CEventBreakpoint: {}}
    self.session_manager.register_callback(self.update_bp, event_type_dict, fSingleUse = False)


def start(command_line, fAttach, fchdir, pwd, fAllowUnencrypted, fRemote, host):
    options= RunningOptions()
    options.set_options(command_line, fAttach, fchdir, pwd, fAllowUnencrypted, fRemote, host)
    return options

def main(start):
    rpdb2.main(start)

def start_as_cl():
    rpdb2.main()

if __name__ == '__main__':
    start_as_cl()
