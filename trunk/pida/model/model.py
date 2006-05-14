# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

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

'''
Model observer support.

The concept is simple. One model, many observers. Model attributes change and
the observers are notified. Observers notify the model of change, and the other
observers are notified. The goal is synchronised data in different views,
files, or anywhere.

A model is a class that is created at runtime. It will be a subclass of Model
that will be additionally tagged with the attributes that have been specified
in the model definition.

Attributes are grouped in a single level of groups, as:

    group1/
        attr1
        attr2
    group2/
        attr1
        attr2

And can then be used on the subsequently created objects as so:

    obj.group1__attr1
    obj.group2__attr2

The model definition is a Python class used as a schema. It contains all the
information required to generate typed attributes with the necessary
parameters. An example schema is available in example.py. It is used as
follows.

class MySchema:

    __order__ = ['Group1']      # the rendered order of the attributes

    class Group1:               # the first attribute this group
        """About group 1"""     # documentation for this group
        label = 'Group 1'       # display label for this group
        stock_id = 'my_stock'   # a string for a graphical representation

        class Attr1:                # the first attribute of group1
            """About attr1"""       # documentation for attr 1
            label = 'Attr1'
            rtype = types.string    # the registry type, from attrypes module
            default = 'foo'         # the default value

       class Attr2:
            """About attr2"""
            label = 'Attr 2'
            rtype = types.readonly  # use a readonly type

            def fget(self):
                """
                You can set a function which will be called when the
                attribute is accessed. This is best used with read-only
                types and is a way of changing what the observer sees
                """
                return self.Group1__Attr1 + '_something added'

           dependents = ['Group1__Attr1']   # if this attribute is to be
                                            # returned from a function, the
                                            # observers will not be notified of
                                            # the change unless we set some
                                            # dependent attributes. In this
                                            # case the attribute is dependent
                                            # on Group1__Attr1, and that is the
                                            # only member of the list that we
                                            # pass.

Once the schema has been specified, a model class needs to be created from
it, calling Model.__model_from_definition__(schema) with the model
schema as the parameter. A class (type) is returned which can then be
instantiated to create model objects, for example, using the schema above:

MyModel = Model.__model_from_definition__(schema)
obj1 = MyModel()
obj2 = MyModel()

etc.
'''

import inspect
import fnmatch

from string import Template
from types import ClassType

def property_evading_setattr(obj, attr, val):
    """Set an attribute, but use the property first if available."""
    if attr in obj.__class__.__dict__:
        p = obj.__class__.__dict__[attr]
        if hasattr(p, 'fset'):
            if p.fset is not None:
                p.fset(obj, val)
            return
    setattr(obj, attr, val)

def property_evading_getattr(obj, attr):
    if attr in obj.__class__.__dict__:
        p = obj.__class__.__dict__[attr]
        if getattr(p, 'fset', None):
            return getattr(p, 'fget')(obj)


def get_defintion_attrs(definition):
    """Generate the inner classes of a model defenition."""
    try:
        attrs = definition.__order__
    except AttributeError:
        get_classes = lambda obj: type(obj) == type or \
                                  type(obj) == ClassType

        attrs = [name for name, obj in \
                    inspect.getmembers(definition, get_classes)]
        
    for name in attrs:
        if not name.startswith('_'):
            attr = getattr(definition, name)
            yield attr


def get_groups(definition):
    for group in get_defintion_attrs(definition):
        L = []
        name = group.__name__
        if hasattr(group, 'stock_id'):
            stock_id = group.stock_id
        else:
            stock_id = ''
        if hasattr(group, 'label'):
            label = group.label
        else:
            label = name

        if group.__doc__ is None:
            doc = None
        else:
            doc = format_docstring(group.__doc__)
            
        G = (name, doc, label, stock_id, L)
        for attr in get_defintion_attrs(group):
            a = ModelAttribute.from_definition(group.__name__, attr)
            L.append(a)
        yield G


def add_attr_to_class(classdict, attr):
    prop_name = attr.key
    attr_name = '_%s' % prop_name
    if attr.fget is not None:
        fget = attr.fget.im_func
        fset = None
    else:
        classdict[attr_name] = attr.default
        def fget(self, attr_name=attr_name):
            return getattr(self, attr_name)
        def fset(self, val, attr_name=attr_name, prop_name=prop_name):
            setattr(self, attr_name, val)
            self.__model_notify__([prop_name])
    classdict[attr.key] = property(fget, fset)

