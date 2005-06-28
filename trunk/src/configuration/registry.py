


import os
import ConfigParser as configparser

class BadRegistryKey(Exception):
    pass

class BadRegistryGroup(Exception):
    pass

class BadRegistryValue(Exception):
    pass

class BadRegistryData(Exception):
    pass

class BadRegistryDefault(Exception):
    pass


class RegistryItem(object):

    def __init__(self, name, default, doc):
        self._name = name
        self.doc = doc
        self._value = None
        self._default = default

    def setdefault(self):
        self._value = self._default

    def validate(self, value):
        return True

    def unserialize(self, data):
        return data

    def serialize(self):
        return '%s' % self.value

    def load(self, data):
        try:
            value = self.unserialize(data)
        except:
            # Any unserialisation error is a failure
            return False
        try:
            self.set(value)
            return True
        except BadRegistryEntry:
            return False

    def set(self, value):
        if self.validate(value):
            self._value = value
        else:
            raise BadRegistryEntry

    def value(self):
        return self._value

    def __repr__(self):
        return ('Registry Value typ=%s name=%s value=%s default=%s '
                'doc=%s' % (self.__class__.__name__, self._name,
                           self._value, self._default, self.doc))
                    

class RegistryGroup(object):
    
    def __init__(self, name, doc):
        self._name = name
        self._doc = doc

    def add(self, name, typ, default, doc):
        try:
            entry = typ(name, default, doc)
            setattr(self, name, entry)
            return entry
        except BadRegistryDefault:
            return False

    def delete(self, name):
        delattr(self, name)

    def __iter__(self):
        for child in dir(self):
            obj = getattr(self, child)
            if isinstance(obj, RegistryItem):
                yield obj
        
    def get(self, childname):
        if hasattr(self, childname):
            return getattr(self, childname)
        else:
            raise BadRegistryKey, '"%s"' % childname



class Boolean(RegistryItem):

    def unserialize(self, data):
        try:
            val = int(data)
        except ValueError:
            val = int(data[0].lower() in ['t'])
        except:
            raise BadRegistryData
        return val

class Integer(RegistryItem):

    def unserialize(self, data):
        try:
            val = int(data)
        except:
            raise BadRegistryData
        return val

class Registry(object):

    def __init__(self, filename):
        self.filename = filename
        self.optparseopts = {}

    def add_group(self, name, doc):
        group = RegistryGroup(name, doc)
        setattr(self, name, group)
        return group

    def iter_groups(self):
        for name in dir(self):
            obj = getattr(self, name)
            if isinstance(obj, RegistryGroup):
                yield obj

    def iter_items(self):
        for group in self.iter_groups():
            for option in group:
                yield group, option
        

    def load_file(self):
        print self.filename
        tempopts = configparser.ConfigParser()
        if os.path.exists(self.filename):
            f = open(self.filename, 'r')
            tempopts.readfp(f)
        for group, option in self.iter_items():
            if tempopts.has_option(group._name, option._name):
                data = tempopts.get(group._name, option._name)
                if not option.load(data):
                    option.setdefault()
            else:
                option.setdefault()

    def load_opts(self):
        for k in self.optparseopts:
            groupname, childname = k
            data = self.optparseopts[k]
            group = getattr(self, groupname)
            option = getattr(group, childname)
            option.load(data)

    def load(self):
        self.load_file()
        self.load_opts()

    def save(self):
        f = open(self.filename, 'w')
        f.write(CONFIG_FILE_INTRO)
        for group in self.iter_groups():
            f.write('\n[%s]\n' % group._name)
            for option in group:
                f.write('# %s\n' % option._name)
                f.write('# %s\n' % option.doc)
                f.write('# default value = %s\n' % option._default)
                f.write('%s = %s\n\n' % (option._name, option.value()))
        f.close()

    def prime_optparse(self, optparser):
        if hasattr(optparser, 'add_option'):
            def setfilename(opt, opt_str, value, parser):
                self.filename = value
            optparser.add_option('-f', '--config-file', type='string', nargs=1,
                                 action='callback', callback=setfilename)
            for group, option in self.iter_items():
                def setitem(opt, opt_str, value, parser):
                    self.optparseopts[(group._name, option._name)] = opt_str
                    print option.load(value), 'setitem'
                name = '%s.%s' % (group._name, option._name)
                longopt = '--config.%s' % name
                optparser.add_option(longopt,
                                     action='callback',
                                     type="string",
                                     callback=setitem, nargs=1, dest=name,
                                     help=option.doc)
            

CONFIG_FILE_INTRO = '# Autogenerated\n'

if __name__ == '__main__':

    r = Registry('/home/ali/tmp/reg')
    g = r.add_group('first', 'The docs for first group')
    e = g.add('blahA', Boolean, 0, 'docs for blahA')
    e = g.add('blahB', Boolean, 1, 'docs for blahB')
    import optparse
    op = optparse.OptionParser()
    r.prime_optparse(op)
    import sys
    sys.argv.append('--config.first.blahB=1')
    #sys.argv.append('-C/home/ali/tmp/reg2')
    print op.parse_args()
    r.load()
    #r.save()
    #e.load('True')
    #print r.groups
    print r.first.blahA
    #r.save()


