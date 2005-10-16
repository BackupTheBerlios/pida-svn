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

import gtk
#import tree
import os
import gobject

import pida.core.plugin as plugin
import pida.pidagtk.tree as tree

try:
    import bike
    from bike.parsing import fastparser
except ImportError:
    bike = fastparser = None
    print ('Python refactring functionality is not available. '
           'If you wish to use these features please install '
           'bicycle repair man (eg "apt-get install bicyclerepair").')

brmctx = None

def brm():
    global brmctx
    if not brmctx:
        brmctx = bike.init().brmctx
    return brmctx

class DefTree(tree.Tree):
    pass

class DefItem(tree.TreeItem):

    def __get_markup(self):
        el = self.value
        mu = ('<span size="small"><span%s><b><i>%s</i></b></span>  '
              '<tt><b>%s</b>\n'
              '  %s</tt></span>')
        name = el.name
        typl = el.type[0].lower()
        col = ''
        col = ' foreground="#0000c0"'
        fl = el.getLine(0).strip().split(' ', 1)[-1].replace(name, '', 1)
        return mu % (col, typl, name, fl)
    markup = property(__get_markup)

class PythonView(plugin.PluginView):
    
    def populate(self):
        vp = gtk.VPaned()
        self.pack_start(vp)
        self.defs = DefTree()
        defbox = gtk.VBox()
        sb = gtk.HBox()
        defbox.pack_start(self.defs)
        defbox.pack_start(sb, expand=False)
        #sortlabel = gtk.Label('Sort')
        #sb.pack_start(sortlabel, expand=False, padding=4)
        #self.sortbox = gtk.combo_box_new_text()
        #self.sortbox.connect('changed', self.cb_sort_changed)
        #self.sortbox.append_text('Name')
        #self.sortbox.append_text('Line number')
        #sb.pack_start(self.sortbox)
        #self.sortascending = gtk.CheckButton(label="asc")
        #self.sortascending.set_active(True)
        #self.sortascending.connect('toggled', self.cb_sort_changed)
        #sb.pack_start(self.sortascending)
        #self.sortbox.set_active(1)
        vp.pack1(defbox, resize=True, shrink=True)

    def refresh_definition(self, nodes):
        self.defs.clear()
        self.set_definitions(nodes)

    def set_definitions(self, nodes, parent=None):
        for node in nodes:
            i = DefItem(node.name, node)
            node.col = node.getLine(0).index(node.name)
            meparent = self.defs.add_item(i, parent)
            self.set_definitions(node.getChildNodes(), meparent)


class Python(plugin.Plugin):
    NAME = 'python'
    ICON = 'python'
    VIEW = PythonView

    BINDINGS = [('buffermanager', 'file-opened'),]

        #self.refwin = RefWin()
        #vp.pack2(self.refwin.win, resize=True, shrink=True)

        #self.refs = self.refwin.tree
        
        #self.add_button('warning', self.cb_but_pydoc , 'Look up in Pydoc')
        #self.add_button('profile', self.cb_but_profile, 'Run in the Python profiler')
        #self.add_button('debug', self.cb_but_debug, 'Run in the Python debugger')
        #self.add_separator()
        #self.add_button('undo', self.cb_but_undo, 'Undo last refactoring')
        #self.add_button('rename', self.cb_but_rename, 'Rename class or method')
        #self.add_button('find', self.cb_but_references, 'List references.')

        #self.menu = gtkextra.PositionPopup('position')

        #self.refs.connect_rightclick(self.cb_refs_rclick)

    def get_references(self, label='References'):
        row, col = self.defs.selected(2), self.defs.selected(3)
        brmc = brm()
        if row and col:
            d = brmc.findReferencesByCoordinates(self.fn, int(row), int(col))
            self.refresh_refs(d, label)
        else:
            self.message('Please select a definition')

    def refresh_defs(self, fn):
        self.fn = fn
        f = open(fn)
        root = fastparser.fastparser(f.read())
        f.close()
        self.videfs.clear()
        self.defs.populate(root.getChildNodes())
   
    def refresh_refs(self, refs, label="References"):
        refs = [i for i in refs]
        self.refs.populate(refs)
        s = '%s: %s' % (label, len(refs))
        self.refwin.show(s)

    def execute(self):
        #py = self.prop_main_registry.commands.python.value()
        #dirn = os.path.split(self.fn)[0]
        #self.do_action('newterminal', '%s %s' % (py, self.fn), directory=dirn)
        self.do_action('command', 'python_execute', [self.fn])

    def evt_buffermanager_file_opened(self, buffer):
        root = fastparser.fastparser(buffer.string)
        self.view.set_definitions(root.getChildNodes())

    def cb_sort_changed(self, *args):
        order = self.sortbox.get_active()
        sortfield = 0
        if order == 1:
            sortfield = 2
        direction = gtk.SORT_DESCENDING
        if self.sortascending.get_active():
            direction = gtk.SORT_ASCENDING
        self.defs.model.set_sort_column_id(sortfield, direction)

    def cb_alternative(self):
        self.execute()
        
    def cb_but_pydoc(self, *args):
        def ans(text):
            self.evt_doc(text)
        self.question('Search Pydoc for:', ans)

    def cb_defs_select(self, tv):
        self.do_edit('gotoline', self.defs.selected(2))

    def cb_refs_select(self, tv):
        fn, line, col = [self.refs.selected(i) for i in [0, 2, 3]]
        if fn != self.fn:
            self.do_edit('openfile', fn)
        self.do_edit('gotoline', line)

    def cb_defs_rclick(self, ite, time):
        line = self.defs.get(ite, 2)
        self.menu.popup(self.fn, line, time)

    def cb_refs_rclick(self, ite, time):
        line = self.refs.get(ite, 2)
        self.menu.popup(self.fn, line, time)

    def cb_but_rename(self, *a):
        self.get_references(label='Renames')
        brmc = brm()
        def rename(name):
            row, col = self.defs.selected(2), self.defs.selected(3)
            brmc.renameByCoordinates(self.fn, int(row), int(col), name)
            brmc.save()
            self.refresh_defs(self.fn)
        self.question('Name to rename to?', rename)

    def cb_but_references(self, *a):
        self.get_references()

    def cb_but_undo(self, *args):
        brmc = brm()
        brmc.undo()
        brmc.save()
        self.refresh_defs(self.fn)

    def evt_bufferchange(self, nr, name):
        self.fn = name
        if name.endswith('py') and os.path.exists(name):
            self.refresh_defs(name)
        else:
            self.defs.model.clear()

    def evt_bufferexecute(self, *args):
        self.execute()

    def evt_started(self, *args):
        brm()
        self.refwin.hide()

    def evt_doc(self, text):
        pydoc = self.prop_main_registry.commands.pydoc.value()
        self.do_action('newterminal', '%s %s' % (pydoc, text))

    def evt_reset(self):
        py = self.prop_main_registry.commands.python.value()

        self.do_action('register_external_command',
                       'python_execute',
                       '%s %%s' % py, 1, ['file name'], 'execute')

        self.do_action('register_external_command',
                       'python_shell',
                       py, 0, [], 'python')
       
Plugin = Python

