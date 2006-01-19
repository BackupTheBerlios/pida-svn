# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Bernard Pratz <bernard@pratz.net>

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
import time
from cgi import escape

class gtk_event_box(gtk.VBox):
    def __init__(self,record,custom=None,markup=None):
        gtk.VBox.__init__(self)
        self.set_homogeneous(False)
    
        self.__record = record
        self.__custom = custom
        self.__markup = markup
        empty = True
        
        print 'TITLE: %s ; MSG : %s ; TYPE : %s' % (record.title,
            record.getMessage(),record.type)
        
        if record.title != None:
            title = gtk.Label(record.title)
            self.pack_start(title,True,False)
        if record.message != None and record.type != 'log':
            label = gtk.Label(record.message)
            self.pack_start(label,True,True)
        if record.answered_value != None:
            self.pack_start(self._event_answered_question(),True,False)
        else:
            if hasattr(self,"_event_%s"%record.type):
                self.pack_start(getattr(self,"_event_%s"%record.type)(),
                                                                    True,False)
            else:   
                self.pack_start(self._event_log(),True,True)
                self.pack_start(
                    gtk.Label("Error unrecognized event: %s"%record.type))
        
        self.show()

    def _markup(self,item):
        return "<b>%s</b> <i>%s</i>\n%s %s:%s\n<b>%s</b>\n" % (
            item.levelname, escape(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(item.created))),
            item.name, item.module, item.lineno, escape(item.getMessage()))

    def __make_entry(self):
        self.__entry = gtk.Entry()
        if self.__record.prefill != None:
            self.__entry.set_text(self.__record.prefill)
        self.__entry.show()
        return self.__entry

    def __cb_true(self,but):
        self.__record.callback(True)

    def _event_yesno(self):
        bb = gtk.HButtonBox()
        bb.set_layout(gtk.BUTTONBOX_END)
        self.__but_yes = gtk.Button("Yes")
        def cb_yes_clicked(but):
            self.__record.callback(True)
            self.remove(bb)
            self.pack_start(self._event_answered_question())
        self.__but_yes.connect('clicked',cb_yes_clicked)
        self.__but_yes.show()
        bb.pack_start(self.__but_yes,True,False)
        self.__but_no = gtk.Button("No")
        def cb_no_clicked(but):
            self.__record.callback(False)
            self.remove(bb)
            self.pack_start(self._event_answered_question())
        self.__but_no.connect('clicked',cb_no_clicked)
        self.__but_no.show()
        bb.pack_start(self.__but_no,True,False)
        bb.show()
        return bb

    def _event_okcancel(self):
        bb = gtk.HButtonBox()
        bb.set_layout(gtk.BUTTONBOX_END)
        self.__but_ok = gtk.Button("Ok")
        def cb_ok_clicked(but):
            self.__record.callback(True)
            self.remove(bb)
            self.pack_start(self._event_answered_question())
        self.__but_ok.connect('clicked',cb_ok_clicked)
        self.__but_ok.show()
        bb.pack_start(self.__but_ok,True,False)
        self.__but_cancel = gtk.Button("Cancel")
        def cb_cancel_clicked(but):
            self.__record.callback(False)
            self.remove(bb)
            self.pack_start(self._event_answered_question())
        self.__but_cancel.connect('clicked',cb_cancel_clicked)
        self.__but_cancel.show()
        bb.pack_start(self.__but_cancel,True,False)
        bb.show()  
        return bb

    def _event_ok(self):
        bb = gtk.HButtonBox()
        bb.set_layout(gtk.BUTTONBOX_END)
        self.__but_ok = gtk.Button("Ok")
        def cb_ok_clicked(but):
            self.__record.callback(True)
            self.remove(bb)
            self.pack_start(self._event_answered_question())
        self.__but_ok.connect('clicked',cb_ok_clicked)
        self.__but_ok.show()
        bb.pack_start(self.__but_ok,True,False)
        bb.show()
        return bb

    def _event_entry_okcancel(self):
        vb = gtk.VBox()
        vb.pack_start(self.__make_entry(),True,False)
        vb.pack_start(self._event_okcancel(),True,False)
        def cb_ok_clicked(but):
            self.__record.callback(self.__entry.get_text())
            self.remove(vb)
            self.pack_start(self._event_answered_question())
        self.__but_ok.connect('clicked',cb_ok_clicked)
        def cb_cancel_clicked(but):
            self.__record.callback(None)
            self.remove(vb)
            self.pack_start(self._event_answered_question())
        self.__but_cancel.connect('clicked',cb_cancel_clicked)
        return vb

    def _event_entry_ok(self):
        vb = gtk.VBox()
        vb.pack_start(self.__make_entry(),True,False)
        vb.pack_start(self._event_ok(),True,False)
        def cb_ok_clicked(but):
            self.__record.callback(self.__entry.get_text())
            self.remove(vb)
            self.pack_start(self._event_answered_question())
        self.__but_ok.connect('clicked',cb_ok_clicked)
        return vb

    def _event_answered_question(self):
        vb = gtk.VBox()
        label = gtk.Label("And you answered '%s'."%self.__record.answered_value)
        label.show()
        vb.pack_start(label,True,True)
        vb.show()
        return vb

    def _event_log(self):
        vb = gtk.VBox()
        title = gtk.Label("%s log message" % self.__record.levelname)
        title.show()
        vb.pack_start(title,True,False)
        if self.__markup == None:
            label = gtk.Label(self._markup(self.__record))
        else:
            label = gtk.Label(self.__markup)
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.show()
        vb.pack_start(label,True,True)
        return vb

    def _event_custom(self):
        if self.__custom != None:
            return self.__custom

    def connect(self,action,callback):
        if hasattr(self,"__but_%s"%action):
            getattr(self,"__but_%s"%action).connect('clicked',callback)

