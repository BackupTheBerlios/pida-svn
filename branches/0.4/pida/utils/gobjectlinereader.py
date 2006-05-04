# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

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

import subprocess
import os
import gobject
import pida.pidagtk.tree as tree

from kiwiutils import gsignal, gproperty

import gprocess


class GobjectReader(gobject.GObject):
    """Read from a sub process."""

    gsignal('started')

    gsignal('finished', gobject.TYPE_PYOBJECT)

    gsignal('data', str)

    gsignal('status-data', str)

    def __init__(self):
        self.__watch = None
        self.procs = []
        self.pid = None
        super(GobjectReader, self).__init__()

    # public interface

    def run(self, *args):
        """Run a process by adding it to the queue.

        Start executing the queue if it is the only task.
        @var *args: command line arguments to be executed
        """
        self.procs.append(args)
        if len(self.procs) == 1:
            self._run_if_queue()

    def stop(self):
        if self.proc is not None:
            self.proc.stop()

    # private interface

    def _run_if_queue(self):
        if len(self.procs):
            self.emit('started')
            self._spawn_process(self.procs[0])

    def _spawn_process(self, args):
        self.data = ""
        self.proc = proc = gprocess.GProcess(args)
        proc.connect("stdout-data", self.on_received)
        proc.connect("finished", self.on_finished)
        proc.connect("started", self.on_started)
        proc.start()

    # signal callbacks

    def on_received(self, proc, data):
        self.data += data
        try:
            data, self.data = self.data.rsplit("\n", 1)
        except ValueError:
            # in this case there is no EOL, we just need to try again
            return
        for chunk in data.split("\n"):
            chunk = chunk.strip()
            if len(chunk) > 0:
                self.emit('data', chunk)

    def on_started(self, proc, pid):
        self.pid = pid
        self.emit('started')

    def on_finished(self, proc, retcode):
        args = self.procs.pop(0)
        self.emit('finished', args)
        self._run_if_queue()


class PkgresourcesReader(GobjectReader):

    def __init__(self, scriptname):
        import pkg_resources
        self.scriptpath = pkg_resources.resource_filename(
                'pida',
                'data/forkscripts/%s' % scriptname)
        super(PkgresourcesReader, self).__init__()

    def run(self, *args):
        args = ['python', self.scriptpath] + list(args)
        super(PkgresourcesReader, self).run(*args)

gobject.type_register(GobjectReader)

class Subprocesslist(tree.Tree):

    def __init__(self):
        self._reader = GobjectReader()
        self._reader.connect('started', self.cb_started)
        self._reader.connect('finished', self.cb_finished)
        self._reader.connect('data', self.cb_data)
        super(Subprocesslist, self).__init__()

    def run(self, *args):
        self._reader.run(*args)

    def make_item(self, data):
        """For overriding"""
        class Item:
            key = data
        return Item()

    def cb_data(self, reader, data):
        def _a(data):
            self.add_item(self.make_item(data))
        gobject.idle_add(_a, data)

    def cb_started(self, reader):
        self.clear()

    def cb_finished(self, reader, currargs):
        pass



def main():
    import gtk
    w = gtk.Window()
    t = Subprocesslist()
    w.add(t)
    w.show_all()
    t.run('pylint', '-r', 'n', 'gobjectlinereader.py')
    gtk.main()

if __name__ == '__main__':
    main()



