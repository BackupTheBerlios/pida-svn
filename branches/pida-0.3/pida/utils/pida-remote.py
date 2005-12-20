#! /usr/bin/python
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



import pida.services.rpc as rpc

import tempfile
import os
import sys

class client_reactor(rpc.reactor):
    
    def __init__(self, serverfile):
        self.__serverfile = serverfile
        f, tempname = tempfile.mkstemp()
        os.close(f)
        os.unlink(tempname)
        rpc.reactor.__init__(self, tempname)

    def do_single_command(self, line):
        self.start()
        self.send(line)
        self.stop()
        
    def send(self, line):
        mangled = self.__mangle(line)
        rpc.reactor.send(self, self.__serverfile, mangled)

    def __mangle(self, line):
        return line.strip().replace(' ', '\1') + '\0'
        
import gtk

def main():
    socdir = os.path.join(os.path.expanduser('~'), '.pida2', 'sockets')
    def reply(reactor, (address, command, args)):
        if command != 'OK':
            print command
        gtk.main_quit()
    for f in os.listdir(socdir):
        path = os.path.join(socdir, f)
        c = client_reactor(path)
        cid = c.connect('received', reply)
        try:
            c.do_single_command(' '.join(sys.argv[1:]))
            gtk.main()
        except Exception, e:
            print path, e
            os.unlink(path)
            c.disconnect(cid)
            continue

if __name__ == '__main__':
    main()
