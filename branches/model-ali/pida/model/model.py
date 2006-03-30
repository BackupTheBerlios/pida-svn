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


def property_evading_setattr(obj, attr, val):
    if attr in obj.__class__.__dict__:
        p = obj.__class__.__dict__[attr]
        if hasattr(p, 'fset'):
            if p.fset is not None:
                p.fset(obj, val)
            return
    setattr(obj, attr, val)


def get_defintion_attrs(definition):
    for name in definition.__order__:
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
        G = (name, group.__doc__, label, stock_id, L)
        for attr in get_defintion_attrs(group):
            a = ModelAttribute.from_definition(group.__name__, attr)
            L.append(a)
        yield G


class ModelAttribute(object):

    def __init__(self, group, name, doc, rtype, default,
                 label, sensitive_attr, dependents, fget):
        self.group = group
        self.name = name
        self.doc = doc
        self.rtype = rtype
        self.default = default
        self.label = label
        self.sensitive_attr = sensitive_attr
        self.dependents = dependents
        self.key = '%s__%s' % (self.group, self.name)
        self.fget = fget

    @classmethod
    def from_definition(cls, group, definition):
        name = definition.__name__
        doc = definition.__doc__
        rtype = definition.rtype
        default = definition.default
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
        else:
            fget = None
        return cls(group, name, doc, rtype, default, label, sensitive_attr,
                   dependents, fget)


def add_attr_to_class(classdict, attr):
    prop_name = attr.key
    attr_name = '_%s' % prop_name
    if attr.fget is not None:
        fget = getattr(attr, 'fget')
        fset = None
    else:
        classdict[attr_name] = attr.default
        def fget(self, attr_name=attr_name):
            return getattr(self, attr_name)
        def fset(self, val, attr_name=attr_name, prop_name=prop_name):
            setattr(self, attr_name, val)
            self.__model_notify__([prop_name])
    classdict[attr.key] = property(fget, fset)

class Model(object):

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
        classdict['__model_markup__'] = property(definition.__markup__)
        newcls = type('%sModel' % definition.__name__, (cls,), classdict)
        return newcls

    def __model_notify__(self, attrs):
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
        for attr in attrs:
            self.__model_observers__[attr].remove(observer)

    def __model_block__(self, observer, attrs):
        for attr in attrs:
            self.__model_blocked__[attr].add(observer)

    def __model_unblock__(self, observer, attrs):
        for attr in attrs:
            self.__model_blocked__[attr].remove(observer)

    def __model_serialize__(self, attr):
        sfunc = self.__model_attrs_map__.rtype.serialize
        return sfunc(getattr(self, attr))


class BaseObserver(object):

    def __model_notify__(self, model, attr, val):
        """Called when a model attribute is changed"""


class BaseSingleModelObserver(BaseObserver):

    def __init__(self, model_attributes=None):
        self.__model_attributes__ = model_attributes
        self._model = None

    def set_model(self, model):
        self._model = model
        if self.__model_attributes__ is None:
            ma = model.__model_attrs_map__.keys()
        else:
            ma = self.__model_attributes__
        model.__model_register__(self, ma)
        model.__model_notify__(ma)

    def update_model(self, attr, value):
        self._model.__model_block__(self, [attr])
        property_evading_setattr(self._model, attr, value)
        self._model.__model_unblock__(self, [attr])


class BaseMultiModelObserver(BaseObserver):

    def __init__(self, model_attributes=None):
        self.__model_attributes__ = model_attributes
        self._model = None

    def add_model(self, model):
        model.__model_register__(self, self.__model_attributes__)

    def set_current_model(self, model):
        """Override to set the crrent value."""


class ModelGroup(object):

    __model_attributes__ = None

    def __init__(self):
        self._observers = []
        self._current = None
        self._models = []

    def create_multi_observer(self, obstype):
        obs = obstype(self.__model_attributes__, self.set_current)
        self._observers.append(obs)
        for model in self._models:
            obs.add_model(model)
        return obs

    def create_single_observer(self, obstype):
        obs = obstype(self.__model_attributes__)
        self._observers.append(obs)
        if self._current is not None:
            obs.set_model(self._current)
        return obs

    def add_model(self, model):
        self._models.append(model)
        for obs in self._observers:
            if hasattr(obs, 'add_model'):
                obs.add_model(model)

    def set_current(self, model):
        self._current = model
        for obs in self._observers:
            if hasattr(obs, 'set_current_model'):
                obs.set_current_model(model)
            elif hasattr(obs, 'set_model'):
                obs.set_model(model)


