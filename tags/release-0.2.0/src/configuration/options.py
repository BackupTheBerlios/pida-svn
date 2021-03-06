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

''' Default configuration options '''

# System imports
import os
import sys
import shutil
import textwrap
import ConfigParser as configparser

# import the base and set the version
import pida.__init__ as __init__
__version__ = __init__.__version__


class Config(configparser.ConfigParser):
    intro = ('#This is an automatically generated Pida config file.\n'
             '#Please edit it, your changes will be preserved.\n'
             '#If you want a fresh config file, delete it, or change the\n'
             '#version string above.\n\n'
             '#Notes:\n'
             '#Boolean values are 1 or 0\n'
             '#Blank lines are ignored as are lines beginning # (comments).\n\n')
    
    def write(self, fp, helpdict):
        '''Write an .ini-format representation of the configuration state.
       
           Modified only slightly from the original source.'''
        fp.write('#%s\n' % __version__)
        fp.write(self.intro)
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    try:
                        help = helpdict[(section, key)]
                    except KeyError:
                        help = None
                    if help:
                        helptext = '\n'.join(['#%s' % s for s in textwrap.wrap(help)])
                        fp.write('%s\n' % helptext)
                        fp.write("%s = %s\n\n" %
                             (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

class Opts(object):
    ''' Class storing options '''

    def __init__(self):
        self.opts = Config()
        self.help = {}
        self.types = {}
        self.dirty_version = False

        ### Directories
        self.add_section('directories')

        # base, per user
        basedir = os.path.expanduser('~/.pida')
        self.create_dir(basedir)
        self.add('directories', 'user', basedir,
                 'The base per-user directory', 'dir')
        
        # libraries
        libdir = os.path.join(sys.prefix, 'share', 'pida')
        self.add('directories', 'shared', libdir,
                 'The shared library directory.', 'dir')

        ### Files
        self.add_section('files')

        # config file
        conffile = os.path.join(basedir,'pida.conf')
        self.add('files', 'config_user', conffile,
                 'The user configuration file. '
                 'A default file will be created at '
                 'this location if no file exists', 'file')

        # vim-side script
        vimscript = os.path.join(basedir, 'pida.vim')
        self.add('files', 'script_vim', vimscript,
                 'Vim-side script location. '
                 'A default file will be created at '
                 'this location if no file exists', 'file')

        # icon data file
        iconsfn = os.path.join(libdir, 'icons.dat')
        self.add('files', 'data_icons', iconsfn,
                 'Location of the icons file.', 'file')

        # project data file
        projectsfn = os.path.join(basedir, 'pida.projects')
        self.add('files', 'data_project', projectsfn,
                 'Location of the project data file.', 'file')

        # project data file
        shortsfn = os.path.join(basedir, 'pida.shortcuts')
        self.add('files', 'data_shorcuts', shortsfn,
                 'Location of the shortcuts data file.', 'file')

        ### Terminal emulator options
        self.add_section('terminal')
        self.add('terminal', 'font_default', 'Monospace 10',
                 'The font for newly started terminals.', 'font')
        self.add('terminal', 'font_log', 'Monospace 8',
                 'The font for the logging terminal', 'font')
        self.add('terminal', 'transparency_enable', '0',
                 'Determines whether terminals will exhibit '
                 'pseudo-transparency.', 'boolean')
        self.add('terminal', 'colour_background', '#000000',
                 'A string representing the background colour', 'color')
        self.add('terminal', 'colour_foreground', '#c0c0c0',
                 'A string representing the foreground colour', 'color')
        ### External command options
        self.add_section('commands')
 
        vimcom = which('gvim') or '/usr/bin/gvim'
        self.add('commands', 'vim', vimcom,
                  'Command for executing graphical Vim.', 'file')
        evimcom = which('evim') or '/usr/bin/evim'
        self.add('commands', 'evim', evimcom,
                  'Command for executing the modeless Vim. '
                  '(Like a standard point-click editor', 'file')

        pycom = which('python') or '/usr/bin/python' 
        self.add('commands', 'python', pycom,
                 'The absolute path to Python on your system', 'file')
        bashcom = os.getenv('SHELL') or which('bash') or '/bin/bash'
        self.add('commands', 'shell', bashcom,
                 'The absolute path to your preferred shell.', 'file')
        browcom = which('firefox') or '/usr/bin/firefox'
        self.add('commands', 'browser', browcom,
                 'The absolute path to your preferred browser.', 'file')
        pagercom = which('less') or '/bin/more'
        self.add('commands', 'pager', pagercom,
                 'The absolute path to a paging program (eg less).', 'file')
        seecom = which('see') or '/usr/bin/see'
        self.add('commands', 'see', seecom,
                 'The absolute path to the "see" program.', 'file')
        mccom = which('mc') or '/usr/bin/mc'
        self.add('commands', 'mc', mccom,
                 'The absolute path to a file manager Application', 'file')
        pydoccom = which('pydoc') or '/usr/bin/pydoc'
        self.add('commands', 'pydoc', pydoccom,
                 'The absolute path to the pydoc Application', 'file')

        ### Logging options
        self.add_section('log')
        self.add('log', 'level', '1',
                 'The default logging level. Messages equal or above '
                 'this level will be logged 0=Debug.')
        ###vim options 
        self.add_section('vim')
        self.add('vim', 'foreground_jump', '1',
                 'Determines whether Pida will foreground Vim when the buffer'
                 'is changed, or the cursor is moved', 'boolean')
        self.add('vim', 'connect_startup', '1',
                 'Determines whether Pida will attempt to connect to Vim '
                 'on startup', 'boolean')
        self.add('vim', 'mode_easy', '0',
                 'Determines whether Pida will run Vim as Evim (easy mode). '
                 'Some people may prefer this mode of operation. '
                 'This is how the Windows-style text editors behave, and '
                 '<b>perfect if you hate Vim</b>', 'boolean')
        self.add('vim', 'mode_embedded', '0',
                 'Embed Vim in Pida when running, like a standard IDE. '
                 '<b>Needs restart</b>',
                 'boolean')

        ### plugin options
        self.add_section('plugins')
        self.add('plugins', 'python_browser', '1',
                 'Enable the Python code browser and refactorer.', 'boolean')
        self.add('plugins', 'python_debugger', '1',
                 'Enable the Python debugger <i>disabled</i>', 'boolean')
        self.add('plugins', 'project', '1',
                 'The project manager <i>experimental</i>', 'boolean')
        self.add('plugins', 'python_profiler', '1',
                 'The python profiler <i>experimental</i>', 'boolean')

        ### Python plugin
        self.add_section('python browser')
        self.add('python browser', 'colors_use', '1',
                 'Determines whther colours will be used for the Python '
                 'elements listing', 'boolean')

        self.add_section('project browser')
        self.add('project browser', 'color_directory', '#0000c0',
                 'Colour used for directories in file list', 'color')

        # Vim shortcuts
        self.add_section('vim shortcuts')
        self.add('vim shortcuts', 'shortcut_leader', ',',
                 'The value of the leader keypress. Pressed before the '
                 'actual keypress. :he &lt;Leader&gt;. Normal mode only.')
        self.add('vim shortcuts', 'shortcut_execute', 'x',
                 'The key press to execute the current buffer in PIDA')
        self.add('vim shortcuts', 'shortcut_debug', 'd',
                 'The key press to debug the current buffer in PIDA')
        self.add('vim shortcuts', 'shortcut_project_execute', 'p',
                 'The key press to execute the current project in PIDA')
        self.add('vim shortcuts', 'shortcut_breakpoint_set', 'b',
                 'The key press to set a breakpoint at the current line')
        self.add('vim shortcuts', 'shortcut_breakpoint_clear', 'B',
                 'The key press to clear a breakpoint at the current line')
        self.add('vim shortcuts', 'shortcut_pydoc_yanked', '/',
                 'The keypress to Pydoc the most recently yankend text.')
        self.add('vim shortcuts', 'shortcut_pydoc_cursor', '?',
                 'The keypress to Pydoc the word under the cursor.')

        if os.path.exists(conffile):
            self.load_defaults()
        self.write()

    def add_section(self, section):
        ''' Add a configuration section. '''
        self.opts.add_section(section)

    def add(self, section, key, value, help, otype=None):
        ''' Add a configuration value for a key and section. '''
        self.set(section, key, value)
        self.help[(section, key)] = help
        self.types[(section, key)] = otype

    def set(self, section, key, value):
        ''' Set the value of a key in a section. '''
        self.opts.set(section, key, value)

    def sections(self):
        ''' Return the sections. '''
        return self.opts.sections()

    def options(self, section):
        ''' Return the options for a section. '''
        return self.opts.options(section)

    def write(self):
        ''' Write the options file to the configured location. '''
        f = open(self.opts.get('files', 'config_user'), 'w')
        self.opts.write(f, self.help)
        f.close()

    def load_defaults(self):
        ''' Load the option file from the configured location. '''
        tempopts = Config()
        f = open(self.opts.get('files', 'config_user'), 'r')
        tempopts.readfp(f)
        f.close()
        for section in tempopts.sections():
            for option in tempopts.options(section):
                if self.opts.has_option(section, option):
                    self.set(section, option, tempopts.get(section, option))

    def create_dir(self, dirname):
        ''' Create a directory if it does not already exist. '''
        if not os.path.exists(dirname):
            os.mkdir(dirname) 

    def get(self, section, key):
        ''' Get the value of a key in a section. '''
        return self.opts.get(section, key)

def which(name):
    ''' Returns the path of the application named name using 'which'. '''
    p = os.popen('which %s' % name)
    w = p.read().strip()
    p.close()
    if len(w):
        if 'command not found' in w:
            return None
        else:
            return w
    else:
        return None

