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

import gtk, gobject

import pida.core.service as service

from pida.utils.launchpadder import lplib, gtkgui

defs = service.definitions


class BugReporter(service.service):


    def cmd_view(self):
        opts, args = lplib.fake_opts(product='pida')
        dlg = gtkgui.ReportWindow(opts)
        def on_response(dlg, response):
            def on_finished(results):
                dlg.hide()
                gobject.timeout_add(1000, dlg.destroy)
            if response == gtk.RESPONSE_ACCEPT:
                dlg._reporter.report(on_finished)  
            else:
                on_finished(None)
        dlg.connect('response', on_response)    
        dlg.show_all()
    
    def act_report_bug(self, action):
        self.call('view')

    def get_menu_definition(self):
        return """
               <menubar>
                <menu name="base_tools" action="base_tools_menu">
                <menuitem name="bugreport" action="bugreporter+report_bug" />
                </menu>
                </menubar>
               """


Service = BugReporter




