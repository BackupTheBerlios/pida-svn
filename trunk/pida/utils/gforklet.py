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

# system import(s)
import os
import sys
import xml.sax
import cPickle as pickle

import gtk
# gobject import(s)
import gobject



 
class parameter_handler(xml.sax.handler.ContentHandler):
    """Basic handler for result tree."""

    def __init__(self, received_callback):
        self.__current = None
        self.__finished = False
        self.__readbuf = ''
        self.__received = received_callback
     
    def startElement(self, name, attributes):
        if name == 'p':
            self.__current = True
 
    def characters(self, data):
        self.__readbuf += data
 
    def endElement(self, name):
        if name == 'p':
            self.__received_parameter(self.__readbuf)
            self.__readbuf = ''
            self.__current = None
        elif name == 'result':
            self.__finished = True

    def __received_parameter(self, readbuf):
        def _received():
            try:
                received_item = pickle.loads(str(readbuf))
                self.__received(received_item)
            except:
                pass
        gobject.idle_add(_received)

    def get_is_finished(self):
        return self.__finished
    is_finished = property(get_is_finished)


def close_fds(*excluding):
    for fd in xrange(3, 1024):
        if fd not in excluding:
            try:
                os.close(fd)
            except:
                pass


def fork_generator(f, fargs, read_callback):
    parser = xml.sax.make_parser()
    handler = parameter_handler(read_callback)
    parser.setContentHandler(handler)
    def _read(fd, cond):
        data = os.read(fd, 1024)
        try:
            parser.feed(data)
        except:
            return False
        if handler.is_finished:
            os.wait()
            return False
        else:
            return True
    readfd, writefd = os.pipe()
    gobject.io_add_watch(readfd, gobject.IO_IN, _read)
    pid = os.fork()
    if pid == 0:
        close_fds(readfd, writefd)
        os.write(writefd, '<result>')
        for item in f(*fargs):
            item_mu = ('<p>%s</p>' %
                            pickle.dumps(item))
            os.write(writefd, item_mu)
        os.write(writefd, '</result>')
        os.close(readfd)
        os.close(writefd)
        os._exit(0)
        sys.exit(0)
    else:
        return pid, readfd, parser
        


def fork(f, fargs, read_callback):
    def _call(*args):
        yield f(*args)
    fork_generator(_call, fargs, read_callback)
    

class dummy(object):

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class tester(gtk.Window):

    def __init__(self):
        super(tester, self).__init__()
        self.t = gtk.TextView()
        self.add(self.t)
        
        self.show_all()


        def read(i):
            
            b = self.t.get_buffer()
            b.insert(b.get_end_iter(), '%s\n' % i)
        
        def gen():
            for i in range(20):
                yield dummy(i, i, i)
        
        def mon():
            return dummy(1, 2, 3)

        fork(mon, [], read)
        #fork_generator(gen, [], read)

def test():
    t = tester()
    gtk.main()

