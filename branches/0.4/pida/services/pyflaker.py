# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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

import textwrap

import gobject

import pida.pidagtk.tree as tree
import pida.core.service as service
import pida.core.actions as actions
from pida.utils.kiwiutils import gsignal
import pida.pidagtk.contentview as contentview
from pida.utils.glinereader import GobjectReader

defs = service.definitions

from pida.model import attrtypes as types

READER_PYFLAKES = 0
READER_PYCHECKER = 1
READER_PYLINT = 2
READER_ERROR = -1

READER_NAMES = {
    READER_PYCHECKER: '<b><span color="#903030">C</span></b>',
    READER_PYLINT: '<b><span color="#309030">L</span></b>',
    READER_PYFLAKES: '<b><span color="#303090">F</span></b>',
    READER_ERROR: '<b><span color="#903030">E</span></b>'
    }

import gtk
import gobject

class Message(object):

    def __init__(self, data, checker):
        linfo, data = data.split(' ', 1)
        if '[' in data:
            dataitems = data.split()
            data = ' '.join([d for d in dataitems if
                     not(d.endswith(']') or d.startswith('['))])
        self.data = '\n'.join(textwrap.wrap(data, 35))
        fn, ln, nothing = linfo.split(':')
        self.linenumber = int(ln)
        if self.linenumber == 0:
            self.linenumber = 1
        self.key = data
        self.checker = READER_NAMES[checker]
    

class ErrorReader(gobject.GObject):

    gsignal('started')

    gsignal('data', gobject.TYPE_PYOBJECT)

    def __init__(self):
        super(ErrorReader, self).__init__()
        self._readers = {}
        for name in [READER_PYFLAKES, READER_PYLINT, READER_PYCHECKER]:
            self._readers[name] = GobjectReader()
            self._readers[name].connect('data', self.cb_data, name)
    
    def run(self, filename, readers):
        self.stop_reader(READER_PYFLAKES)
        self.stop_reader(READER_PYLINT)
        self.stop_reader(READER_PYCHECKER)
        self.emit('started')
        if READER_PYFLAKES in readers:
            self.run_flakes(filename)
        if READER_PYLINT in readers:
            self.run_lint(filename)
        if READER_PYCHECKER in readers:
            self.run_checker(filename)

    def run_flakes(self, filename):
        try:
            self._readers[READER_PYFLAKES].run('pyflakes', filename)
        except OSError:
            pass

    def run_lint(self, filename):
        try:
            self._readers[READER_PYLINT].run('pylint', '--parseable=y',
                                             '-r', 'n', filename)
        except OSError:
            pass

    def run_checker(self, filename):
        try:
            self._readers[READER_PYCHECKER].run('pychecker', '-Q', '-q',
            '--blacklist="Tkinter,wxPython,gtk,GTK,GDK,wx,_gobject,gobject"',
            '-a', '-I', '-8', '-1', filename)
        except OSError:
            pass

    def stop_reader(self, name):
        self._readers[name].stop()

    def cb_data(self, reader, data, name):
        m = Message(data, name)
        self.emit('data', m)


class MultiSubprocesslist(tree.Tree):

    SORT_AVAILABLE = [('Line number', 'linenumber')]
    SORT_CONTROLS = True

    def __init__(self, readerbut):
        super(MultiSubprocesslist, self).__init__()
        self.set_property('markup-format-string',
                          '<tt>%(checker)s '
                          '%(linenumber)s </tt>%(data)s')
        self.view.set_expander_column(self.view.get_column(1))