def format_docstring(doc):
    assert doc is not None
    return doc.replace('\n', ' ').strip()

class ModelAttribute(object):
    """A model attribute."""
    def __init__(self, group, name, doc, rtype, default,
                 label, sensitive_attr, dependents, hidden, fget):
        self.group = group
        self.name = name
        self.doc = doc
        self.rtype = rtype
        self.default = default
        self.label = label
        self.sensitive_attr = sensitive_attr
        self.dependents = dependents
        self.key = '%s__%s' % (self.group, self.name)
        self.hidden = hidden
        self.fget = fget

    @classmethod
    def from_definition(cls, group, definition):
        name = definition.__name__

        if definition.__doc__ is None:
            doc = None
        else:
            doc = format_docstring(definition.__doc__)
            
        rtype = definition.rtype
        if hasattr(definition, 'label'):
            label = definition.label
        else:
            label = name
        if hasattr(definition, 'sensitive_attr'):
            sensitive_attr = definition.sensitive_attr
        else:
            sensitive_attr = None
        if hasattr(definition, 'dependents'):
            dependents = definition.dependents
        else:
            dependents = []
        if hasattr(definition, 'fget'):
            fget = definition.fget
            default = None
        else:
            default = definition.default
            fget = None
        if hasattr(definition, 'hidden'):
            hidden = definition.hidden
        else:
            hidden = False
        return cls(group, name, doc, rtype, default, label, sensitive_attr,
                   dependents, hidden, fget)


class Model(object):
    """The Model base class.

    Not really for subclassing unless you know what you are doing. Instead,
    create a definition and call __model_from_definition__
    """
    def __init__(self):
        self.__model_observers__ = {}
        self.__model_dependents__ = {}
        self.__model_blocked__ = {}
        self.__model_ini_filename__ = None
        for attr_key in self.__model_attrs_map__:
            self.__model_observers__[attr_key] = set()
            self.__model_blocked__[attr_key] = set()
        self.__model_dependents__ = self.__class__.__model_dependents__

    @classmethod
    def __model_from_definition__(cls, definition):
        """Create a new Model type for a definition schema"""
        classdict = dict(cls.__dict__)
        classdict['__model_attrs__'] = []
        classdict['__model_attrs_map__'] = {}
        classdict['__model_groups__'] = []
        classdict['__model_dependents__'] = {}
        for group_name, group_doc, label, stock_id, attrs in \
                                                get_groups(definition):
            classdict['__model_groups__'].append((group_name, group_doc,
                label, stock_id, [attr.key for attr in attrs]))
            for attr in attrs:
                add_attr_to_class(classdict, attr)
                classdict['__model_attrs__'].append(attr)
                attr_key = attr.key
                classdict['__model_attrs_map__'][attr_key] = attr
                classdict['__model_dependents__'][attr_key] = set()
                for depattr in attr.dependents:
                    classdict['__model_dependents__'][depattr].add(attr_key)
        classdict['__model_markup__'] = property(definition.__markup__.im_func)
        newcls = type('%sModel' % definition.__name__, (cls,), classdict)
        return newcls

    def __model_notify__(self, attrs=None):
        if attrs is None:
            attrs = self.__model_attrs_map__.keys()
        for attr in attrs:
            val = getattr(self, attr)
            for observer in self.__model_observers__[attr]:
                if observer not in self.__model_blocked__[attr]:
                    observer.__model_notify__(self, attr, val)
            self.__model_notify__(self.__model_dependents__[attr])

    def __model_register__(self, observer, attrs=None):
        if attrs is None:
            attrs = self.__model_attrs_map__.keys()
        for attr in attrs:
            self.__model_observers__[attr].add(observer)

    def __model_unregister__(self, observer, attrs):
        if attrs is None:
            attrs = self.__model_attrs_map__.keys()
        for attr in attrs:
            try:
                self.__model_observers__[attr].remove(observer)
            except KeyError:
                pass

    def __model_block__(self, observer, attrs):
        for attr in attrs:
            self.__model_blocked__[attr].add(observer)

    def __model_unblock__(self, observer, attrs):
        for attr in attrs:
            self.__model_blocked__[attr].remove(observer)

    def __model_serialize__(self, attr):
        sfunc = self.__model_attrs_map__.rtype.serialize
        return sfunc(getattr(self, attr))

    def __model_get_interpolation_attrs__(self):
        interp = {}
        for k in self.__model_attrs_map__:
            a = property_evading_getattr(self, k)
            if a is not None:
                interp[k] = a
        return interp

    def __model_interpolate__(self, text):
        t = Template(text)
        try:
            return t.substitute(self.__model_get_interpolation_attrs__())
        except (ValueError, KeyError):
            return text


