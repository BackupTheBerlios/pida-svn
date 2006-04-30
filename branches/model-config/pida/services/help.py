# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Ali Afshar aafshar@gmail.com

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

import pida
import pida.core.service as service
from pida.pidagtk.contentview import create_pida_icon

import gtk

class about_dialog(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)


class help(service.service):

    def cmd_about(self):
        dialog = gtk.AboutDialog()
        dialog.set_transient_for(self.boss.get_main_window())
        pb = create_pida_icon()
        dialog.set_logo(pb)
        dialog.set_version(self.boss.version)
        dialog.set_copyright(copyright)
        dialog.set_license(license)
        dialog.set_authors(authors)
        dialog.run()

    def act_about(self, action):
        self.call('about')

    def get_menu_definition(self):
        return """<menubar>
                    <menu name="base_help" action="base_help_menu">
                    <menuitem name="about" action="help+about" />    
                  </menu>
                    </menubar>"""


from pkg_resources import resource_filename
license_file = open(resource_filename('pida', 'data/COPYING'))
license = license_file.read()
license_file.close()
authors_file = open(resource_filename('pida', 'data/AUTHORS'))
authors = [n.strip() for n in authors_file.read().splitlines()]
authors_file.close()
copyright = 'Copyright (c) 2005-6 The PIDA Project aafshar@gmail.com'

Service = help
