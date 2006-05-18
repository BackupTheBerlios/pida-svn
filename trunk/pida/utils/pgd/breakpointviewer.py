# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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
import gobject

from components import PGDSlaveDelegate

from tree import Tree

class Breakpoint(object):
    
    def __init__(self, index, filename, linenumber):
        self.key = index
        self.filename = filename
        self.linenumber = linenumber
        self.enabled = True

    def get_color(self):
        if self.enabled:
            return '#000000'
        else:
            return '#a0a0a0'

    def get_disabled_text(self):
        if self.enabled:
            return ''
        else:
            return '(disabled)'

    disabled_text = property(get_disabled_text)
    
    color = property(get_color)

class BreakpointViewer(PGDSlaveDelegate):

    def attach_slaves(self):
        self.main_window.attach_slave('breaks_holder', self)
        self.show_all()

    def update_bp(self, action, index, indices, filename, linenumber):
        mod = self.tree.model
        if action == 'set':
            gen = self._get_all_bps([index])
            try:
                index, val = gen.next()
                val.filename = filename
                val.linenumber = linenumber
                val.reset_markup()
            except StopIteration:
                bp = Breakpoint(index, filename, linenumber)
                self.tree.add_item(bp)
                #self.app.source.set_breakpoint(index, filename, linenumber)
        elif action == 'remove':
            for i, row in self._get_all_index_rows(indices):
                val = row[1].value
                filename = val.filename
                #self.app.source.remove_breakpoint(i, filename)
                mod.remove(row.iter)
        elif action == 'disable':
            for i, value in self._get_all_bps(indices):
                value.enabled = False
                value.reset_markup()
        elif action == 'enable':
            for i, value in self._get_all_bps(indices):
                value.enabled = True
                value.reset_markup()

    def create_toplevel_widget(self):
        vb = gtk.VBox()
        t = self.add_widget('tree', Tree())
        t.set_property('markup-format-string',
                       '<b>[%(key)s]</b>'
                       '<span color="%(color)s">'
                       '<tt> %(filename)s:%(linenumber)s </tt>'
                       '</span><i>%(disabled_text)s</i>')
        vb.pack_start(t)
        self._create_actions()
        return vb

    def _create_actions(self):
        self._current = None
        self.add_widget('dis_act', gtk.Action('Disable', 'Disable',
            'Disable this breakpoint', gtk.STOCK_NO))
        self.add_widget('en_act', gtk.Action('Enable', 'Enable',
            'Enable this breakpoint', gtk.STOCK_YES))

    def _create_popup(self, bp, event):
        self._current = bp
        if not bp: return
        menu = gtk.Menu()
        mi = self.dis_act.create_menu_item()
        menu.add(mi)
        self.dis_act.set_sensitive(bp.enabled)
        mi = self.en_act.create_menu_item()
        menu.add(mi)
        self.en_act.set_sensitive(not bp.enabled)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)

    def _get_all_index_rows(self, indices):
        mod = self.tree.model
        for index in indices:
            for row in mod:
                if row[0] == str(index):
                    yield index, row
        
    def _get_all_bps(self, indices):
        for index, row in self._get_all_index_rows(indices):
            value = row[1].value
            yield index, value

    def _set_breakpoint_enabled_status(self, bp, enabled):
        if not enabled:
            func = self.session_manager.disable_breakpoint
        else:
            func = self.session_manager.enable_breakpoint
        gobject.idle_add(func, [bp.key], False)

    def on_tree__double_clicked(self, tv, item):
        if item:
            val = item.value
            self._set_breakpoint_enabled_status(val, not val.enabled)

    def on_tree__right_clicked(self, tv, item, event):
        if item is None:
            val = item
        else:
            val = item.value
        self._create_popup(val, event)
        
    def on_dis_act__activate(self, action):
        print 'disabled'
        self._set_breakpoint_enabled_status(self._current, False)

    def on_en_act__activate(self, action):
        self._set_breakpoint_enabled_status(self._current, True)