class BaseObserver(object):

    def __model_notify__(self, model, attr, val):
        """Called when a model attribute is changed"""

    def set_model(self, model):
        """Override to set the current value."""


class BaseSingleModelObserver(BaseObserver):

    def __init__(self, model_attributes=None):
        self.__model_attributes__ = model_attributes
        self._model = None

    def set_model(self, model):
        if self._model is not None:
            self._model.__model_unregister__(self,
                self._model.__model_attrs_map__.keys())
        self._model = model
        if self.__model_attributes__ is None:
            ma = model.__model_attrs_map__.keys()
        else:
            ma = self.__model_attributes__
        model.__model_register__(self, ma)
        for attr in model.__model_attrs_map__.keys():
            self.__model_notify__(model, attr, getattr(model, attr))

    def update_model(self, attr, value):
        self._model.__model_block__(self, [attr])
        property_evading_setattr(self._model, attr, value)
        self._model.__model_unblock__(self, [attr])


class BaseMultiModelObserver(BaseObserver):

    def __init__(self, model_attributes=None,
                 current_callback=lambda *a: None):
        self.__model_attributes__ = model_attributes
        self._model = None
        self.current_callback = current_callback

    def add_model(self, model):
        model.__model_register__(self, self.__model_attributes__)

    def remove_model(self, model):
        model.__model_unregister__(self, self.__model_attributes__)

class CallbackObserver(BaseSingleModelObserver):

    def __init__(self, instance, prefix='cb'):
        self.instance = instance
        self.prefix = prefix
        super(CallbackObserver, self).__init__()

    def __model_notify__(self, model, attr, val):
        fname = '%s_%s' % (self.prefix, attr)
        if hasattr(self.instance, fname):
            getattr(self.instance, fname)(val)

class MatchObserver(BaseSingleModelObserver):
    """
    This type of observer uses a matcher function to figure out if
    it wants to be notified for a certain state change. The matcher
    function must accept a single argument, the attribute.
    
    It uses callable objects to be notified, they have this format:
    callback(attr, val)
    """
    def __init__(self):
        self.observers = {}
        super(MatchObserver, self).__init__()
        self.id = 0
        
    def register(self, matcher, callback):
        """When you register you get a registration id you can
        then use to unregister the callback from this observer"""
        
        self.observers[self.id] = (matcher, callback)
        current_id = self.id
        self.id += 1
        return current_id

    def unregister(self, register_id):
        del self.observers[register_id]
        
    def connect(self, pattern, callback):
        """Uses glob style strings to match the attribute name"""
        matcher = lambda attr: fnmatch.fnmatchcase(attr, pattern)
        return self.register(matcher, callback)
        
    def __model_notify__(self, model, attr, val):
        for matcher, callback in self.observers.values():
            if matcher(attr):
                callback(attr, val)


class ModelGroup(object):

    __model_attributes__ = None

    def __init__(self, current_callback=lambda *a: None):
        self._observers = []
        self._current = None
        self._models = []
        self.current_callback = current_callback

    def create_multi_observer(self, obstype):
        obs = obstype(self.__model_attributes__, self.set_current)
        self._observers.append(obs)
        for model in self._models:
            obs.add_model(model)
        if self._current is not None:
            obs.set_model(self._current)
        return obs

    def create_single_observer(self, obstype):
        obs = obstype(self.__model_attributes__)
        self._observers.append(obs)
        if self._current is not None:
            obs.set_model(self._current)
        return obs

    def remove_observer(self, obs):
        self._observers.remove(obs)
        for model in self._models:
            model.__model_unregister__(obs, obs.__model_attributes__)

    def add_model(self, model):
        self._models.append(model)
        for obs in self._observers:
            if hasattr(obs, 'add_model'):
                obs.add_model(model)

    def remove_model(self, model):
        self._models.remove(model)
        for obs in self._observers:
            if hasattr(obs, 'remove_model'):
                obs.remove_model(model)
        if len(self._models):
            self.set_current(self._models[-1])

    def set_current(self, model, level=0):
        if self._current is not model:
            self._current = model
            for obs in self._observers:
                obs.set_model(model)
            if level:
                self.current_callback(model)
            #model.__model_notify__()

    def __iter__(self):
        return iter(self._models)


