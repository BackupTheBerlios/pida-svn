
import gtk
import gobject
import socket
import os

class Server(object):

    def __init__(self, localsocketfile, remotesocketfile):
        self.reactor = DummyCB()
        self.socketfile = localsocketfile
        self.remote_socketfile = remotesocketfile
        self.read_buffer = ''
         
    def start(self):
        if os.path.exists(self.socketfile):
            os.remove(self.socketfile)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.bind(self.socketfile)
        gobject.io_add_watch(self.socket, gobject.IO_IN, self.cb_read)
    
    def stop(self):
        gtk.main_quit()

    def cb_read(self, socket, condition):
        if condition == gobject.IO_IN:
            data, address = socket.recvfrom(6024)
            self.received_data(data)

    def send(self, data):
        print 'sending'
        self.socket.sendto(data, self.remote_socketfile)

    def local(self, command, *args):
        commandname = 'do_%s' % command
        if hasattr(self.reactor, commandname):
            print command, args
            getattr(self.reactor, commandname)(*args)

    def remote(self, command, *args):
        commandstring = '%s\1%s\0' % (command, '\1'.join(args))
        self.send(commandstring)

    def received_data(self, data):
        self.read_buffer = '%s%s' % (self.read_buffer, data)
        self.process_data()

    def process_data(self):
        lines = self.read_buffer.split('\0')
        self.read_buf = lines.pop()
        for line in lines:
            self.received_line(line)

    def received_line(self, line):
        args = line.split('\1')
        command = args.pop(0)
        self.local(command, *args)




class DummyCB(object):

    def do_hello(self, *args):
        print args

if __name__ == '__main__':
    s = Server('/home/ali/socket', '/home/ali/csocket')
    s.start()
    gtk.main()
