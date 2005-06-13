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

import gtk

class FolderDialog(gtk.FileChooserDialog):
    TITLE = 'Select Directory'
    ACTION = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER

    def __init__(self, cb, responsecb):
        self.cb = cb
        gtk.FileChooserDialog.__init__(self, title=self.TITLE,
                                             parent=None,
                                             action=self.ACTION,
                                             buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.connect('response', responsecb)

    def connect_widgets(self):
        pass

    #def show(self):
        #self.set_current_folder(directory)
    #    self.show()

class FolderButton(gtk.HBox):
    
    DTYPE = FolderDialog

    def __init__(self, cb):
        self.cb = cb
        gtk.HBox.__init__(self)
        self.entry = gtk.Entry()
        self.pack_start(self.entry)
        self.but = self.cb.icons.get_button('open')
        self.but.connect('clicked', self.cb_open)
        self.pack_start(self.but, expand=False)
        self.dialog = None

    def update(self):
        self.entry.set_text(self.dialog.get_filename())

    def show(self):
        if not self.dialog:
            self.dialog = self.DTYPE(self.cb, self.cb_response)
            self.dialog.connect('destroy', self.cb_destroy)
        self.dialog.set_filename(self.entry.get_text())
        self.dialog.show()

    def cb_response(self, d, resp):
        self.dialog.hide()
        if resp == gtk.RESPONSE_ACCEPT:
            self.update()
        
    def cb_destroy(self, *args):
        self.dialog.destroy()
        self.dialog = None

    def cb_open(self, *args):
        self.show()

    def get_filename(self):
        return self.entry.get_text()

    def set_filename(self, fn):
        self.entry.set_text(fn)

class FileDialog(FolderDialog):
    TITLE = 'Select File'
    ACTION = gtk.FILE_CHOOSER_ACTION_OPEN

    def connect_widgets(self):
        def cb(*args):
            self.response(1)
        self.connect('file-activated', cb)
        
class FileButton(FolderButton):

    DTYPE = FileDialog
    
