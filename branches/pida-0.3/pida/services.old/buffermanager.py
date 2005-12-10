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
import pida.core.buffer as buffer
import glob
import os
import pida.core.service as service
import pida.pidagtk.buffertree as buffertree
import gobject

import pida.pidagtk.contentbook as contentbook

class BufferView(contentbook.ContentView):

    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_LABEL = False

    def populate(self):
        self.__buffertree = buffertree.BufferTree()
        self.pack_start(self.__buffertree.details_box, expand=False)
        self.pack_start(self.__buffertree)

    def get_bufferview(self):
        return self.__buffertree
    bufferview = property(get_bufferview)

class Buffermanager(service.Service):
    NAME = 'buffermanager'

    COMMANDS = [['open-file', [('filename', True)]],
                ['open-file-line', [('filename', True), ('linenumber', True)]],
                ['close-file', [('filename', True)]],
                ['add-buffer', [('buffer', True)]],
                ['rename-buffer', [('buffer', True), ('filename', True)]],
                ['close-current-file', []],
                ['open-new-file', []],
                ['reset-current-buffer', []],
                ['get-bufferlist', []],
                ['register-file-handler', [('filetype', True), ('handler', True)]],
                ['get-currentbuffer', []]]

    EVENTS = ['buffer-opened', 'buffer-modified']

    BINDINGS = [('editor', 'started'),
                ('editor', 'file-opened'),
                ('editor', 'current-file-closed')]
    
    def init(self):
        self.__currentbuffer = None
        self.__buffers = {}
        self.__handlers = {}

    def populate(self):
        self.__view = BufferView()
        self.__view.bufferview.connect('clicked', self.cb_view_clicked)

    def cb_view_clicked(self, view, bufitem):
        buf = bufitem.value
        if buf != self.__currentbuffer:
            self.cmd_open_file(buf.filename)

    def cmd_get_currentbuffer(self):
        return self.__currentbuffer

    def cmd_get_bufferlist(self):
        return self.__bufferlist

    def cmd_open_file(self, filename):
        self.__open_file(filename)
        return self.__currentbuffer

    def cmd_open_file_line(self, filename, linenumber):
        self.__open_file(filename)
        self.__editor.__open_file_line(filename, linenumber)

    def __open_file(self, filename):
        if self.__currentbuffer is None or self.__currentbuffer.filename != filename:
            if filename not in self.__buffers:
                handler = self.__get_handler(filename)
                if handler is None:
                    new_buf = self.__create_editorbuffer(filename)
                else:
                    new_buf = handler.create_buffer(filename)
                new_buf.handler = handler
                self.__add_buffer(new_buf)
            self.__set_current_buffer(self.__buffers[filename])

    def __create_editorbuffer(self, filename):
        new_buf = buffer.Buffer(filename)
        new_buf.boss = self.boss
        return new_buf

    def __set_current_buffer(self, buf):
        self.__currentbuffer = buf
        self.__view.bufferview.set_currentbuffer(buf.filename)
        self.__view.bufferview.display_buffer(buf)
        if buf.handler is not None:
            buf.handler.open_file(buf)
        else:
            self.boss.command('editor', 'open-file',
                              filename=buf.filename)
        self.emit_event('buffer-opened', buffer=buf)

    def __add_buffer(self, new_buf):
        self.__buffers[new_buf.filename] = new_buf
        self.__view.bufferview.set_bufferlist(self.__buffers)

    def __get_handler(self, filename):
        for match in self.__handlers:
            if glob.fnmatch.fnmatch(filename, match):
                return self.__handlers[match]

    def cmd_open_new_file(self):
        new_buffer = buffer.TemporaryBuffer("", "new_file")
        new_buffer.boss = self.boss
        new_buffer.handler = None
        self.cmd_add_buffer(new_buffer)
        self.__set_current_buffer(new_buffer)
        self.boss.command('editor', 'open-file',
                          filename=new_buffer.filename)

    def cmd_add_buffer(self, buffer):
        self.__add_buffer(buffer)
        self.__set_current_buffer(buffer)

    def cmd_close_current_file(self):
        if self.__currentbuffer.filename in self.__buffers:
            del self.__buffers[self.__currentbuffer.filename]
            self.__view.bufferview.set_bufferlist(self.__buffers)

    def cmd_close_file(self, filename):
        if filename in self.__buffers:
            del self.__buffers[filename]
            self.__view.bufferview.set_bufferlist(self.__buffers)
            def delayed_select():
                if not self.__view.bufferview.selected:
                    for name in self.__buffers:
                        self.__view.bufferview.set_selected(name)
                        break
                self.__currentbuffer = self.__view.selected.value
            gobject.timeout_add(500, delayed_select)

    def cmd_register_file_handler(self, filetype, handler):
        self.__handlers[filetype] = handler

    def cmd_rename_buffer(self, buffer, filename):
        if buffer.filename in self.__buffers:
            try:
                self.cmd_close_file(buffer.filename)
                os.rename(buffer.filename, filename)
                self.cmd_open_file(filename)
            except OSError:
                raise
            
    def cmd_reset_current_buffer(self):
        if self.__currentbuffer.poll():
            self.emit_event('buffer-modified')

    def evt_editor_started(self):
        #if len(self.__buffers):
        #    for buf in self.__buffers:
        #        self.boss.command('editor', 'open-file',
        #            filename=buf.filename)
        #        self.__view.set_currentbuffer(buf)
        #else:
        return #self.cmd_open_new_file()

    def evt_editor_file_opened(self, filename):
        #self.cmd_open_file(filename)
        pass

    def evt_editor_current_file_closed(self):
        return
        self.cmd_close_current_file()

    def __get_view(self):
        return self.__view
    view = property(__get_view)



Service = Buffermanager

if __name__ == '__main__':
    pass

