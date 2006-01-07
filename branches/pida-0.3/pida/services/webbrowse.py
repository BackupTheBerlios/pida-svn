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

import pida.core.service as service
import pida.pidagtk.contentview as contentview
import pida.pidagtk.toolbar as toolbar
import gtk
import os
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

class BrowserView(contentview.content_view):
    ICON = 'internet' 

    FIXED_TITLE = 'browser'

    def init(self):
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
        controls = toolbar.Toolbar()
        controls.connect('clicked', self.cb_toolbar_clicked)
        controls.add_button('back', 'left', 'Go back to the previous URL')
        controls.add_button('close', 'close', 'Stop loading the current URL')
        bar = gtk.HBox()
        self.widget.pack_start(bar, expand=False)
        bar.pack_start(controls, expand=False)
        self.location = gtk.Entry()
        bar.pack_start(self.location)
        self.location.connect('activate', self.cb_url_entered)
        self.widget.pack_start(self.swin)
        self.urlqueue = []
        self.urlqueueposition = 0


    def fetch(self, url):
        if '#' in url:
            aurl, self.mark = url.split('#')
        else:
            aurl = url
            self.mark = None    
        self.url = url
        self.doc.clear()
        self.doc.open_stream('text/html')
        self.fetcher.fetch_url(aurl)

    def done(self):
        self.urlqueue.append(self.url)
        self.location.set_text(self.url)
        if self.mark:
            self.scroll_to_mark(self.mark)

    def scroll_to_mark(self, mark):
        self.view.jump_to_anchor(self.url)

    def ro(self, *args):
        return

    def cb_style_updated(self, node, style, foo):
        pass

    def cb_onurl(self, view, url):
        print url

    def cb_url_entered(self, entry):
        url = self.location.get_text()
        self.fetch(url)

    def cb_request_url(self, doc, url, stream):
        url = urlparse.urljoin(self.url, url)
        self.fetcher.fetch_url(url, stream)
        
    def cb_link_clicked(self, doc, url):
        url = urlparse.urljoin(self.url, url)
        self.fetch(url)

    def cb_toolbar_clicked(self, toolbar, namr):
        if name == 'back':
            if len(self.urlqueue) > 1:
                self.urlqueue.pop()
                self.fetch(self.urlqueue[-1])
                self.urlqueue.pop()

class web_browser(service.service):

    NAME = 'webbrowser'

    multi_view_type = BrowserView
    multi_view_book = 'view'    

    def init(self):
        self.__last_view = None

    def cmd_browse(self, url=None, newview=False):
        view = self.create_view()
        if not url:
            url = 'http://pseudoscience.co.uk/'
        view.fetch(url)

    def create_view(self):
        view = self.create_multi_view()
        view.connect('raised', self.cb_view_raised)
        return view
    
    def cb_view_raised(self, view):
        self.__last_view = view

    

class Fetcher(object):

    def __init__(self, browser):
        self.browser = browser

    def fetch_url(self, url, stream=None):
        def fetch():
            if not url.endswith('css'):
                fd = urllib.urlopen(url)
                gobject.io_add_watch(fd.fp, gobject.IO_IN, self.readable, stream)
            else:
                if stream:
                    stream.close()
        t = threading.Thread(target=fetch)
        t.start()
    
    def readable(self, fd, cond, stream):
        data = fd.read(64)
        gtk.threads_enter()
        if data:
            if stream:
                stream.write(data)
            else:
                self.browser.doc.write_stream(data)
            gtk.threads_leave()
            return True
        else:
            if stream:
                stream.close()
            else:
                self.browser.doc.close_stream()
                self.browser.done()
            gtk.threads_leave()
            return False


Service = web_browser
