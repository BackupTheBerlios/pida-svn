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
"""
This module tries to offer a very small subset of existing facilities of
'peak.binding'.

Its propose is to act as a bridge to aid in the migration to PEAK. Or to help
users who only need what this module has to offer.

You should import this module as:
try:
    from peak.api import binding
except ImportError:
    import components as binding

Currently supported stuff:

binding.Component (someParent, foo="foo", bar=1)
binding.Obtain ("../some/path")
binding.Obtain (SomeClass)
binding.Obtain (PropertyName ("some.key"))
binding.Obtain (Foo, offerAs=[ISomeIterface])
binding.Obtain (Foo, offerAs=[PropertyName('some.key')])
binding.Make (SomeClass)
binding.Make (lambda self: "foo")
binding.Make (Foo, offerAs=[ISomeIterface])
binding.Make (Foo, offerAs=[PropertyName('some.key')])

Not suported:
binding.Make (dict)
binding.Make (list)
binding.Make (lambda: "foo")
binding.Make (Foo, uponAssembly = True)

What's new and shouldn't be used if you're concerned with compatibility:
binding.Obtain ("foo", static = False)
binding.Obtain ("foo()")
binding.PropertyWrapper()
binding.ObjectPath()
binding.Component.iterUp()
binding.Component.components
binding.Component.namedComponents

Q: Why not use the actual peak.binding module?
A: On some specific cases size is a problem, on other cases the problem is that
PEAK is, unfornutely, not available on distributions.

Q: But isn't peak.binding more throughly tested? Aren't we just introducing more
bugs into it?

A: This is a real small module, I am going to port the test cases that apply to
peak.binding so that it has the same level of unittesting the original module
has.

Q: Can you implement X?
A: Maybe, but only if it's really small and offers real gain, otherwise please
use peak.binding instead.
"""
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
    
    def __init__ (self, path, static = True, offerAs = (), uponAssembly = False):
        self.fullPath = path.split("/")
        self.isAbsolute = path.startswith("/")
        self.keys = offerAs
        # The return values and
        self.returnValues = {}
        self.areStatic = {}
        self.static = static
        self.uponAssembly = uponAssembly
    
    def transverse (self, full_path, helper_func):
        
        return obj
    
    def isStatic (self, obj):
        return self.areStatic.get (obj, self.static)
    
    def hasReturnValue (self, obj):
        return obj in self.returnValues
        
    def __get__ (self, obj, type = None):
        
        if self.isStatic (obj) and self.hasReturnValue (obj):
            return self.returnValues[obj]

        orig_obj = obj
            
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
        
        if self.static:
            
            if hasattr (self, "name"):
                setattr (orig_obj, self.name, obj)
            else:
                self.returnValues[orig_obj] = obj
            
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

class Make (object):
    """
    A 'Make' content is created only when it's needed. It should wrap the
    component that you want to make lazy.
    
    Usage example:
    
    class Bar (Component):
        pass
    
    class Foo (Component):
        bar = Make (Bar)
    
    When you create an instance of 'Foo', the 'bar' instance will only be
    created when you access it the first time.    
    """
    
    def __init__ (self, componentFactory, offerAs = (), uponAssembly = False):
        self.componentFactory = componentFactory
        self.keys = offerAs
        self.uponAssembly = uponAssembly
        self.components = {}
        
    def __get__ (self, obj, type = None):
        if obj in self.components:
            return self.components[obj]
        
        self.components[obj] = self.componentFactory (obj)
        
        if hasattr (self, "name"):
            setattr (obj, self.name, self.components[obj])

        return self.components[obj]

class MetaComponent (type):
    def __init__ (cls, name, bases, attrs):
        cls._properties = {}
        cls._assembly_components = []
        
        for key, value in attrs.iteritems ():
            if isinstance (value, Make) or isinstance (value, ObjectPath):
                value.name = key
                
                for prop in value.keys:
                    cls._properties[prop] = value
                
                if (isinstance (value, Make) or isinstance (value, ObjectPath)) and value.uponAssembly:
                    cls._assembly_components.append (value)
                    
        # chain up
        super (MetaComponent, cls).__init__ (cls, name, bases, attrs)
        
class ParentsIterator:
    def __init__ (self, component):
        self.component = component
        
    def next (self):
        component = self.component
        if component is None:
            raise StopIteration
        
        self.component = self.component.parent
        
        return component
    
    def __iter__ (self):
        return self
        
class PropertyMapper (object):
    def __init__ (self, parent, data):
        self._data = data
        self._parent = weakref.ref (parent)
    
    parent = property (lambda self: self._parent())
    
    def get (self, key, default = None):
        if key not in self:
            return default
        
        return self[key]
        
    def __getitem__ (self, key):
        data = self._data[key]
        if hasattr (data, "__get__"):
            return data.__get__ (self.parent)
        else:
            return data
     
    def __setitem__ (self, key, value):
        self._data[key] = value
        
    def __contains__ (self, key):
        return key in self._data
    
    def __len__ (self):
        return len (self._data)
    
    def has_key (self, key):
        return self._data.has_key (key)
    
    def __repr__ (self):
        assert self._data is not None
        print "<PropertyMapper %r>" % self._data

try:
    import gobject
    
    class MetaGComponent (MetaComponent, gobject.GObjectMeta): pass
    
except ImportError:
    gobject = None
    
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
    if gobject is not None:
        __metaclass__ = MetaGComponent
    else:
        __metaclass__ = MetaComponent
    
    _properties = {}
    
    def __init__ (self, parent = None, **kwargs):
        self.__parent = parent is not None and weakref.ref (parent) or void_func
        self._properties = PropertyMapper (self, self._properties)
        # Maintain components reference
        self._components = []
        for component in self.components:
            self._components.append (component (self))
        
        asm_components = []
        for component in self._assembly_components:
           asm_components.append (component.__get__ (self))
        
        self._assembly_components = asm_components
        
        for attr, component in self.namedComponents.iteritems ():
            setattr (self, attr, component(self))
        
        for key, value in kwargs:
            setattr (self, key, value)
        self._init ()
    
    def _init (self):
        """Override this method which is called in the constructor."""
    
    def getParent (self):
        return self.__parent ()
    
    parent = property (getParent)
    
    components = ()
    namedComponents = {}

    def iterUp (self):
        return ParentsIterator (self)
        

# Peak compatibility:
LazyComponent = Make

class PropertyName:
    def __init__ (self, name):
        self.name = name
    
    def __repr__ (self):
        return "<Property('%s')>" % self.name

class ObtainProperty (object):
    def __init__ (self, key):
        self.key = key
        
    def __get__ (self, obj, type = None):
        for component in iter (obj.iterUp ()):
            val = component._properties.get (self.key)
            if val is not None:
                break
        
        # Cache it when needed
        if component is not obj and val is not None:
            obj._properties[self.key] = val
            
        return obj._properties[self.key]
            

def Obtain (key, **kwargs):
    if isinstance (key, str):
        return ObjectPath (key, **kwargs)
    elif isinstance (key, PropertyName):
        return ObtainProperty (key, **kwargs)

