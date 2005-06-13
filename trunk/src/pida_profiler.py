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

''' The Pida profiler plugin '''

#system imports
import os
import profile
import cPickle as pickle

# GTK imports
import gtk
import gobject

# Pida imports
import tree
import plugin
import gtkipc

def script_directory():
    def f(): pass
    d, f = os.path.split(f.func_code.co_filename)
    return d

SCRIPT_DIR = script_directory()



class Plugin(plugin.Plugin):
    NAME = 'Profiler'
    DICON = 'profile', 'Profile the current buffer.'
    ICON = 'profile'
    
    def populate_widgets(self):

        sb = gtk.HBox()
        self.add(sb)

        self.sortbox = gtk.combo_box_new_text()
        sb.pack_start(self.sortbox)

        self.sortascending = gtk.CheckButton()
        sb.pack_start(self.sortascending)

        self.profiler = Profiler(self.cb)
        self.fn = None
        self.readbuf = ''

    def cb_alternative(self, *args):
        #if self.fn and self.fn.endswith('.py'):
        self.profiler.run(self.fn, self.cb_read, self.cb_hup)
            
    def cb_read(self, fd, cond):
        s = os.read(fd, 1024)
        self.readbuf = ''.join([self.readbuf, s])
        return True

    def cb_hup(self, fd, cond):
        print hup
        os.close(fd)
        t = self.readbuf
        self.readbuf = ''
        self.reaceived_profile(t)
        return False
    
    

    def evt_bufferchange(self, nr, name):
        self.fn = name


class Profiler(object):

    def __init__(self, cb):
        self.cb = cb
        self.ipc = gtkipc.IPWindow(self)

    def run(self, filename, ioreadcb, iohupcb):
        profilerfn = os.path.join(SCRIPT_DIR, 'profiler.py')
        xid = '%s' % self.ipc.get_lid()
        py = self.cb.opts.get('commands', 'python')
        pid = os.fork()
        if pid == 0:
            os.execvp(py, ['python', profilerfn, filename, xid])
        else:
            self.pid = pid
        print 'run'

    def do_stats(self, outf):
        f = open(outf, 'r')
        stats = pickle.load(f)
        f.close()
        os.remove(outf)
        print 'stats', stats



