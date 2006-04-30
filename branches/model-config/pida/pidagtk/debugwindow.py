# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# Copyright (C) 2005 by Async Open Source and Sicem S.L.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gettext
import linecache
import os
import sys
import traceback
import urllib
import urllib2
import pango
import gtk
import sys
from rat import hig

_ = gettext.gettext

import pida.core.errors as errors

class DebugWindow(gtk.Dialog):

    application = None
    
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, 'An Error Occurred', parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR)

        self.send = self._create_button(gtk.STOCK_NETWORK, _('_Report bug ...'))
        self.send.connect('clicked', self._on_send__clicked)
        self.send.set_sensitive(False)
        self._build_ui()
        self.action_area.pack_end(self.send)

        
        quit = self._create_button(gtk.STOCK_OK, _('_Continue'))
        quit.connect('clicked', self._on_ok__clicked)
        self.action_area.pack_end(quit)
        
        self._pwd = os.getcwd()

    def _create_button(self, stock, text):
        b = gtk.Button()
        #a = gtk.Alignment(0.5, 0.5, 1.0, 1.0)
        h = gtk.HBox()
        #a.add(h)
        i = gtk.Image()
        i.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
        l = gtk.Label(text)
        if '_' in text:
            l.set_use_underline(True)

        h.pack_start(i)
        h.pack_start(l)
        b.add(h)
        b.show_all()
        return b
        
    def _build_ui(self):
        # 416 = 600 / sqrt(2) = golden number
        self.set_default_size(600, 416)
        self.set_border_width(12)

        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, False)
        self.vbox.set_spacing(6)
        lbl = gtk.Label('<b>Exception type:</b>')
        lbl.set_use_markup(True)
        hbox.pack_start(lbl, False, False, 6)
        lbl.show()
        self._info_label = gtk.Label()
        hbox.pack_start(self._info_label, False, False)
        self._info_label.show()
        hbox.show()

        self.notebook = gtk.Notebook()
        self.vbox.pack_start(self.notebook)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_IN)
        sw.show()
        
        self._buffer = gtk.TextBuffer()
        self._buffer.create_tag('filename', style=pango.STYLE_ITALIC, foreground='gray20')
        self._buffer.create_tag('name', foreground='#000055')
        self._buffer.create_tag('lineno', weight=pango.WEIGHT_BOLD)
        self._buffer.create_tag('exc', foreground='#880000', weight=pango.WEIGHT_BOLD)
        
        self._textview = gtk.TextView(self._buffer)
        self._textview.set_editable(False)
        self._textview.set_cursor_visible(False)
        sw.add(self._textview)
        self._textview.show()
        
        br = gtk.VBox()
        br.pack_start(sw)
        self.notebook.append_page(br, tab_label=gtk.Label("Exception"))
        
        exp = gtk.Expander(label='Bug report details')
        def _a(exp):
            self.send.set_sensitive(exp.get_expanded()) 
        exp.connect_after('activate', _a)
        br.pack_start(exp, expand=False)
        tb = gtk.VBox(spacing=6)
        exp.add(tb)
        sg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        h1 = gtk.HBox(spacing=12)
        tb.pack_start(h1, expand=False)
        l = gtk.Label('Title:')
        l.set_alignment(1, 0)
        sg.add_widget(l)
        h1.pack_start(l, expand=False, padding=6)
        self._ticketname = gtk.Entry()
        self._ticketname.set_has_frame(False)
        h1.pack_start(self._ticketname, padding=6)
        h1 = gtk.HBox(spacing=12)
        tb.pack_start(h1)
        l = gtk.Label('Description:')
        l.set_alignment(1, 0)
        sg.add_widget(l)
        h1.pack_start(l, expand=False, padding=6)
        self._ticketdesc = gtk.TextView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self._ticketdesc)
        h1.pack_start(sw, padding=6)
        self._ticketinclexc = gtk.CheckButton(
            label='Include exception traceback in report')
        tb.pack_start(self._ticketinclexc)
        self._ticketinclexc.set_active(True)
        
        
        self.notebook.show_all()

    def show_exception(self, exctype, value, tb):
        if exctype is errors.ServiceNotFoundError:
            svcname = value.args[0]
            pt = 'Tried to access non-existing service "%s"' % svcname
            st = ('PIDA tried to find a service that is not loaded'
                  '. Most likely this is due to a missing dependency'
                  '. Please check the file:\n\n'
                  '<tt>~/.pida/logs/pida.log</tt>')
            if svcname in ['window', 'buffermanager', 'contexts',
                         'editormanager']:
                st = ('%s\n\n<span color="#c03030">'
                      'The service "%s" is critical.</span>\n\n'
                      '<b>PIDA will not run without it</b>'
                      % (st, svcname))
                hig.error(pt, st, title='Service Not Found')
            else:
                hig.warning(pt, st, title='Service Not Found')
            return True
        else:
            self.unhandled_exception(exctype, value, tb)

    def unhandled_exception(self, exctype, value, tb):
        self._info_label.set_text(str(exctype))
        self.print_tb(tb)
        lines = traceback.format_exception_only(exctype, value)

        msg = traceback.format_exception_only(exctype, value)[0]
        result = msg.split(' ', 1)
        if len(result) == 1:
            msg = result[0]
            arguments = ''
        else:
            msg, arguments = result
        self._insert(msg, 'exc')
        self._insert(' ' + arguments)
        
    def _print(self, line):
        self._buffer.insert_at_cursor(line + '\n')

    def _insert(self, text, *tags):
        end_iter = self._buffer.get_end_iter()
        self._buffer.insert_with_tags_by_name(end_iter, text, *tags)
        
    def _print_file(self, filename, lineno, name):
        if filename.startswith(self._pwd):
            filename = filename.replace(self._pwd, '')[1:]

        self._insert('  File ')
        self._insert(filename, 'filename')
        self._insert(', line ')
        self._insert(str(lineno), 'lineno')
        self._insert(', in ')
        self._insert(name, 'name')
        self._insert('\n')
        
    def print_tb(self, tb, limit=None):
        """Print up to 'limit' stack trace entries from the traceback 'tb'.

        If 'limit' is omitted or None, all entries are printed.  If 'file'
        is omitted or None, the output goes to sys.stderr; otherwise
        'file' should be an open file or file-like object with a write()
        method.
        """

        if limit is None:
            if hasattr(sys, 'tracebacklimit'):
                limit = sys.tracebacklimit
        n = 0
        while tb is not None and (limit is None or n < limit):
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            self._print_file(filename, lineno, name)
            line = linecache.getline(filename, lineno)
            if line:
                self._print('    ' + line.strip())
            tb = tb.tb_next
            n = n+1

    def _start_debugger(self):
        import pdb
        pdb.pm()

    def _on_send__clicked(self, button):
        buf = self._ticketdesc.get_buffer()
        desc = buf.get_text(*buf.get_bounds())
        if self._ticketinclexc.get_active():
            exc = self._buffer.get_text(*self._buffer.get_bounds())
            desc = '%s\n\n{{{\n%s\n}}}\n' % (desc, exc)
        summary = self._ticketname.get_text()
        reply = self.maketicket(summary, desc)

    def _on_ok__clicked(self, button):
        self.destroy()

    def maketicket(self, summary, description, name='Pida Bug report'):
        base = 'http://tracos.org/pida/'
        url = '%s/newticket' % base.rstrip('/')
        postdata={'reporter': name,
                  'summary': summary,
                  'description': description,
                  'action': 'create',
                  'status': 'new',
                  'milestone': '0.3',}
        data = urllib.urlencode(postdata)
        request = urllib2.Request(url, data=data)
        try:
            page = urllib2.urlopen(request).read()
        except:
            page = ''
        if 'id="ticket"' in page:
            number = page.split('<title>', 1)[-1].split(' ', 1)[0]
            number = number.strip('#')
            reply = ('New ticket at: %s/ticket/%s' %
                     (base.rstrip('/'), number))
        else:
            reply = 'Posting a new bug report failed.'
        self._print(reply)

    
def show(exctype, value, tb):
    if exctype is not KeyboardInterrupt:
        dw = DebugWindow()
        if dw.show_exception(exctype, value, tb):
            return
        dw.show_all()
        if not gtk.main_level():
            def q(window):
                gtk.main_quit()
            dw.connect('destroy', q)
            gtk.main()

if __name__ == '__main__':
    sys.excepthook = show
    print 123
    def a():
        raise errors.ServiceNotFoundError('window')
    def b():
        a()
    def c():
        b()
        b()
    c()
    #dw = DebugWindow()
    #resp = dw.run()
    #print resp
    #dw.destroy()
