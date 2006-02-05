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

# pida import(s)
import boss
import base

# system import(s)
import os
import sys
import subprocess
import warnings
import optparse

# gtk import(s)
import gtk
gtk.threads_init()


from pkg_resources import Requirement, resource_filename
version_file = resource_filename(Requirement.parse('pida'),
                                 'version/version')
try:
    pida_version = open(version_file).read().strip()
except:
    pida_version = 'testing'

def print_version_and_die():
    print 'PIDA, version %s' % pida_version
    sys.exit(0)

class environment(object):
    """Handle environment variable and command line arguments"""
    def __init__(self):
        self.__parseargs()

    def __parseargs(self):
        home_dir_option = None
        op = optparse.OptionParser()
        op.add_option('-d', '--home-directory', type='string', nargs=1,
                      action='store',
                      help='The location of the pida home directory',
                      default=os.path.expanduser('~/.pida'))
        op.add_option('-o', '--option', type='string', nargs=1,
                      action='append', help='Set an option')
        op.add_option('-v', '--version', action='store_true',
                      help='Print version information and exit.')
        op.add_option('-D', '--debug', action='store_true',
                      help='Run PIDA in debug mode')
        op.add_option('-r', '--remote', action='store_true',
                      help='Run PIDA remote')
        op.add_option('-p', '--profile', action='store_true',
                      help='Run PIDA in the python profiler')
        opts, args = op.parse_args()
        envhome = self.__parseenv()
        if envhome is not None:
            home_dir_option = envhome
        else:
            home_dir_option = opts.home_directory
        self.__home_dir = home_dir_option
        self.__create_home_tree(self.__home_dir)
        self.__args = args
        self.opts = opts

    def __parseenv(self):
        if 'PIDA_HOME' in os.environ:
            return os.environ['PIDA_HOME']

    def __create_home_tree(self, root):
        dirs = {}
        self.__mkdir(root)
        for name in ['conf', 'log', 'run', 'vcs', 'sockets', 'data',
                     'projects', 'library']:
            path = os.path.join(root, name)
            self.__mkdir(path)
            dirs[name] = path
        return dirs

    def __mkdir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def get_config_file(self):
        if self.__opts.registry_file:
            return self.__opts.registry_file

    def get_positional_args(self):
        return self.__args
    positional_args = property(get_positional_args)

    def get_home_dir(self):
        return self.__home_dir
    home_dir = property(get_home_dir)

    def get_version(self):
        return pida_version
    version = property(get_version)


class application(object):
    """The pIDA Application."""

    def __init__(self, bosstype, mainloop, mainstop, environment):
        self.__mainloop = mainloop
        self.__mainstop = mainstop
        self.__env = environment
        self.__boss = bosstype(application=self, env=self.__env)
        self.boss = self.__boss

    def start(self):
        """Start PIDA."""
        self.__boss.start()
        self.__mainloop()

    def stop(self):
        """Stop PIDA."""
        self.__mainstop()

def pida_excepthook(exctype, value, tb):
    if exctype is not KeyboardInterrupt:
        import pida.pidagtk.debugwindow as debugwindow
        dw = debugwindow.DebugWindow()
        dw.show_exception(exctype, value, tb)
        dw.run()
        dw.destroy()

sys.excepthook = pida_excepthook

def run_pida(bosstype, mainloop, mainstop, env):
    app = application(bosstype, mainloop, mainstop, env)
    app.start()
    return app

def run_remote(env):
    import pida.utils.pidaremote as pidaremote
    pidaremote.main(env.home_dir, env.positional_args)

def main(bosstype=boss.boss, mainloop=gtk.main, mainstop=gtk.main_quit):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    env = environment()
    if env.opts.version is not None:
        print_version_and_die()
    if env.opts.debug:
        os.environ['PIDA_DEBUG'] = '1'
        os.environ['PIDA_LOG_STDERR'] = '1'
    if env.opts.remote:
        run_remote(env)
        return
    if env.opts.profile:
        import profile
        def _a():
            run_pida(bosstype, mainloop, mainstop, env)
        profile.runctx('_a()', locals(), globals())
        return
    run_pida(bosstype, mainloop, mainstop, env)
    


if __name__ == '__main__':
    main()
