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

import cgi

from components import PGDSlaveDelegate
from mainwindow import NiceNotebook
from tree import IconTree
from icons import icons

type_icons = {
    'str': icons.get('nsstring', 16),
    'type': icons.get('nsclass', 16),
    'other': icons.get('nsother', 16),
    'int': icons.get('nsint', 16),
    'float': icons.get('nsfloat', 16),
    'list': icons.get('nslist', 16),
    'tuple': icons.get('nstuple', 16),
    'dict': icons.get('nsdict', 16),
    'NoneType': icons.get('nsnone', 16),
    'module': icons.get('nsmodule', 16),
    'bool': icons.get('nsbool', 16),
    'builtin_function_or_method': icons.get('nsfunc', 16),
    'function': icons.get('nsfunc', 16)
    }

nochildren = ['NoneType', 'str', 'int', 'float', 'long', 'bool']
            
reprable = nochildren + ['dict', 'list', 'tuple']
    

def get_pixbuf(nstype):
    if nstype not in type_icons:
        nstype = 'other'
    return type_icons[nstype]

class NamespaceItem(object):

    def __init__(self, nsdict):
        self.name = nsdict['name']
        self.stype = nsdict['type']
        self.srepr = nsdict['repr']
        self.expr = nsdict['expr']
        self.n_subnodes = nsdict['n_subnodes']
        self.key = self.name
        self.is_value = False
    
    def get_markup(self):
        if self.is_value:
            self.name = '.'
            mu = cgi.escape(self.srepr)
        else:
            n = cgi.escape(self.name)
            t = cgi.escape(self.stype)
            mu = ('<tt><b>%s</b>  </tt>'
                  '<span color="#903030"><i><small>%s</small></i></span>'
                  % (n, t))
            if self.stype in reprable:
                v = '<tt> %s</tt>' % cgi.escape(self.srepr)
                mu = ''.join([mu, v])
        return mu
    markup = property(get_markup)

    def get_pixbuf(self):
        if self.is_value:
            return None
        return get_pixbuf(self.stype)
    pixbuf = property(get_pixbuf)

class NamespaceTree(IconTree):

    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Name', 'name'),
                      ('Type', 'stype')]


class NamespaceViewer(PGDSlaveDelegate):

    def create_toplevel_widget(self):
        toplevel = gtk.VBox()
        t = self.add_widget('tree', NamespaceTree())
        t.set_property('markup-format-string', '%(markup)s')
        toplevel.pack_start(t)
        v = self.add_widget('tree_view', t.view)
        return toplevel

    def update_namespace(self, expr=None, parent=None):
        if expr is None:
            expr = self.get_root_expr()
            parent = None
            self.tree.clear()
        el = [(expr, True)]
        filt = None
        ns = self.session_manager.get_namespace(el, filt)
        for sn in ns[0]['subnodes']:
            item = NamespaceItem(sn)
            piter = self.tree.add_item(item, parent=parent)
            if item.stype not in nochildren:
                valitem = NamespaceItem(sn)
                valitem.is_value = True
                self.tree.add_item(valitem, parent=piter)

    def on_tree_view__row_expanded(self, tv, titer, path):
        value = self.tree.get(titer, 1).value
        if self.tree.model.iter_n_children(titer) == 1:
            self.update_namespace(value.expr, titer)

    def get_root_expr(self):
        raise NotImplementedError


class GlobalsViewer(NamespaceViewer):

    def get_root_expr(self):
        return 'globals()'

    def attach_slaves(self):
        self.main_window.attach_slave('globals_holder', self)
        self.show_all()


class LocalsViewer(NamespaceViewer):

    def get_root_expr(self):
        return 'locals()'
        
    def attach_slaves(self):
        self.main_window.attach_slave('locals_holder', self)
        self.show_all()


class AllNamespaceViewer(PGDSlaveDelegate):

    def create_toplevel_widget(self):
        #self.local_viewer = LocalViewer(self.app)
        #self.global_viewer = GlobalViewer(self.app)
        tl = gtk.VBox()
        nb = NiceNotebook()
        tl.pack_start(nb)
        nb.set_tab_pos(gtk.POS_TOP)
        lh = self.add_widget('globals_holder', gtk.EventBox())
        tl1 = self._create_big_label('globals()')
        nb.append_page(lh, tab_label=tl1)
        gh = self.add_widget('locals_holder', gtk.EventBox())
        tl2 = self._create_big_label('locals()')
        nb.append_page(gh, tab_label=tl2)
        return tl

    def _create_big_label(self, text):
        l = gtk.Label(text)
        return l

    def attach_slaves(self):
        #self.attach_slave('globals_holder', self.global_viewer)
        #self.attach_slave('locals_holder', self.local_viewer)
        #self.main_window.attach_slave('ns_holder', self)
        self.show_all()

    def update_namespace(self):
        self.local_viewer.update_namespace()
        self.global_viewer.update_namespace()