class pyflake_view(contentview.content_view):

    ICON_NAME = 'gtk-info'

    HAS_CONTROL_BOX = True

    LONG_TITLE = 'Python errors'
    SHORT_TITLE = 'Py Errors'

    def init(self):
        refbut = gtk.ToolButton(stock_id=gtk.STOCK_REFRESH)
        self.toolbar.insert(gtk.SeparatorToolItem(), 1)
        self.toolbar.insert(refbut, 1)
        self.__list = MultiSubprocesslist(refbut)
        self.__list.connect('double-clicked', self.cb_source_clicked)
        self.widget.pack_start(self.__list)
        hb = gtk.HBox()
        self._lint = gtk.CheckButton(label="Pylint")
        hb.pack_start(self._lint, expand=True)
        self._lint.set_active(self.service.opt('checkers', 'pylint'))
        self._flakes = gtk.CheckButton(label='Pyflakes')
        hb.pack_start(self._flakes, expand=True)
        self._flakes.set_active(self.service.opt('checkers', 'pyflakes'))
        self._checker = gtk.CheckButton(label="Pychecker")
        hb.pack_start(self._checker, expand=True)
        self._checker.set_active(self.service.opt('checkers', 'pychecker'))
        self.widget.pack_start(hb, expand=False)
        def _a(but):
            self.service.call('check_current_document')
        refbut.connect('clicked', _a)
        self._reader = ErrorReader()
        self._reader.connect('data', self.cb_message)
        self._reader.connect('started', self.cb_started)

    def check(self, filename, uncache=False):
        self._reader.run(filename, self.get_active_readers())

    def get_active_readers(self):
        readers = []
        if self._flakes.get_active():
            readers.append(READER_PYFLAKES)
        if self._lint.get_active():
            readers.append(READER_PYLINT)
        if self._checker.get_active():
            readers.append(READER_PYCHECKER)
        return readers
    
    def error(self, msg):
        self.__list.clear()
        fakedata = '0:-1: <span color="#903030"><b>%s</b></span>' % msg
        self.__list.add_item(self.__list.make_item(fakedata, -1))

    def cb_source_clicked(self, treeview, item):
        self.service.boss.call_command('editormanager', 'goto_line',
                                        linenumber=item.value.linenumber)

    def cb_message(self, reader, message):
        self.__list.add_item(message)

    def cb_started(self, reader):
        self.__list.clear()


class PyflakeConfig:
    __order__ = ['checkers']
    class checkers(defs.optiongroup):
        """Applications used to check python code."""
        __order__ = ['pylint', 'pychecker', 'pyflakes']
        class pylint(defs.option):
            """Use Pylint to check."""
            rtype = types.boolean
            default = False
        class pychecker(defs.option):
            """Use Pychecker to check."""
            rtype = types.boolean
            default = False
        class pyflakes(defs.option):
            """Use Pyflakes to check."""
            rtype = types.boolean
            default = True
    __markup__ = lambda self: 'Python Error Checking'


class pyflaker(service.service):

    display_name = 'Python Error Checking'

    config_definition = PyflakeConfig

    class PyflakeView(defs.View):
        view_type = pyflake_view
        book_name = 'plugin'

    @actions.action(
        type=actions.TYPE_TOGGLE,
        label="Error Viewer",
        stock_id=gtk.STOCK_DIALOG_WARNING,
        )
    def act_show(self, action):
        if action.get_active():
            if self.__view is None:
                self.__view = self.create_view('PyflakeView')
                self.__view.show()
            else:
                self.__view.raise_page()
            self.cmd_check_current_document()
        else:
            if self.__view is not None:
                self.__view.close()

    def cmd_check_current_document(self):
        if self.__view is None:
            return
        if self._currentdocument is None:
            self.__view.error('There is no current file.')
        elif not self._currentdocument.filename.endswith('.py'):
            self.__view.error('Current file is not a python file.')
        else:
            self.call('check', document=self._currentdocument)

    def cmd_check(self, document, uncache=False):
        if self.__view is None:
            return
        self.__view.check(document.filename, uncache)

    def init(self):
        self.__view = None
        self._currentdocument = None

    def bnd_buffermanager_document_changed(self, document):
        self._currentdocument = document
        self.cmd_check_current_document()

    def get_plugin_view(self):
        return self.__view
    plugin_view = property(get_plugin_view)

    def view_closed(self, view):
        self.__view = None
        self.action_group.get_action('pyflaker+show').set_active(False)

    def bnd_buffermanager_document_modified(self, document):
        if self._currentdocument is document:
            self.cmd_check(document, uncache=True)

    def get_menu_definition(self):
        return """
                <menubar>
                    <menu action="base_python_menu" name="base_python">
                        <menuitem action="pyflaker+show" />
                    </menu>
                </menubar>
               """

def checkPath(filename):
    return check(file(filename).read(), filename)


Service = pyflaker

