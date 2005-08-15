# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: __init__.py 352 2005-07-14 00:16:02Z gcbirzan $
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

import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry
import pida.configuration.config as config
import pida.base as base

try:
    import gtkhtml2
except ImportError:
    gtkhtml2 = None

import threading
import urllib
import urllib2
import urlparse
import gobject
import gtk

class Plugin(plugin.Plugin):
    VISIBLE = False

    def configure(self, reg):
        self.registry = reg.add_group('browser', 'Options for web browsing')
    

        self.registry.add('internal_browser', registry.Boolean,
                          False,
                          'Determines whether the Pida internal browser is used')
        self.registry.add('homepage', registry.RegistryItem,
                          'http://www.google.com',
                          'The default web browser homepage')

    def evt_newbrowser(self, url=None):
        if not url:
            url = self.registry.homepage.value()
            
        embd = self.registry.internal_browser.value() and not (gtkhtml2 is None)
        if embd:
            browser = Browser()
            self.do_action('newcontentpage', browser)
            browser.fetch(url)
        else:
            self.do_action('command', 'browse', [url])

    def evt_reset(self):
        br = self.prop_main_registry.commands.browser.value()
        self.do_action('register_external_command',
                    'browse', '%s %%s' % br,
                    1, ['URL'], 'internet')


    __call__ = evt_newbrowser


class Browser(base.pidaobject):
    
    icon = 'internet' 

    def do_init(self):
        self.fetcher = Fetcher(self)
        self.doc = gtkhtml2.Document()
        self.doc.connect('request-url', self.cb_request_url)
        self.doc.connect('link-clicked', self.cb_link_clicked)
        self.view = gtkhtml2.View()
        self.view.connect('on-url', self.ro)
        self.view.set_document(self.doc)
        self.view.set_size_request(400,300)
        self.swin = gtk.ScrolledWindow()
        self.swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.swin.add(self.view)

        self.win = gtk.VBox()

        hb = gtk.HBox()
        toolbar = gtkextra.Toolbar()
        hb.pack_start(toolbar.win, expand=False)
        
        toolbar.add_button('left', self.cb_back_clicked, 'Back')
        toolbar.add_button('close', self.cb_stop_clicked, 'Stop')

        self.location = gtk.Entry()
        hb.pack_start(self.location)

        self.location.connect('activate', self.cb_url_entered)

        self.win.pack_start(hb, expand=False)
        self.win.pack_start(self.swin)

    def start(self):
        pass

    def die(self):
        pass

    def fetch(self, url):
        self.url = url
        self.doc.clear()
        self.doc.open_stream('text/html')
        self.fetcher.fetch_url(url)

    def done(self):
        self.location.set_text(self.url)

    def ro(self, *args):
        return
        print 'ro', args

    def cb_onurl(self, view, url):
        print url

    def cb_url_entered(self, entry):
        url = self.location.get_text()
        print url
        self.fetch(url)

    def cb_request_url(self, doc, url, stream):
        url = urlparse.urljoin(self.url, url)
        self.fetcher.fetch_url(url, stream)
        
    def cb_link_clicked(self, doc, url):
        url = urlparse.urljoin(self.url, url)
        self.fetch(url)

    def cb_back_clicked(self, button):
        pass

    def cb_stop_clicked(self, button):
        pass

class Fetcher(base.pidaobject):

    def do_init(self, browser):
        self.browser = browser

    def fetch_url(self, url, stream=None):
        def fetch():
            fd = urllib.urlopen(url)
            gtk.threads_enter()
            gobject.io_add_watch(fd.fp, gobject.IO_IN, self.readable, stream)
            gtk.threads_leave()
        t = threading.Thread(target=fetch)
        t.start()

    def readable(self, fd, cond, stream):
        data = fd.read(1)
        #print data
        if data:
            if stream:
                stream.write(data)
            else:
                self.browser.doc.write_stream(data)
            return True
        else:
            if stream:
                stream.close()
            else:
                self.browser.doc.close_stream()
                self.browser.done()
            return False

