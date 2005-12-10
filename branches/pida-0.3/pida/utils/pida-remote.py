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



from twisted.spread import pb
from twisted.internet import reactor
from twisted.python import util

#factory = pb.PBClientFactory()
#reactor.connectTCP("localhost", 8781, factory)
#d = factory.getRootObject()
#d.addCallback(lambda object: object.callRemote("command", "terminal",
#              "execute-py-shell", {}))
#d.addCallback(lambda echo: 'server echoed: '+echo)
#d.addErrback(lambda reason: 'error: '+str(reason.value))
#d.addCallback(util.println)
#d.addCallback(lambda _: reactor.stop())
#reactor.run()

import cmd

import twisted.python.log as log
import sys
#log.startLogging(sys.stdout)

class PidaRemote(cmd.Cmd):

    def do_cmd(self, args):
        args = args.split()
        if len(args) < 2:
            print "command <servicename> <command> [args]"
            return
        else:
            servicename = args[0]
            commandname = args[1]
            kwdict = {}
            for arg in args[2:]:
                keyval = args.split('=')
                if len(keyval != 2):
                    print "command <servicename> <command> [args]"
                    return
                else:
                    kwdict[keyva[0]] = keyval[1]
            print self.remote_call(servicename, commandname, kwdict)
                    

    def remote_call(self, servicename, name, kwdict):
        socket_file = '/home/ali/.pida2/sockets/pida-rpc'
        factory = pb.PBClientFactory()
        reactor.connectUNIX(socket_file, factory)
        d = factory.getRootObject()
        d.addCallback(lambda object: object.callRemote("command",
                      servicename, name, kwdict))
        d.addCallback(lambda echo: '%s' % echo)
        d.addErrback(lambda reason: 'error: '+str(reason.value))
        #d.addCallback(util.println)
        d.addCallback(lambda _: reactor.stop())
        d.addErrback(lambda _: reactor.stop())
        reactor.run()
            

def main():
    
    c = PidaRemote()
    c.onecmd(raw_input())

    
    

if __name__ == '__main__':
    main()
