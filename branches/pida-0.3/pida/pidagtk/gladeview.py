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

# pidagtk import(s)
import pida.pidagtk.contentview as contentview

# gtk import(s)
import gtk

# gazpacho import(s)
try:
    from pida.utils.gazpacholoader import ObjectBuilder
except:
    ObjectBuilder = None

def glade_view_builder(glade_file_name, top_level_name='pida_view'):
    def __init__(self, svc, prefix, **kw):
        view = glade_view(svc, prefix,
                          glade_file_name=glade_file_name,
                          top_level_name=top_level_name,
                          **kw)
        return view
    return __init__
    
class glade_view(contentview.content_view):
    """A content_view based on a glade file"""

    glade_file_name = None
    top_level_name = 'pida_view'

    def init(self, glade_file_name=None, top_level_name=None):
        assert (self.glade_file_name or glade_file_name,
                'must provide a glade file')
        assert ObjectBuilder, 'gazpacho must be installed'
        if glade_file_name is None:
            glade_file_name = self.glade_file_name
        else:
            self.glade_file_name = glade_file_name
        glade_file = self.__find_gladefile(glade_file_name)
        if not glade_file:
            self.service.log.info('glade file not found %s', glade_file)
            not_found = gtk.Label('this glade file was not found')
            self.widget.pack_start(not_found)
            return
        glade_build = ObjectBuilder(glade_file)
        self.__auto_connect(glade_build)
        if top_level_name is None:
            top_level_name = self.top_level_name
        else:
            self.top_level_name = top_level_name
        top_level = glade_build.get_widget(self.top_level_name)
        if top_level.get_parent() is not None:
            top_level.unparent()
        self.widget.pack_start(top_level)
        top_level.show_all()
        self.__glade_build = glade_build
        self.init_glade()

    def init_glade(self):
        pass

    def __auto_connect(self, glade_build):
        self.__connect_signals(glade_build, self, prefix='')
        self.__connect_signals(glade_build, self.service, prefix=self.prefix)

    def __connect_signals(self, glade_build, target, prefix=''):
        for attr in dir(target):
            if not attr.startswith('on_'):
                continue
            try:
                widg_name, sig_name = attr[3:].split('__')
                if prefix:
                    if widg_name.startswith(prefix):
                        widg_name = widg_name[len(prefix) + 1:]
                    else:
                        continue
            except ValueError:
                self.service.log.info('badly named signal handler "%s"',
                                      attr)
                continue
            f = getattr(target, attr)
            if not callable(f):
                self.service.log.info('non callable signal handler "%s"',
                                      attr)
                continue
            widget = glade_build.get_widget(widg_name)
            if widget is None:
                self.service.log.info('signal handler exists, but there'
                                      'is no widget "%s"', widg_name)
                continue
            try:
                widget.connect(sig_name, f)
            except TypeError:
                self.service.log.info('signal type "%s" does not exist '
                                      'for widget type "%s"',
                                       sig_name, widget)

    def __find_gladefile(self, filename):
        from pkg_resources import Requirement, resource_filename
        requirement = Requirement.parse('pida')
        resource = 'glade/%s' % filename
        try:
            glade_file = resource_filename(requirement, resource)
        except KeyError:
            glade_file = None
        return glade_file

    def get_widget(self, name):
        return self.__glade_build.get_widget(name)

