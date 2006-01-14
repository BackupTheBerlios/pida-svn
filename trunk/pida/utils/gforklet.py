import os
import sys
import xml.sax
import cPickle as pickle

import gtk
import gobject


parser = xml.sax.make_parser()
import cgi

 
class parameter_handler(xml.sax.handler.ContentHandler):

    def __init__(self, received_callback):
        self.__current = None
        self.__finished = False
        self.__readbuf = ''
        self.__received = received_callback
     
    def startElement(self, name, attributes):
        if name == 'param':
            self.__current = attributes['name']
 
    def characters(self, data):
        self.__readbuf += data
 
    def endElement(self, name):
        if name == 'param':
            self.__received_parameter(self.__readbuf)
            self.__readbuf = ''
            self.__current = None
        elif name == 'result':
            self.__finished = True

    def __received_parameter(self, readbuf):
        def _received():
            item = pickle.loads(str(readbuf))
            self.__received(item)
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
    handler = parameter_handler(read_callback)
    parser.setContentHandler(handler)
    parser.reset()
    def _read(fd, cond):
        data = os.read(fd, 1024)
        parser.feed(data)
        return not handler.is_finished
    readfd, writefd = os.pipe()
    gobject.io_add_watch(readfd, gobject.IO_IN, _read)
    pid = os.fork()
    if pid == 0:
        close_fds(readfd, writefd)
        os.write(writefd, '<result>')
        for item in f(*fargs):
            item_mu = ('<param name="a">%s</param>' %
                            pickle.dumps(item))
            os.write(writefd, item_mu)
        os.write(writefd, '</result>')
        os.close(readfd)
        os.close(writefd)
        os._exit(0)

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

