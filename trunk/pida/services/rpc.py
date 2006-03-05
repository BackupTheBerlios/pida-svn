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

import sys
if sys.platform == "win32":
    raise ImportError("RPC is not compatible with win32")

import pida.core.service as service
from pida.utils.kiwiutils import gsignal
import gobject
import os

class rpc(service.service):


    def init(self):
        self.__pipename = os.path.join(self.boss.pida_home,
                                        'sockets',
                                        'pida.%s' % os.getpid())
        self.__pipe = None
        self.call('start')

    def cmd_start(self):
        self.__pipe = reactor(self.__pipename)
        self.__pipe.connect('received', self.cb_pipe_received)
        self.__pipe.start()
        
    def cmd_stop(self):
        self.stop()

    def cb_pipe_received(self, pipe, (address, command, args)):
        if len(args) == 0 and command:
            filename = command
            self.log.debug('remote file open %s', filename)
            self.__pipe.send(address, 'OK\1OK\0')
            self.boss.call_command('buffermanager', 'open_file',
                                   filename=filename)
        else:
            self.log.debug('remote ping from %s', address)
            self.__pipe.send(address, 'EEK\1EEK\0')
        self.call('start')

    def stop(self):
        self.__pipe.stop()

"""
A Symmetrical Unix Domain Socket UDP remote procedure protocol.
"""

# gobject import
import gobject

# system imports
import os
import socket

class reactor(gobject.GObject):

    gsignal('received', object)

    def __init__(self, localsocketfile):
        gobject.GObject.__init__(self)
        self.socketfile = localsocketfile
        self.__buffers = {}
         
    def start(self):
        if os.path.exists(self.socketfile):
            os.remove(self.socketfile)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.bind(self.socketfile)
        gobject.io_add_watch(self.socket, gobject.IO_IN, self.cb_read)
    
    def stop(self):
        os.unlink(self.socketfile)

    def cb_read(self, socket, condition):
        if condition == gobject.IO_IN:
            data, address = socket.recvfrom(6024)
            self.received_data(data, address)
        return True

    def send(self, address, data):
        self.socket.sendto(data, address)

    def local(self, address, command, *args):
        self.emit('received', [address, command, args])

    def remote(self, command, *args):
        commandstring = '%s\1%s\0' % (command, '\1'.join(args))
        self.send(commandstring)

    def received_data(self, data, address):
        buf = self.__buffers.setdefault(address, '')
        self.__buffers[address] = buf + data
        print self.__buffers
        self.process_data(address)

    def process_data(self, address):
        lines = self.__buffers[address].split('\0')
        self.__buffers[address] = lines.pop()
        for line in lines:
            self.received_line(line, address)

    def received_line(self, line, address):
        args = line.split('\1')
        command = args.pop(0)
        self.local(address, command, *args)

gobject.type_register(reactor)

Service = rpc
