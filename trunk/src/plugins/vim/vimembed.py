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

''' A library to embed vim in a gtk socket '''


import gtk
import os
import pty
import gobject



class Vim(object):

    def __init__(self, command, args):
        self.win = gtk.EventBox()
        self.socket = gtk.Socket()
        self.socket.connect('plug-added', self.cb_plugged)
        self.socket.connect('plug-removed', self.cb_unplugged)
        self.win.add(self.socket)
        self.pid = None
        self.command = command
        self.args = args
        self.r_cb_plugged = None
        self.r_cb_unplugged = None

    def run(self):
        xid = self.socket.get_id()
        args = self.args[:] # a copy
        if not xid:
            return
        if not self.pid:
            pid = os.fork()
            if pid == 0:
                args.extend(['--socketid', '%s' % xid])
                os.execvp(self.command, args)
            else:
                self.pid = pid

    def stop(self):
        try:
            os.kill(self.pid, 15)
        except OsError:
            pass
        self.pid = None
        self.socket.destroy()
        self.win.destroy()

    def cb_plugged(self, *a):
        if self.r_cb_plugged:
            self.r_cb_plugged()

    def cb_unplugged(self, *a):
        self.stop()
        if self.r_cb_unplugged:
            self.r_cb_unplugged()

    def connect(self, plugged, unplugged):
        self.r_cb_plugged = plugged
        self.r_cb_unplugged = unplugged

class PidaVim(Vim):
    
    def __init__(self, cb, holder, command, name):
        self.cb = cb
        self.name = name
        # get the user preferences
        Vim.__init__(self, command,  ['gvim', '-f', '--servername', name])
        holder.add(self.win)
        holder.show_all()
        self.run()
        

class TestWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_size_request(600,400)
        v = PidaVim(None, self, '/usr/bin/gvim', 'TEST')


if __name__ == '__main__':
    a = TestWindow()
    gtk.main()
