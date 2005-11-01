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

import sys
sys.path.insert(2, '../../')
#sys.path.insert(1, '/home/ali/working/pida/pida/branches/pida-ali/')

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor


import pida.core.service as service

import os
import gtk
import boss
import base


class Application(object):
    """The PIDA Application."""

    def __init__(self):
        self.dirs = create_home_tree()
        self.boss = boss.Boss()
        self.boss.application = self

    def start(self):
        """Start PIDA."""
        self.boss.start()
        reactor.run()

    def stop(self):
        """Stop PIDA."""
        reactor.stop()

def create_home_tree(root=None):
    dirs = {}
    if root is None:
        root = os.path.expanduser('~/.pida2')
    mkdir(root)
    dirs['root'] = root
    for name in ['conf', 'log', 'run', 'vcs', 'sockets']:
        path = os.path.join(root, name)
        mkdir(path)
        dirs[name] = path
    return dirs

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def main():
    app = Application()
    app.start()

if __name__ == '__main__':
    gtk.threads_init()
    main()
