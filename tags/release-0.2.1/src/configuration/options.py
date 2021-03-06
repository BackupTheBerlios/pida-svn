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

''' Default configuration options '''

# System imports
import os
import sys
import ConfigParser as configparser

# The pida registry
import registry

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

def configure(reg):
    """
    Default global configuration.
    """
    dirs_group = reg.add_group('directories',
                                  'Locations of directories pida will use.')
    # user directory
    dirs_user = dirs_group.add('user',
                 registry.CreatingDirectory,
                 os.path.expanduser('~/.pida'),
                 'The base per-user directory')
    # libraries
    # This takes a bit of work
    prefix = __file__.split('lib', 1)[0]
    dirs_libs = dirs_group.add('shared',
                 registry.Directory,
                 os.path.join(prefix, 'share', 'pida'),
                 'The shared library directory.')

    dirs_sock = dirs_group.add('socket',
                 registry.CreatingDirectory,
                 os.path.join(dirs_user._default, '.sockets'),
                 'Where Pida will start Unix Domain Sockets')
                 
 #       ### Files
    file_group = reg.add_group('files',
        'Location of files Pida will use.')

    file_icon = file_group.add('icon_data',
                registry.MustExistFile,
                os.path.join(dirs_libs._default, 'icons.dat'),
                'Location of the icons file')
    
    file_proj = file_group.add('project_data',
                registry.File,
                os.path.join(dirs_user._default, 'pida.projects'),
                'Location of the project data file.')

    file_shrt = file_group.add('shortcut_data',
                registry.File,
                os.path.join(dirs_user._default, 'pida.shortcuts'),
                'Location of the shortcuts data file.')


 #       ### External command options
    coms_group = reg.add_group('commands',
        'Paths to external commands used by Pida')
                  

    coms_gvim = coms_group.add('vim',
                registry.WhichFile,
                'gvim',
                'Path to Gvim (may be set as /path/to/vim -g).')

    coms_cvim = coms_group.add('console_vim',
                registry.WhichFile,
                'vim',
                'Path to console Vim')

    coms_evim = coms_group.add('evim',
                registry.WhichFile,
                'evim',
                'Path to the modeless (easy) Vim version.')

    coms_pyth = coms_group.add('python',
                registry.WhichFile,
                'python',
                'Path to the Python interpreter.')

    coms_shel = coms_group.add('shell',
                registry.WhichFile,
                os.getenv('SHELL'),
                'The path to your preferred shell.')
 
    coms_brow = coms_group.add('browser',
                registry.WhichFile,
                'firefox',
                'The path to your preferred browser.')

    coms_page = coms_group.add('pager',
                registry.WhichFile,
                'less',
                'The path to the paging program (eg less).')

    coms_seem = coms_group.add('see',
                registry.WhichFile,
                'see',
                'The path to the "see" general previewer.')
    
    coms_mcom = coms_group.add('mc',
                registry.WhichFile,
                'mc',
                'The path to the midnight commander or any file manager.')

    coms_pdoc = coms_group.add('pydoc',
                registry.WhichFile,
                'pydoc',
                'The path to the pydoc program.')

    logs_group = reg.add_group('log',
                               'Logging options.')

    log_level = logs_group.add('level',
                   registry.Integer,
                   20,
                   'The default logging level (10=debug, 50=critical)')

    log_level.adjustment = (10, 50, 10)

    lay_group = reg.add_group('layout', 'Thigs to do with layout')
    
    lay_vert = lay_group.add('vertical_split',
               registry.Boolean,
               0,
               'Whether to split the view vertically (requires restart).')
    
   
if __name__ == '__main__':
    pass
