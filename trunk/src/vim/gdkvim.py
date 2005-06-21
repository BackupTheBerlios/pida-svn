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


""" A library to control vim -g using its X protocol interface (with gdk)."""

# You require pygtk probably
import gtk.gdk as gdk
import gtk
import os

class VimWindow(gtk.Window):
    ''' A GTK window that can communicate with Vim. '''
    def __init__(self, cb=None):
        self.cb = cb
        gtk.Window.__init__(self)
        self.realize()
        self.window.property_change("Vim", gdk.SELECTION_TYPE_STRING, 8,
                            gdk.PROP_MODE_REPLACE, "6.0")
        self.add_events(gtk.gdk.PROPERTY_CHANGE_MASK)
        self.connect('property-notify-event', self.cb_notify)
        self.serial = 1
        self.messages = []
        self.callbacks = {}
        self.bad_servers = []
        self.cwds = {}

    def serverlist(self):
        ''' get the serverlist from the X root window '''
        rootwindow = gdk.get_default_root_window()
        # Read the property
        propval = rootwindow.property_get("VimRegistry")
        res = {}
        if propval:
            prop = propval[-1].split('\0')
            for r in prop:
                if r:
                    rs = r.split()
                    id = long(int(rs[0], 16))
                    name = rs[1]
                    w = self.server_exists(id)
                    if w and not (name in self.bad_servers):
                        res[name] = id
        return res

    def server_exists(self, id):
        ''' Vaguely attempt to identify whether the server exists. '''
        return gdk.window_foreign_new(id)
    
    def server_window(self, name):
        ''' Create and return a foreign window for a Vim server or None. '''
        try:
            wid = self.serverlist()[name]
            return self.server_exists(wid)
        except KeyError:
            return None

    def generate_message(self, server, cork, message, sourceid):
        """ Generate a message. """
        m = '\0%s\0-n %s\0-s %s\0-r %x %s\0' % (cork, server, message,
                                                sourceid, self.serial)
        return m
 
    def parse_message(self, message):
        m = {}
        for t in [s.split(' ') for s in message.split('\0')]:
            if t and len(t[0]):
                if t[0].startswith('-'):
                    m[t[0][1:]] = t[1]
                else:
                    m['t'] = t[0]    
        return m

    def send_message(self, server, message, asexpr, callback):
        cork = (asexpr and 'c') or 'k'
        sw = self.server_window(server)
        if sw and sw.property_get("Vim"):
            mp = self.generate_message(server, cork, message,
                                    self.window.xid)
            sw.property_change("Comm", gdk.TARGET_STRING, 8,
                                    gdk.PROP_MODE_APPEND, mp)
            if asexpr and callback:
                self.callbacks['%s' % (self.serial)] = callback
                self.serial += 1

    def send_expr(self, server, message, callback):
        self.send_message(server, message, True, callback)

    def send_keys(self, server, message):
        self.send_message(server, message, False, False)

    def send_esc(self, server):
        self.send_keys(server, '<C-\><C-N>')

    def send_ret(self, server):
        self.send_keys(server, '<RETURN>')

    def send_ex(self, server, message):
        self.send_esc(server)
        self.send_keys(server, ':%s' % message)
        self.send_ret(server)

    def foreground(self, server):
        def cb(*args):
            pass
        self.send_expr(server, 'foreground()', cb)
        
    def change_buffer(self, server, nr):
        self.send_ex(server, 'b!%s' % nr)

    def close_buffer(self, server):
        self.send_ex(server, 'bw')

    def change_cursor(self, server, x, y):
        self.send_message(server, 'cursor(%s, %s)' % (y, x), True, False)
        self.send_esc(server)

    def save_session(self, name):
        self.send_ex('mks %s' % name)

    def open_file(self, server, name):
        self.send_ex(server, 'confirm e %s' % name)

    def preview_file(self, server, fn):
        self.send_ex(server, 'pc')
        self.send_ex(server, 'set nopreviewwindow')
        self.send_ex(server, 'pedit %s' % fn)

    def get_bufferlist(self, server):
        def cb(bl):
            l = [i.split(':') for i in bl.strip(';').split(';')]
            l = [(n[0], self.abspath(server, n[1])) for n in l]
            self.cb.evt('bufferlist', l)
        self.get_cwd(server)
        self.send_expr(server, 'Bufferlist()', cb)

    def get_current_buffer(self, server):
        def cb(bs):
            bn = bs.split(',')
            bn[1] = self.abspath(server, bn[1])
            self.cb.evt('bufferchange', *bn)
        self.get_cwd(server)
        self.send_expr(server, "bufnr('%').','.bufname('%')", cb)

    def cwd(self, server):
        return self.cwds[server]

    def get_cwd(self, server):
        def cb(cwd):
            self.cwds[server] = cwd
        self.send_expr(server, "getcwd()", cb)

    def quit(self, server):
        self.send_ex(server, 'q')

    def abspath(self, server, name):
        if not name.startswith('/'):
            hdir = os.path.expanduser('~')
            name = os.path.join(self.cwds.setdefault(server, hdir), name)
        return name

    def cb_notify(self, *a):
        win, ev =  a
        if hasattr(ev, 'atom'):
            if ev.atom == 'Comm':
                message = self.window.property_get('Comm', pdelete=True)
                if message:
                    self.cb_reply(message[-1])
        return True


   

    def cb_reply(self, data):
        mdict = self.parse_message(data)
        if mdict['t'] == 'r':
            if mdict['s'] in self.callbacks:
                self.callbacks[mdict['s']](mdict['r'])
        else:
            self.cb_reply_async(mdict['n'])

    def cb_reply_async(self, data):
        if data.count(','):
            evt, d = data.split(',', 1)
            self.cb.evt(evt, *d.split(','))
        else:
            self.bad_servers.append(data)
            self.cb.evt('badserver', data)
            print '?bad server', data        

if __name__ == '__main__':
    w = VimWindow()

    gtk.main()
