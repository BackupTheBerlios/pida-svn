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

class environment(object):
    """Handle environment variable and command line arguments"""
    def __init__(self):
        self.__editorname = None
        self.__parseargs()

    def __parseargs(self):
        home_dir_option = None
        default_home = os.path.expanduser('~/.pida')
        op = optparse.OptionParser()
        op.add_option('-d', '--home-directory', type='string', nargs=1,
            action='store',
            help=('The location of the pida home directory. '
                  'If this directory does not exist, it will be created. '
                  'Default: %s' % default_home),
            default=default_home)
        op.add_option('-o', '--option', type='string', nargs=1,
            action='append',
            help=('Set an option. Options should be in the form: '
                  'servicename/group/name=value. '
                  'For example (without quotes): '
                  '"pida -o editormanager/general/editor_type=Vim". '
                  'More than one option can be set by repeated use of -o.'))
        op.add_option('-v', '--version', action='store_true',
                      help='Print version information and exit.')
        op.add_option('-D', '--debug', action='store_true',
            help=('Run PIDA with added debug information. '
                  'This merely sets the environment variables: '
                  'PIDA_DEBUG=1 and PIDA_LOG_STDERR=1, '
                  'and so the same effect may be achieved by setting them.'))
        op.add_option('-r', '--remote', action='store_true',
            help=('Run PIDA remotely to open a file in an existing instance '
                  'of PIDA. Usage pida -r <filename>.'))
        op.add_option('-F', '--first-run-wizard', action='store_true',
                      help='Run the PIDA first time wizard')
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

    def get_positional_args(self):
        return self.__args
    positional_args = property(get_positional_args)

    def get_home_dir(self):
        return self.__home_dir
    home_dir = property(get_home_dir)

    def get_version(self):
        return pida_version
    version = property(get_version)

    def override_configuration_system(self, services):
        if self.__editorname:
            svc = services.get('editormanager')
            svc.set_option('general', 'editor_type', self.__editorname)
            svc.options.save()
        if not self.opts.option:
            return
        for opt in self.opts.option:
            if '=' in opt:
                name, value = opt.split('=', 1)
                if '/' in name:
                    parts = name.split('/', 3)
                    if len(parts) == 3:
                        service, group, option = parts
                        svc = services.get(service)
                        svc.set_option(group, option, value)
                    else:
                        raise KeyError('service/group/option ' + opt)
                else:
                    raise KeyError('service/group/option ' + opt )
            else:
                raise ValueError('Need key=value ' + opt)

    def override_editor_option(self, editorname):
        self.__editorname = editorname

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

def run_pida(env, bosstype, mainloop, mainstop):
    if run_firstrun(env):
        app = application(bosstype, mainloop, mainstop, env)
        app.start()
        return 0
    else:
        return 1

def run_version(env, *args):
    print 'PIDA, version %s' % pida_version
    return 0

def run_remote(env, *args):
    import pida.utils.pidaremote as pidaremote
    pidaremote.main(env.home_dir, env.positional_args)
    return 0

def run_firstrun(env, *args):
    first_filaname = os.path.join(env.home_dir, '.firstrun')
    if not os.path.exists(first_filaname) or env.opts.first_run_wizard:
        import pida.utils.firstrun as firstrun
        ftw = firstrun.FirstTimeWindow()
        response, editor = ftw.run(first_filaname)
        if response == gtk.RESPONSE_ACCEPT:
            if editor is None:
                raise RuntimeError('No Working Editors')
            else:
                env.override_editor_option(editor)
                return True
        else:
            return False
    else:
        return True

def run_profile(env, *args):
    import profile
    def _a():
        run_pida(bosstype, mainloop, mainstop, env)
    profile.runctx('_a()', locals(), globals())
    return 0

def main(bosstype=boss.boss, mainloop=gtk.main, mainstop=gtk.main_quit):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    env = environment()
    if env.opts.debug:
        os.environ['PIDA_DEBUG'] = '1'
        os.environ['PIDA_LOG_STDERR'] = '1'
    if env.opts.version is not None:
        run_func = run_version
    elif env.opts.remote:
        run_func = run_remote
    else:
        run_func = run_pida
    sys.exit(run_func(env, bosstype, mainloop, mainstop))
    


if __name__ == '__main__':
    main()
