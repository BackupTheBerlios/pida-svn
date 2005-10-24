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


import pida.core.service as service
import pida.pidagtk.contentbook as contentbook

from gazpacho import application

class GazpachoApplication(application.Application):
    pass

class EmbeddedGazpacho(contentbook.ContentView):

    def populate(self):
        self.__gazpacho = GazpachoApplication()
        print dir(self.__gazpacho)
        self.pack_start(self.__gazpacho.get_container())

class Gazpacho(service.Service):
    NAME = 'gazpacho'

    def populate(self):
        self.__view = None
        self.boss.command("buffermanager", "register-file-handler",
                          filetype="*.glade", handler=self)

    def open_file(self, filename):
        if self.__view is None:
            self.__view = EmbeddedGazpacho()
            self.boss.command("editor", "add-page", contentview=self.__view)


Service = Gazpacho
