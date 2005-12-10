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
import pida.core.registry as registry
import os

SOCKETS_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "sockets")

class Service(service.Service):
    
    NAME = 'rpc'

    COMMANDS = [('start', []),
                ('build-listen-socket', [('listener', True),
                                         ('name', False)])]

    OPTIONS = [('start-automatically',
                'whether the rpc will start automatically.',
                True, registry.Boolean)]

    def populate(self):
        self.__sockets = {}
        self.start()

    def reset(self):
        pass

    def cmd_start(self):
        self.start()
    
    def start(self):
        self.cmd_build_listen_socket(RPCListener, 'pida-rpc')

    def close_socket(self, name, delete=True):
        if name in self.__sockets:
            self.__sockets[name].stopListening()
            if delete:
                # to prevent mutation while iterating
                del self.__sockets[name]

    def close_all(self):
        for socket in self.__sockets:
            self.close_socket(socket, delete=False)
        self.__sockets = {}

    def cmd_build_listen_socket(self, listener, name):
        self.close_socket(name)
        listener = RPCListener()
        listener.boss = self.boss
        socket_file = self.__generate_socketfile(name)
        l = reactor.listenUNIX(socket_file, pb.PBServerFactory(listener))
        self.__sockets[name] = l
        return socket_file

    def cmd_close_listen_socket(self, name):
        pass

    def __generate_socketfile(self, name):
        socket_file = os.path.join(SOCKETS_CONF, name)
        if os.path.exists(socket_file):
            return self.__generate_socketfile('%s~' % name)
        return socket_file

    def stop(self):
        self.close_all()
        
        

try:
    from twisted.spread import pb
    from twisted.internet import reactor
except ImportError:
    class dummypb(object):
        Root = object
    pb = dummypb

class RPCListener(pb.Root):
    def remote_command(self, group, command, kwargs):
        return self.boss.command(group, command, **kwargs)


