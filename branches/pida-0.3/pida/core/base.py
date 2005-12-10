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


def set_boss(boss):
    pidaobject.boss = boss

class pidaobject(object):
    """The base pida class."""

    def __init__(self, *args, **kw):
        self.init(*args, **kw)

    def init(self, *args, **kw):
        """The actual constructor."""

class pidalogenabled(object):
    """Logging mixin."""

    def __init__(self, *args, **kw):
        self.log = self.__build_logger(self.__class__.__name__)

    def  __build_logger(self, name):
        import logging
        format_str = ('%(levelname)s '
                      '%(module)s.%(name)s:%(lineno)s '
                      '%(message)s')
        format = logging.Formatter(format_str)
        handler = logging.StreamHandler()
        handler.setFormatter(format)
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger
        

class pidaserializable(object):
    
    class __record__(object):
        __fields__ = []

    def get_record(self):
        record = pidaobject()
        for field, typ in self.__record__.__fields__:
            setattr(record, field, getattr(self, field, None))
        record.__fields__ = list(self.__record__.__fields__)
        return record

    def set_record(self, value):
        for field in value.__fields__:
            setattr(self, field, getattr(value, field, None))

    record = property(get_record, set_record)

class pidacomponent(pidalogenabled, pidaobject):
    """A single component."""
    def __init__(self, *args, **kw):
        pidalogenabled.__init__(self)
        pidaobject.__init__(self, *args, **kw)

    def is_leaf(self):
        return True
    is_leaf = property(is_leaf)

class pidagroup(pidacomponent):
    """A group of components."""

    component_type = pidacomponent
    group_type = lambda *a: pidagroup(*a)

    def init(self, name):
        self.__name = name
        self.__components = {}

    def add(self, name, component):
        """Add a component."""
        self.__components[name] = component
        return component

    def add_group(self, name, *args):
        group = self.group_type(name, *args)
        self.__components[name] = group
        return group

    def new(self, componentname, *args, **kw):
        component = self.component_type(componentname, *args, **kw)
        self.add(componentname, component)
        return component

    def remove(self, name):
        if name in self.__components:
            del self.__components[name]

    def get(self, name):
        """Return the named component, or None."""
        try:
            return self.__components[name]
        except KeyError:
            return None

    def get_name(self):
        """Return the name for the group."""
        return self.__name
    name = property(get_name)

    def __iter__(self):
        for k in self.__components:
            yield self.__components[k]

    def __len__(self):
        return len(self.__components)

    def iter_groups(self):
        for component in self:
            if not component.is_leaf:
                yield component

    def iter_components(self):
        for component in self:
            if component.is_leaf:
                yield component

    def is_leaf(self):
        return False
    is_leaf = property(is_leaf)

class pidamanager(pidagroup):
    """Manage components within top-level groups."""

    def init(self):
        pidagroup.init(self, None)

    def get_component(groupname, componentname):
        group = self.get(groupname)
        if group is not None:
            return group.get(componentname)

    def add_component(groupname, componentname, component):
        group = self.get(groupname)
        if group is not None:
            group.add(componentname, component)
        
    def new_component(self, groupname, componentname, *args, **kw):
        component = self.component_type(*args, **kw)
        self.add_component(component)

    def iter_items(self):
        for group in self.iter_groups():
            for item in group.iter_components():
                yield group, item

