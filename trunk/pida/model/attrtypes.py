

class RegistryItem(object):

    @staticmethod
    def serialize(data):
        return '%s' % data

    @staticmethod
    def unserialize(data):
        return data

class types(object):
    """Types used by the registry."""

class string(RegistryItem):
    """A plain string."""

class readonly(RegistryItem):
    """A read only string"""

class directory(RegistryItem):
    """A directory"""

#class directorycreating(directory):
#    def validate(self, value):
#        if Directory.validate(self, value):
#            return True
#        else:
#            os.makedirs(value)
#            return directory.validate(self, value)

class file(RegistryItem):
    """A file"""

class readonlyfile(file):
    """Read only file"""

#class filemustexist(file):

#    def validate(self, value):
#        return os.path.exists(value)

#class filewhich(file):
# 
#     def setdefault(self):
#         import distutils.spawn as spawn
#         path = spawn.find_executable(self.default)
#         if path:
#             self.set(path)
#         else:
#             self.set('')

class font(RegistryItem):
    """Font"""

class boolean(RegistryItem):
    
    @staticmethod
    def unserialize(data):
        try:
            val = int(data)
        except ValueError:
            val = int(data[0].lower() in ['t'])
        except:
            raise errors.BadRegistryDataError
        return val

class integer(RegistryItem):

    @staticmethod
    def unserialize(data):
        try:
            val = int(data)
        except:
            raise errors.BadRegistryDataError
        return val

class list(RegistryItem):
    """"""

class editor(list):
    # see #101
    choices = ['vim', 'culebra', 'emacs', 'scerpent']

class color(RegistryItem):
    """"""

class fileembedded(RegistryItem):
    """"""

class password(RegistryItem):
    """A password item."""

def intrange(lower, upper, step):
    # can't use class call
    classdict = {'lower': lower,
                 'upper': upper,
                 'step': step}
    return type('intrange', (integer,), classdict)

def stringlist(*args):
    classdict = {'choices': args}
    return type('stringlist', (list,), classdict)
