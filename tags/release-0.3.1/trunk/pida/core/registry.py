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

# pida import(s)
import base
import errors

# system import(s)
import os
import ConfigParser as configparser


class registry_item(base.pidacomponent):
    """A single item in the registry."""

    def init(self, name, doc, default):
        self.__name = name
        if doc is not None:
            doc = doc.replace('\n', ' ')
        self.__doc = doc
        self.__value = None
        self.__default = default

    def setdefault(self):
        self.value = self.__default

    def validate(self, value):
        return True

    def unserialize(self, data):
        return data

    def serialize(self):
        return '%s' % self.value

    def load(self, data):
        try:
            value = self.unserialize(data)
        except Exception, e:
            # Any unserialisation error is a failure
            return False
        try:
            self.value = value
            return True
        except errors.BadRegistryValueError:
            self.setdefault()
            return False

    def set_value(self, value):
        if self.validate(value):
            self.__value = value
        else:
            raise errors.BadRegistryValueError, value

    def get_value(self):
        return self.__value

    value = property(get_value, set_value)

    def get_name(self):
        return self.__name
    name = property(get_name)

    def get_doc(self):
        return self.__doc

    def set_doc(self, value):
        self.__doc = value

    doc = property(get_doc, set_doc)

    def get_default(self):
        return self.__default

    default = property(get_default)

    def __repr__(self):
        return ('Registry Value typ=%s name=%s value=%s default=%s '
                'doc=%s' % (self.__class__.__name__, self.__name,
                           self.__value, self.__default, self.doc))
                    
class registry_group(base.pidagroup):
    """A registry group."""
    
    group_type = lambda *a: registry_group(*a)
    def __create_component(self, name, doc, default, typ):
        return typ(name, doc, default)
    component_type = __create_component

    def init(self, name, doc):
        base.pidagroup.init(self, name)
        self.__doc = doc

    def get_doc(self):
        return self.__doc
    doc = property(get_doc)


class registry(base.pidamanager):
    """The pida registry."""

    group_type = registry_group

    file_intro = '# pida generated ini file'

    def __get_tempopts(self, filename):
        self.filename = filename
        tempopts = configparser.ConfigParser()
        if os.path.exists(self.filename):
            f = open(self.filename, 'r')
            tempopts.readfp(f)
            f.close()
        return tempopts

    def load(self, filename):
        tempopts = self.__get_tempopts(filename)
        for group, option in self.iter_items():
            if tempopts.has_option(group.name, option.name):
                data = tempopts.get(group.name, option.name)
                if not option.load(data):
                    option.setdefault()
            else:
                option.setdefault()

    def save(self):
        f = open(self.filename, 'w')
        f.write(self.file_intro)
        for group in self.iter_groups():
            f.write('\n[%s]\n' % group.name)
            for option in group:
                f.write('# %s\n' % option.name)
                f.write('# %s\n' % option.doc)
                f.write('# default value = %s\n' % option.default)
                f.write('%s = %s\n\n' % (option.name, option.value))
        f.close()


class types(object):
    """Types used by the registry."""

    class string(registry_item):
        """A plain string."""

    class directory(registry_item):
        def validate(self, value):
            return os.path.isdir(value)
        
    class directorycreating(directory):
        def validate(self, value):
            if Directory.validate(self, value):
                return True
            else:
                os.makedirs(value)
                return directory.validate(self, value)

    class file(registry_item):
        """"""

    class filemustexist(file):

        def validate(self, value):
            return os.path.exists(value)

    class filewhich(file):
    
        def setdefault(self):
            import distutils.spawn as spawn
            path = spawn.find_executable(self.default)
            if path:
                self.set(path)
            else:
                self.set('')

    class font(registry_item):
        """Font"""

    class boolean(registry_item):
        def unserialize(self, data):
            try:
                val = int(data)
            except ValueError:
                val = int(data[0].lower() in ['t'])
            except:
                raise errors.BadRegistryDataError
            return val

    class integer(registry_item):
        def unserialize(self, data):
            try:
                val = int(data)
            except:
                raise errors.BadRegistryDataError
            return val

    class list(registry_item):
        """"""

    class editor(list):
        # see #101
        choices = ['vim', 'culebra', 'emacs', 'scerpent']

    class color(registry_item):
        """"""

    class fileembedded(registry_item):
        """"""

    class password(registry_item):
        """A password item."""

    @staticmethod
    def intrange(lower, upper, step):
        # can't use class call
        classdict = {'lower': lower,
                     'upper': upper,
                     'step': step}
        return type('intrange', (types.integer,), classdict)
    
    @staticmethod
    def stringlist(*args):
        classdict = {'choices': args}
        return type('stringlist', (types.list,), classdict)

CONFIG_FILE_INTRO = (
    '#This is an automatically generated Pida config file.\n'
    '#Please edit it, your changes will be preserved (if valid).\n'
    '#If you want a fresh config file, delete it.\n\n'
    '#Notes:\n'
    '#Boolean values are 1 or 0\n'
    '#Blank lines are ignored as are lines beginning #\n'
    '#(comments).\n\n')


