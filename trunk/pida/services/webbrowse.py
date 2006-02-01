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
import gtkhtml2

import threading
import urllib
import urllib2
import urlparse
import gobject
import gtk

def get_url_mark(url):
    if '#' in url:
        url, mark = url.rsplit('#', 1)
    else:
        mark = None
    return url, mark

def open_url(url):
    return urllib.urlopen(url)

def fetch_url(url, read_cb, hup_cb):
    def _fetch():
        def _readable(fd, cond):
            data = fd.read(1024)
            if data:
                read_cb(data)
                return True
            else:
                hup_cb(url)
                return False
        fd = open_url(url)
        gobject.io_add_watch(fd.fp, gobject.IO_IN, _readable)
    t = threading.Thread(target=_fetch)
    t.start()
    #_fetch()

class web_client(gtk.ScrolledWindow):

    def __init__(self, manager=None):
        super(web_client, self).__init__()
        self.__view = gtkhtml2.View()
        self.add(self.__view)
        self.__document = gtkhtml2.Document()
        self.__view.set_document(self.__document)
        self.__document.connect('request-url', self.cb_request_url)
        self.__document.connect('link-clicked', self.cb_link_clicked)
        self.__current_url = None
        self.__current_mark = None
        self.__fetching_url = None
        self.__fetching_mark = None
        self.__manager = manager
        self.__urlqueue = []

    def load_url(self, url):
        url, mark = get_url_mark(url)
        self.__fetching_mark = mark
        self.__fetching_url = url
        if url != self.__current_url:
            self.__manager.stop_button.set_sensitive(True)
            self.__document.clear()
            self.__document.open_stream('text/html')
            fetch_url(url, self.cb_loader_data, self.cb_loader_finished)
        else:
            self.finished(url)

    def cb_loader_data(self, data):
        self.__document.write_stream(data)

    def cb_loader_finished(self, url):
        self.__document.close_stream()
        self.finished(url)
    
    def stop(self):
        self.cb_loader_finished(self.__fetching_url)

    def back(self):
        if len(self.__urlqueue) > 1:
            self.__urlqueue.pop()
            url = self.__urlqueue.pop()
            self.load_url(url)

    def finished(self, url):
        self.__current_url = url
        self.__current_mark = self.__fetching_mark
        if self.__current_mark:
            self.__view.jump_to_anchor(self.__current_mark)
        else:
            self.__view.jump_to_anchor('')
        durl = url
        if self.__current_mark:
            durl = durl + '#' + self.__current_mark
        self.__manager.stop_button.set_sensitive(False)
        self.__manager.location.set_text(url)
        self.__urlqueue.append(url)
        self.__manager.back_button.set_sensitive(len(self.__urlqueue) > 1)
        

    def cb_request_url(self, doc, url, stream):
        def _data(data):
            stream.write(data)
        def _hup(url):
            stream.close()
        url = urlparse.urljoin(self.__fetching_url, url)
        fetch_url(url, _data, _hup)

    def cb_link_clicked(self, doc, url):
        url = urlparse.urljoin(self.__current_url, url)
        self.load_url(url)




class BrowserView(contentview.content_view):
    ICON_NAME = 'internet' 

    HAS_TITLE = False

    def init(self):
        controls = toolbar.Toolbar()
        controls.connect('clicked', self.cb_toolbar_clicked)
        self.back_button = controls.add_button('back',
            'go-back-ltr', 'Go back to the previous URL')
        self.back_button.set_sensitive(False)
        self.stop_button = controls.add_button('close',
            'gtk-stop', 'Stop loading the current URL')
        #self.stop_button.set_sensitive(False)
        bar = gtk.HBox()
        self.widget.pack_start(bar, expand=False)
        bar.pack_start(controls, expand=False)
        self.location = gtk.Entry()
        bar.pack_start(self.location)
        self.location.connect('activate', self.cb_url_entered)
        self.__browser = web_client(self)
        self.widget.pack_start(self.__browser)
        self.status_bar = gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id('web')
        self.widget.pack_start(self.status_bar, expand=False)

    def cb_url_entered(self, entry):
        url = self.location.get_text()
        self.fetch(url)

    def fetch(self, url):
        self.__browser.load_url(url)

    def cb_toolbar_clicked(self, button, name):
        if name == 'back':
            self.__browser.back()
        else:
            self.__browser.stop()
            
            


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
            url = ('/usr/share/gtk-doc/html/pygtkmozembed/'
                   'gtkmozembed-class-reference.html')
        view.fetch(url)

    def create_view(self):
        view = self.create_multi_view()
        view.connect('raised', self.cb_view_raised)
        return view
    
    def cb_view_raised(self, view):
        self.__last_view = view

Service = web_browser
