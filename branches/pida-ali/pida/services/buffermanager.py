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

import pida.core.service as service
import pida.pidagtk.buffertree as buffertree

class Buffermanager(service.Service):
    NAME = 'buffermanager'

    COMMANDS = [['open-file', [('filename', True)]],
                ['close-file', [('filename', True)]],
                ['close-current-file', []],
                ['get-bufferlist', []],
                ['get-currentbuffer', []]]

    EVENTS = ['file-opened']

    BINDINGS = [('editor', 'started'),
                ('editor', 'file-opened'),
                ('editor', 'current-file-closed')]
    
    def init(self):
        self.__currentbuffer = None
        self.__buffers = {}
        self.__view = buffertree.BufferTree()
        self.__view.connect('clicked', self.cb_view_clicked)

    def __stop_all_polling(self):
        for filename, buf in self.__buffers.iteritems():
            buf.stop_polling()

    def cb_view_clicked(self, view, bufitem):
        buf = bufitem.value
        if buf != self.__currentbuffer:
            #self.boss.command('editor', 'open-file', filename=buf.filename)
            self.__currentbuffer = buf
            self.__view.display_buffer(buf)
            self.emit_event('file-opened', buffer=self.__currentbuffer)

    def cmd_get_currentbuffer(self):
        return self.__currentbuffer

    def cmd_get_bufferlist(self):
        return self.__bufferlist

    def cmd_open_file(self, filename):
        if self.__currentbuffer is None or self.__currentbuffer.filename != filename:
            if not filename in self.__buffers:
                self.__buffers[filename] = buffer.Buffer(filename)
            self.__currentbuffer = self.__buffers[filename]
            self.__view.set_bufferlist(self.__buffers)
            self.__view.set_currentbuffer(filename)
            self.__view.display_buffer(self.__currentbuffer)
            self.__stop_all_polling()
            self.__currentbuffer.start_polling()
            self.emit_event('file-opened', buffer=self.__currentbuffer)
            return self.__currentbuffer

    def cmd_close_current_file(self):
        if self.__currentbuffer.filename in self.__buffers:
            del self.__buffers[self.__currentbuffer.filename]
            self.__view.set_bufferlist(self.__buffers)

    def cmd_close_file(self, filename):
        if filename in self.__buffers:
            del self.__buffers[filename]
            self.__view.set_bufferlist(self.__buffers)

    def evt_editor_started(self):
        for buf in self.__buffers:
            self.emit_event('file-opened', buffer=self.__buffers[buf])
            self.__view.set_currentbuffer(buf.filename)
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

