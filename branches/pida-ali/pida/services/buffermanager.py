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
import buffer
import glob
import os
import pida.core.service as service
import pida.pidagtk.buffertree as buffertree

class Buffermanager(service.Service):
    NAME = 'buffermanager'

    COMMANDS = [['open-file', [('filename', True)]],
                ['close-file', [('filename', True)]],
                ['add-buffer', [('buffer', True)]],
                ['rename-buffer', [('buffer', True), ('filename', True)]],
                ['close-current-file', []],
                ['open-new-file', []],
                ['reset-current-buffer', []],
                ['get-bufferlist', []],
                ['register-file-handler', [('filetype', True), ('handler', True)]],
                ['get-currentbuffer', []]]

    EVENTS = ['file-opened', 'buffer-modified']

    BINDINGS = [('editor', 'started'),
                ('editor', 'file-opened'),
                ('editor', 'current-file-closed')]

    
    def init(self):
        self.__currentbuffer = None
        self.__buffers = {}
        self.__handlers = {}
        self.__view = buffertree.BufferTree()
        self.__view.connect('clicked', self.cb_view_clicked)

    def cb_view_clicked(self, view, bufitem):
        buf = bufitem.value
        if buf != self.__currentbuffer:
            #self.boss.command('editor', 'open-file', filename=buf.filename)
            self.cmd_open_file(buf.filename)

    def set_current_buffer(self, filename):
        self.__currentbuffer = self.__buffers[filename]
        self.__view.set_currentbuffer(filename)
        self.__view.display_buffer(self.__currentbuffer)

    def cmd_get_currentbuffer(self):
        return self.__currentbuffer

    def cmd_get_bufferlist(self):
        return self.__bufferlist

    def cmd_open_file(self, filename):
        assert(isinstance(filename, str))
        if self.__currentbuffer is None or self.__currentbuffer.filename != filename:
            matched = False
            for match in self.__handlers:
                print match, filename
                if glob.fnmatch.fnmatch(filename, match):
                    new_buffer = self.__handlers[match].open_file(filename)
                    matched = True
                    self.cmd_add_buffer(new_buffer)
                    break
            if not matched:
                if not filename in self.__buffers:
                    new_buffer = buffer.Buffer(filename)
                    self.cmd_add_buffer(new_buffer)
                    # replace with an editor command call?
                else:
                    self.set_current_buffer(filename)
                    new_buffer = self.__buffers[filename]
                self.emit_event('file-opened', buffer=new_buffer)
        return self.__currentbuffer

    def cmd_open_new_file(self):
        new_buffer = buffer.TemporaryBuffer("* ", "new file")
        self.cmd_add_buffer(new_buffer)
        self.set_current_buffer(new_buffer.file)
        self.emit_event('file-opened', buffer=new_buffer)

    def cmd_add_buffer(self, buffer):
        filename = buffer.filename
        self.__buffers[filename] = buffer
        self.__view.set_bufferlist(self.__buffers)
        self.set_current_buffer(filename)

    def cmd_close_current_file(self):
        if self.__currentbuffer.filename in self.__buffers:
            del self.__buffers[self.__currentbuffer.filename]
            self.__view.set_bufferlist(self.__buffers)

    def cmd_close_file(self, filename):
        if filename in self.__buffers:
            del self.__buffers[filename]
            self.__view.set_bufferlist(self.__buffers)

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
        if len(self.__buffers):
            for buf in self.__buffers:
                self.emit_event('file-opened', buffer=self.__buffers[buf])
                self.__view.set_currentbuffer(buf)
        else:
            self.cmd_open_new_file()

        #self.__view.set_selected(buf)

    def evt_editor_file_opened(self, filename):
        self.cmd_open_file(filename)

    def evt_editor_current_file_closed(self):
        return
        self.cmd_close_current_file()

    def __get_view(self):
        return self.__view
    view = property(__get_view)



Service = Buffermanager

if __name__ == '__main__':
    pass

