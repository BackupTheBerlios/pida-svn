# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: setup.py 526 2005-08-16 18:09:12Z aafshar $
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


from distutils.core import setup
from setuptools import setup

import os
import sys
import shutil

VERBOSE = True

def log(message):
    if VERBOSE:
        print 'Pida:', message

log('Preparing core')
packages = ['pida',
            'pida.core',
            'pida.pidagtk',
            'pida.services',
            'pida.editors',
            'pida.plugins',
            'pida.utils',
            'pida.utils.vim',
            'pida.utils.vc']

#log('Preparing editors')
#plugindir = os.path.join('pida', 'editors')
#for plugin in os.listdir(plugindir):
#    if not plugin[0] in ['.', '_']:
#        log('Adding editor "%s"' % plugin)
#        packages.append('pida.editors.%s' % plugin)

log('Performing setup.')

services = []
for svc in os.listdir(os.path.join('pida', 'services')):
    if svc.endswith('.py') and not svc.startswith('_'):
        name = svc.rsplit('.')[0]
        services.append('%s = pida.services.%s:Service' % (name, name))
plugins = []
for svc in os.listdir(os.path.join('pida', 'plugins')):
    if svc.endswith('.py') and not svc.startswith('_'):
        name = svc.rsplit('.')[0]
        plugins.append('%s = pida.plugins.%s:Plugin' % (name, name))
editors = []
for svc in os.listdir(os.path.join('pida', 'editors')):
    if svc.endswith('.py') and not svc.startswith('_'):
        name = svc.rsplit('.')[0]
        editors.append('%s = pida.editors.%s:Service' % (name, name))

pixmaps = []
for pix in os.listdir(os.path.join('data', 'pixmaps')):
    if pix.endswith('xpm'):
        pixmaps.append('data/pixmaps/%s' % pix)
print pixmaps
setup(name='pida',
    version='0.3planning',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    url='http://pida.berlios.de',
    download_url='http://pida.berlios.de/index.php/PIDA:Downloads',
    description=('A Python IDE written in Python and GTK, '
                 'which uses Vim as its editor.'),
    long_description='Please visit the Pida website for more details.',
    packages=packages,
    package_dir = {'pida': 'pida'},
    scripts=['scripts/pida'],
    data_files=[
                ('images', ['data/icons.dat']),
                ('glade', ['glade/project-creator.glade']),
                ('pixmaps', pixmaps),
                ('', ['data/icons/pida-icon.png']),
                ],
    entry_points = {
        'console_scripts': [
            'pida = pida.core.application:main',
        ],
        'gui_scripts': [],
        'pida.services' : services,
        'pida.plugins' : plugins,
        'pida.editors' : editors,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development']
      
      )
