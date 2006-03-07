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

# system import(s)
import os
import sys
import optparse
import warnings


def die(message):
    """Die in a command line way."""
    print message
    print 'Exiting. (this is fatal)'
    sys.exit(1)


# First gtk import, let's check it
try:
    import gtk
    major, minor, rev = gtk.pygtk_version
    if major < 2 or minor < 6:
        die('PIDA requires PyGTK >= 2.6. It only found %s.%s'
            % (major, minor))
except ImportError:
    die('PIDA requires Python GTK bindings. They were not found.')

# the threads evilness
gtk.threads_init()


def die_gui(message):
    """Die in a GUI way."""
    mu = ('<b>There was an error starting PIDA</b>\n\n'
          '%s\n\n<i>This is fatal</i>' % message)
    dlg = gtk.MessageDialog(parent=None,
                            flags=0,
                            type=gtk.MESSAGE_ERROR,
                            buttons=gtk.BUTTONS_CLOSE)
    dlg.set_markup(mu)
    dlg.run()
    die(message)


# Python 2.4
major, minor = sys.version_info[:2]
if major < 2 or minor < 4:
    die_gui('Python 2.4 is required to run PIDA. Only %s.%s was found' %
            (major, minor))


# Setuptools is needed to run PIDA
try:
    import setuptools
    import pkg_resources
    pkg_resources.require('pida')
except ImportError:
    raise
    die_gui('PIDA requires setuptools to be installed.')


# This can test if PIDA is installed
try:
    import pida.core.boss as boss
    import pida.pidagtk.debugwindow as debugwindow
except ImportError:
    die_gui('PIDA could not import itself.')


# Now we can use a gui exception hook
old_excepthook = sys.excepthook
sys.excepthook = debugwindow.show


def get_version():
    from pkg_resources import resource_string
    try:
        version_file = resource_string('pida', 'data/version')
    except:
        version_file = 'unversioned'
    return version_file


pida_version = get_version()


class environment(object):
    """Handle environment variable and command line arguments"""
    def __init__(self):
        self.__editorname = None
        self.__parseargs()

    def __parseargs(self):
        home_dir_option = None
        default_home = os.path.join(os.path.expanduser('~'), '.pida')

        if default_home == os.path.join('~', '.pida'):
            # When on win32
            from win32com.shell import shell, shellcon
            default_home = shell.SHGetSpecialFolderLocation(
                0,
                shellcon.CSIDL_APPDATA
            )
            default_home = shell.SHGetPathFromIDList(default_home)
            default_home = os.path.join(default_home, "Pida")
            del shell
            del shellcon
            
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
        op.add_option('-t', '--testing-mode', action='store_true',
                      help='Run te PIDA self test')
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
                        try:
                            svc = services.get(service)
                            svc.options.get(group).get(option).load(value)
                        except:
                            pass

    def override_editor_option(self, editorname):
        self.__editorname = editorname


class application(object):
    """The pIDA Application."""

    def __init__(self,
                 bosstype=boss.boss,
                 mainloop=gtk.main,
                 mainstop=gtk.main_quit,
                 environment=environment()):
        self.__mainloop = mainloop
        self.__mainstop = mainstop
        self.__env = environment
        self.__boss = bosstype(application=self, env=self.__env)
        self.boss = self.__boss
        self.env = self.__env

    def start(self):
        """Start PIDA."""
        self.__boss.start()
        gtk.threads_enter()
        self.__mainloop()
        gtk.threads_leave()

    def stop(self):
        """Stop PIDA."""
        self.__mainstop()


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


def main(bosstype=boss.boss, mainloop=gtk.main, mainstop=gtk.main_quit):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    env = environment()
    if env.opts.debug:
        os.environ['PIDA_DEBUG'] = '1'
        os.environ['PIDA_LOG_STDERR'] = '1'
    if env.opts.testing_mode:
        sys.excepthook = old_excepthook
    if env.opts.version is not None:
        run_func = run_version
    elif env.opts.remote:
        run_func = run_remote
    else:
        run_func = run_pida

    sys.exit(run_func(env, bosstype, mainloop, mainstop))


if __name__ == '__main__':
    main()
