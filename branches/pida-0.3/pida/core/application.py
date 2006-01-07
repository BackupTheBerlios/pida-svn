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
import warnings
import optparse

# gtk import(s)
import gtk


from pkg_resources import Requirement, resource_filename
version_file = resource_filename(Requirement.parse('pida'),
                                 'revision/svn_revision')
pida_revision = open(version_file).read().strip()
pida_version = '0.3.pre r%s' % pida_revision

def print_version_and_die():
    print 'pIDA version %s' % pida_version
    sys.exit(0)

class environment(base.pidacomponent):
    """Handle environment variable and command line arguments"""
    def init(self):
        self.__parseargs()

    def __parseargs(self):
        home_dir_option = None
        op = optparse.OptionParser()
        op.add_option('-d', '--home-directory', type='string', nargs=1,
                      action='store',
                      help='The location of the pida home directory',
                      default=os.path.expanduser('~/.pida2'))
        op.add_option('-o', '--option', type='string', nargs=1,
                      action='append', help='Set an option')
        op.add_option('-v', '--version', action='store_true',
                      help='Print version information and exit.')
        opts, args = op.parse_args()
        if opts.version is not None:
            print_version_and_die()
        envhome = self.__parseenv()
        if envhome is not None:
            home_dir_option = envhome
        else:
            home_dir_option = opts.home_directory
        self.__home_dir = home_dir_option
        self.__create_home_tree(self.__home_dir)
        self.__args = args

    def __parseenv(self):
        if 'PIDA_HOME' in os.environ:
            return os.environ['PIDA_HOME']

    def __create_home_tree(self, root):
        dirs = {}
        self.__mkdir(root)
        for name in ['conf', 'log', 'run', 'vcs', 'sockets', 'data', 'projects']:
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

    def __init__(self):
        self.__env = environment()
        self.__boss = boss.boss(application=self, env=self.__env)

    def start(self):
        """Start PIDA."""
        self.__boss.start()
        gtk.main()

    def stop(self):
        """Stop PIDA."""
        gtk.main_quit()


def main():
    gtk.threads_init()
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    app = application()
    app.start()


if __name__ == '__main__':
    main()
