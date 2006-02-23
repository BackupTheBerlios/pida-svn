
import os
import sys
import pickle
import threading

# not sure why this is necessary for some distributions
import pkg_resources
pkg_resources.require("pida")

import pida.utils.vc as vc

class Lister(object):

    def __init__(self):
        self._list_lock = threading.Lock()
        self._print_lock = threading.Lock()
        self._list_queue = []

    def ls(self, directory):
        self._list_lock.acquire()
        def _t():
            self.plain_ls(directory)
        p = threading.Thread(target=_t)
        def _t():
            self.status_ls(directory)
        s = threading.Thread(target=_t)
        s.start()
        p.start()
        self._list_lock.release()

    def plain_ls(self, directory):
        for name in os.listdir(directory):
            self._print_lock.acquire()
            print '<p>', os.path.join(directory, name)
            self._print_lock.release()

    def status_ls(self, directory):
        os.chdir(directory)
        vcdir = vc.Vc(directory)
        if vcdir.NAME == 'Null':
            print '<s> <s> <s>'
        else:
            statuses = vcdir.listdir(directory)
            for status in statuses:
                self._print_lock.acquire()
                print '<s>', status.state, status.path
                self._print_lock.release()
            sys.exit(0)

if __name__ == '__main__':
    directory = sys.argv.pop()
    l = Lister()
    l.ls(directory)
