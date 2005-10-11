# -*- coding: utf-8 -*-
# Copyright (C) 2005 Tiago Cogumbreiro <cogumbreiro@users.sf.net>
# $Id: components.py 570 2005-09-09 19:28:26Z cogumbreiro $

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import weakref

void_method = lambda self: None
void_func = lambda *args: None

def getRootComponent(component):
    """
    This is a helper function that tranverses the component tree upwards.
    """
    while component.parent is not None:
        component = component.parent
    return component

class ObjectPath (object):
    """
    An ObjectPath binds the path to a certain attribute to the instance
    of this class. It can have a relative or a absolute path, example:
    class Foo(Component):
        a_dict = {}
        a_list = []
        
        grandparent = ObjectPath ("../..")
        root = ObjectPath ("/", static=True)
        a_list_count = ObjectPath("a_list.__len__()")
    
    You can navigate up the hierarchy if you use the '..' fragment, this
    assumes your object has a field named 'parent'.
    
    You can also call any callable fragment using "()".
    
    If you assign the 'static' keyword argument to True then the
    value is only retrieved once.
    """
    def __init__ (self, path, static = False):
        self.fullPath = path.split("/")
        self.isAbsolute = path.startswith("/")
        self.isStatic = static
    
    def transverse (self, full_path, helper_func):
        
        return obj
        
    def __get__ (self, obj, type = None):

        if self.isStatic and hasattr(self, "returnValue"):
            return self.returnValue
            
        if self.isAbsolute:
            obj = getRootComponent(obj)
            
        for path in self.fullPath:
            if path == "." or path == "":
                pass
            elif path == "..":
                obj = obj.parent
            else:
                is_callable = path.endswith("()")
                if is_callable:
                    path = path[:-len ("()")]
                
                obj = getattr(obj, path)
                if is_callable:
                    obj = obj()
        
        if self.isStatic:
            self.returnValue = obj
            
        return obj

class PropertyWrapper (object):
    """
    PropertyWrapper is usefull to wrap the getter and setter methods of a
    variable that is not accessible through the 'property' protocol.
    It accepts private variables as well. 
    """
    def __init__ (self, variable, getter = None, setter = None):
        self.variable = variable
        self.realVariable = None
        self.getter = getter
        self.setter = setter
        
        if self.setter is None:
            del self.__set__
        
        if self.getter is None:
            del self.__get__
        
    def getVariable (self, obj):
        if self.realVariable is None:
            if self.variable.startswith("__"):
                self.realVariable = "_" + type(obj).__name__ + self.variable
            else:
                self.realVariable = self.variable
        return getattr (obj, self.realVariable)
    
    def __get__ (self, obj, type = None):
        obj = self.getVariable (obj)
        return getattr (obj, self.getter)()
    
    def __set__ (self, obj, value):
        obj = self.getVariable (obj)
        getattr (obj, self.setter) (value)


class Component (object):
    """
    A Component is an object that is structured in a hierarchical model.
    It is constructed upon runtime from the root to its children. To define
    a Component you have to define a list of subcomponents, these are usually
    classes of this type.
    They define a method called '_init' that is called in the constructor.
    It also contains a '_components' protected variable that holds a list of its
    children components.
    """
    
    def __init__ (self, parent = None):
        self.__parent = parent is not None and weakref.ref (parent) or void_func
        # Maintain components reference
        self._components = []
        for component in self.components:
            self._components.append (component(self))
            
        self._init ()
    
    def _init (self):
        """Override this method which is called in the constructor."""
    
    def getParent (self):
        return self.__parent ()
        
    parent = property (getParent)
    
    components = ()

