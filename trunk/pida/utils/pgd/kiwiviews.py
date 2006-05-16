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

"""
Module for providing Python-written Kiwi-enabled views and delegates.

Background:

Sometimes it is impractical to build a component with Glade, and the classes in
this module can be used to create and attach views written in pure python.
"""

import gtk


#from kiwi.proxies import Proxy
from kiwi.ui.delegates import Delegate, SlaveDelegate
from kiwi.ui.views import SlaveView, BaseView

class PythonViewMixin(object):
    def __init__(self):
        # defeat class.widgets
        self.widgets = []
        self._proxied_widgets = set()

    def create_toplevel_widget(self):
        """Override to create and return the top level container."""
        return gtk.VBox()

    def add_widget(self, attribute, widget, model_attribute=None):
        """Name a widget and make it available to kiwi."""
        if model_attribute is not None:
            widget.set_property('model-attribute', model_attribute)
            self._proxied_widgets.add(attribute)
        setattr(self, attribute, widget)
        # needed to get over the class variable widgets
        self.widgets.append(attribute)
        return widget

    def attach_slaves(self):
        """Override to insert post-initialisation slave attachment."""

    def set_model(self, model):
        """Set the model and create a proxy."""
        self.python_model = model
        self.python_proxy = Proxy(self, model=model, widgets=self._proxied_widgets)
        self.model_changed(model)

    def model_changed(self, model):
        pass

class PythonSlaveDelegate(SlaveDelegate, PythonViewMixin):
    def __init__(self, toplevel=None, **kw):
        PythonViewMixin.__init__(self)
        if toplevel is None:
            toplevel = self.create_toplevel_widget()
        SlaveDelegate.__init__(self, toplevel=toplevel, **kw)
        self.attach_slaves()
        
class PythonView(BaseView, PythonViewMixin):
    def __init__(self, toplevel=None, *args, **kw):
        PythonViewMixin.__init__(self)
        if toplevel is None:
            toplevel = self.create_toplevel_widget()
        BaseView.__init__(self, toplevel=toplevel, *args, **kw)

class PythonDelegate(Delegate, PythonViewMixin):
    def __init__(self, toplevel=None, **kw):
        PythonViewMixin.__init__(self)
        if toplevel is None:
            toplevel = self.create_toplevel_widget()
        Delegate.__init__(self, toplevel=toplevel, **kw)
        self.attach_slaves()

