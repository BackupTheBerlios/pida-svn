# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: base.py 352 2005-07-14 00:16:02Z gcbirzan $
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
import os
import gtk
import pida.core.base as base
from pida.pidagtk.contentview import create_pida_icon

import distutils.spawn as spawn

im = gtk.Image()
im.set_from_pixbuf(create_pida_icon())

class IComponent(object):

    def get_sanity_errors(self):
        return None

class Vim(IComponent):
    LABEL = 'Vim'
    def get_sanity_errors(self):
        if spawn.find_executable('gvim'):
            return []
        else:
            return ['Gvim is not installed']

class Vimmulti(Vim):
    LABEL = 'Vim external'
        
class Culebra(IComponent):
    LABEL = 'Culebra'

    def get_sanity_errors(self):
        errors = []
        try:
            import rat
        except ImportError:
            errors.append('Rat is not installed')
        return errors

EDITORS = [Vim(), Vimmulti(), Culebra()]

class FirstTimeWindow(object):

    def __init__(self):
        self.win = gtk.Dialog(parent=None,
                              title='PIDA First Run Wizard',
                              buttons=(gtk.STOCK_QUIT, gtk.RESPONSE_REJECT,
                                       gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        hbox = gtk.HBox(spacing=12)
        hbox.set_border_width(12)
        self.win.vbox.pack_start(hbox)
        logo = gtk.Image()
        logofrm = gtk.Alignment(0, 0, 0.1, 0.1)
        logofrm.add(im)
        hbox.pack_start(logofrm, padding=8)
        box = gtk.VBox()
        hbox.pack_start(box, padding=8)
        s = ('It seems this is the first time '
            'you are running Pida.\n\n<b>Please select an editor:</b>')
        l = gtk.Label()
        l.set_markup(s)
        box.pack_start(l, expand=False, padding=8)
        self.radio = gtk.RadioButton()
        for editor in EDITORS:
            ebox = gtk.HBox(spacing=6)
            box.pack_start(ebox, expand=False, padding=4)
            radio = gtk.RadioButton(self.radio, label=editor.LABEL)
            ebox.pack_start(radio)
            cbox = gtk.VBox(spacing=3)
            label = gtk.Label()
            label.set_alignment(1, 0.5)
            cbox.pack_start(label)
            ebox.pack_start(cbox, padding=4, expand=False)
            sanitybut = gtk.Button(label='Check')
            ebox.pack_start(sanitybut, expand=False, padding=1)
            sanitybut.connect('clicked', self.cb_sanity, editor, radio, label)
            self.cb_sanity(sanitybut, editor, radio, label)
            errs =  editor.get_sanity_errors()
            self.radio = radio
        bbox = gtk.HBox()
        box.pack_start(bbox, expand=False, padding=4)

    def run(self, filename):
        self.win.show_all()
        response = self.win.run()
        self.win.hide_all()
        editor_name = self.get_editor_option()
        self.win.destroy()
        self.write_file(filename)
        return (response, editor_name)

    def cb_sanity(self, button, component, radio, label):
        errs =  component.get_sanity_errors()
        if errs:
            radio.set_sensitive(False)
            radio.set_active(False)
            s = '\n'.join(errs)
            label.set_markup('<span size="small" foreground="#c00000">'
                             '<i>%s</i></span>' % s)
        else:
            radio.set_sensitive(True)
            radio.set_active(True)
            label.set_markup('<span size="small" foreground="#00c000">'
                             '<i>Okay to use</i></span>')
            button.set_sensitive(False)
    
    def get_editor_option(self, *args):
        for radio in self.radio.get_group():
            if radio.get_active():
                editor = radio.get_label()
                return editor

    def write_file(self, filename):
        f = open(filename, 'w')
        f. write('#Remove this to rerun the start wizard\n\n')
        f.close()

if __name__ == '__main__':
    ftw = FirstTimeWindow()
    print ftw.run('/home/ali/.firstrun')

