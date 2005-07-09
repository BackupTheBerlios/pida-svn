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

import os
import gtk
import pango
import gobject
import pida.plugin as plugin
import pida.gtkextra as gtkextra


class Plugin(plugin.Plugin):
    ICON = 'paste'
    DICON = 'paste', 'Make a paste to a pastebin site'
    
    def init(self):
        self.pastes = []
        self.historyposition = 0

    def configure(self, reg):
        pass

    def populate_widgets(self):
        
        self.model = gtk.TextBuffer()
        self.view = gtk.TextView(self.model)


        self.resmodel = gtk.TextBuffer()
        self.restag = self.resmodel.create_tag(foreground='#0000FF',
                                                scale=pango.SCALE_SMALL,
                                                font='Monospace')
        self.resview = gtk.TextView(self.resmodel)
        self.resview.set_wrap_mode(gtk.WRAP_CHAR)
        self.resview.set_sensitive(False)
        self.resmodel.insert(self.resmodel.get_end_iter(), 'No results yet.\n')
    
        ressw = gtk.ScrolledWindow()
        ressw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        #ressw.add(self.resview)
        self.add(self.resview, expand=False)

        self.add(gtk.HSeparator(), expand=False, padding=2)

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.add(self.view)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(scrolledwindow)
        
        self.sitelist = gtk.combo_box_new_text()
        

        self.add(self.sitelist, expand=False)

        self.poslabel = gtk.Label()
        self.cusbar.pack_start(self.poslabel)

        self.back_but = self.add_button('left', self.cb_history,
                        'Go to the last paste in the history', [-1])

        self.forw_but = self.add_button('right', self.cb_history,
                        'Go to the next paste in the history', [1])

        self.forw_but.set_sensitive(False)

        self.back_but.set_sensitive(False)

        
        self.set_pos_label()


    def paste(self, text):
        paster = RafbPaster(self.cb, self)
        paster.paste(text)

    def cb_history(self, button, amount):
        self.historyposition = self.historyposition + amount
        self.historyposition = max(0, self.historyposition)
        self.historyposition = min(len(self.pastes) - 1, self.historyposition)
        self.displaypaste(self.historyposition)

    def cb_alternative(self, *args):
        text = self.get_text()
        self.paste(text)

    def get_text(self):
        siter = self.model.get_start_iter()
        eiter = self.model.get_end_iter()
        return self.model.get_text(siter, eiter)

    def newpaste(self, url, text):
        self.pastes.append([url, text])
        self.historyposition = len(self.pastes) - 1
        self.displaypaste(self.historyposition)

    def displaypaste(self, index):
        try:
            url, text = self.pastes[index]
        except IndexError:
            return
        self.back_but.set_sensitive(index != 0)
        self.forw_but.set_sensitive(index != (len(self.pastes) - 1))

        self.resview.set_sensitive(True)
        self.resmodel.set_text('')
        self.resmodel.insert_with_tags(self.resmodel.get_end_iter(), url, self.restag)
        self.model.set_text('')
        self.model.insert(self.model.get_end_iter(), text)
        self.set_pos_label()

    def set_pos_label(self):
        tot = len(self.pastes)
        pos = '-'
        if tot:
            pos = self.historyposition + 1
        self.poslabel.set_markup('<small>%s of %s</small>' % (pos, tot))


import urllib
import threading
class Paster(object):
    URL = None
    def __init__(self, cb, plugin):
        self.cb = cb
        self.plugin = plugin
        self.readbuffer = []

    def paste(self, text):
        self.post(())

    def post(self, dataopts, text):
        def t():
            data = urllib.urlencode(dataopts)
            page = urllib.urlopen(self.URL, data)
            gtk.threads_enter()
            gobject.io_add_watch(page, gobject.IO_IN, self.readable, text)
            gtk.threads_leave()
            print 'tried'
        t = threading.Thread(target=t)
        t.start()

    def readable(self, fd, cond, text):
        data = fd.read(16)
        if not data:
            print fd.geturl()
            self.received(fd.geturl(), ''.join(self.readbuffer), text)
            self.readbuffer = []
            return False
        else:
            self.readbuffer.append(data)
            return True

    def received(self, url, page, text):
        url = self.parse(url, page)
        self.plugin.newpaste(url, text)

    def parse(self, url, page):
        return url

class RafbPaster(Paster):
    URL = 'http://www.rafb.net/paste/paste.php'
    def paste(self, text):
        dataopts = [('text', text),
                    ('name', 'Pida'),
                    ('desc', 'pida paste'),
                    ('lang', 'Python'),
                    ('cvt_tabs', 4),
                    ('submit', 'Paste')]
        self.post(dataopts, text)

        


