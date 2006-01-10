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

from setuptools import setup

import os

VERBOSE = True

VERSION_STRING = '0.3.0'

def log(message):
    if VERBOSE:
        print 'Pida:', message

log('Preparing core...')
packages = ['pida',
            'pida.core',
            'pida.pidagtk',
            'pida.services',
            'pida.editors',
            'pida.plugins',
            'pida.utils',
            'pida.utils.vim',
            'pida.utils.vc',
            'pida.utils.pyflakes']

log('Performing setup...')


def find_entry_points(directory_name, entrypoint_name):
    entrypoints = []
    dirpath = os.path.join('pida', directory_name)
    for svc in os.listdir(dirpath):
        if svc.endswith('.py') and not svc.startswith('_'):
            name = svc.split('.', 1)[0]
            entrypoints.append('%s = pida.%s.%s:%s' %
                            (name, directory_name, name, entrypoint_name))
    return entrypoints

services = find_entry_points('services', 'Service')
plugins = find_entry_points('plugins', 'Plugin')
editors = find_entry_points('editors', 'Service')

def ensure_version_file_exists():
    version_path = os.path.join('data', 'version')
    if not os.path.exists(version_path):
        f = open(version_path, 'w')
        f.write('%s\n' % VERSION_STRING)
        f.close()

ensure_version_file_exists()

pixmaps = []
for pix in os.listdir(os.path.join('data', 'pixmaps')):
    if pix.endswith('xpm'):
        pixmaps.append('data/pixmaps/%s' % pix)

uis = []
for ui in os.listdir('glade'):
    if ui.endswith('glade'):
        uis.append('glade/%s' % ui)

#print pixmaps
#print uis
setup(name='pida',
    version=VERSION_STRING,
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
                ('glade', uis),
                ('pixmaps', pixmaps),
                ('version', ['data/version']),
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
