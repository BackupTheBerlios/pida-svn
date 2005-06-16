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

""" The Pida buffer explorer plugin """

# system imports
import os
import mimetypes
# GTK imports
import gtk
import gobject
# Pida imports
import pida.plugin as plugin
import pida.gtkextra as gtkextra

class BufferTree(gtkextra.Tree):
    ''' Tree view control for buffer list. '''
    YPAD = 2
    XPAD = 2
    COLUMNS = [('icon', gtk.gdk.Pixbuf, gtk.CellRendererPixbuf, True,
                 'pixbuf'),
                ('name', gobject.TYPE_STRING, gtk.CellRendererText, True,
                 'text'),
                ('file', gobject.TYPE_STRING, None, False, None),
                ('number', gobject.TYPE_INT, None, False, None)]

    def populate(self, bufferlist):
        ''' Populate the list with the given buffer list. '''
        self.clear()
        for buf in bufferlist:
            path = ''
            if len(buf) > 1:
                path = '%s' % buf[1]
            try:
                nr = int(buf[0])
                name = os.path.split(path)[-1]
                mtype = mimetypes.guess_type(path)[0]
            except ValueError:
                nr = 0
                name = ''
                mtype = None
            if mtype:
                mtype = mtype.replace('/','-')
                im = self.cb.icons.get_image(mtype).get_pixbuf()
            else:
                im = self.cb.icons.get_image('text-plain').get_pixbuf()
            self.add_item([im, name, path, nr])

    def set_active(self, i):
        ''' Set the selected element in the list by buffer number. '''
        for node in self.model:
            if node[3] == i:
                self.view.set_cursor(node.path)
                return True
        return False


class Plugin(plugin.Plugin):
    NAME = 'Buffers'
    DICON = 'refresh', 'Refresh the buffer list'
    
    def populate_widgets(self):
        self.buffers = BufferTree(self.cb)
        self.add(self.buffers.win)
        self.add_button('open', self.cb_open, 'Open file')
        self.add_button('close', self.cb_close, 'Close Buffer')
        self.cbuf = None
        self.odialog = None

    def connect_widgets(self):
        self.buffers.connect_select(self.cb_bufs_selected)

    def cb_alternative(self):
        ''' Called when the detach button is clicked. '''
        self.cb.action_getbufferlist()

    def cb_bufs_selected(self, tv):
        ''' Called when an element in the buffer list is selected. '''
        if not self.cbuf or self.cbuf != self.buffers.selected(3):
            self.cb.action_changebuffer(self.buffers.selected(3))

    def cb_open(self, *args):
        ''' Called when the open button is clicked. '''
        if not self.odialog:
            self.odialog = gtkextra.FileDialog(self.cb, self.cb_open_response)
            self.odialog.connect('destroy', self.cb_open_destroy)
        self.odialog.show()

    def cb_open_response(self, dialog, response):
        ''' Called when a response is recived from the open dialog. '''
        self.odialog.hide()
        if response == gtk.RESPONSE_ACCEPT:
            fn = self.odialog.get_filename()
            self.cb.action_openfile(fn)

    def cb_open_destroy(self, *args):
        ''' Called when the open dialog is destroyed. '''
        self.odialog = None
        return True

    def cb_close(self, *a):
        ''' Called when the close buffer button is clicked. '''
        self.cb.action_closebuffer()

    def refresh(self, bufferlist):
        ''' Refresh the bufferlist. '''
        self.buffers.populate(bufferlist)

    def evt_bufferlist(self, bufferlist):
        ''' Called when a new buffer list is received. '''
        self.refresh(bufferlist)
        self.cb.action_getcurrentbuffer()

    def evt_bufferchange(self, i, name):
        ''' Called when the buffer number has changed. '''
        self.cbuf = int(i)
        if not self.buffers.set_active(self.cbuf):
            self.cb.action_getbufferlist()

    def evt_bufferunload(self, *a):
        ''' Called when a buffer is unloaded '''
        self.cb.action_getbufferlist()
    
    def evt_serverchange(self, server):
        ''' Called when the server is changed '''
        self.cb.action_getbufferlist()

