

import os.path
from ConfigParser import ConfigParser

from model import Model, BaseMultiModelObserver, property_evading_setattr

def get_tempopts(filename):
    tempopts = ConfigParser()
    if os.path.exists(filename):
        f = open(filename, 'r')
        tempopts.readfp(f)
        f.close()
    return tempopts

def load_model_from_ini(filename, model):
    model.__model_ini_filename__ = filename
    tempopts = get_tempopts(filename)
    for attr in model.__model_attrs_map__.values():
        if tempopts.has_option(attr.group, attr.name):
            data = tempopts.get(attr.group, attr.name)
            val = attr.rtype.unserialize(data)
            if val == '':
                val = attr.default
            property_evading_setattr(model, attr.key, val)
    return model

class IniFileObserver(BaseMultiModelObserver):

    file_intro = '# pida generated ini file'

    def __model_notify__(self, model, attr, val):
        self.save(model)

    def save(self, model):
        if model.__model_ini_filename__ is not None:
            filename = model.__model_ini_filename__
        else:
            print 'not saving'
            return
        f = open(filename, 'w')
        f.write(self.file_intro)
        for groupname, doc, label, stock_id, attrkeys in \
                                            model.__model_groups__:
            f.write('\n[%s]\n' % groupname)
            for attrname in attrkeys:
                attr = model.__model_attrs_map__[attrname]
                if attr.fget is not None:
                    continue
                f.write('# %s\n' % attr.name)
                if attr.doc is not None:
                    f.write('# %s\n' % attr.doc.replace('\n', ' ').strip())
                f.write('# default value = %s\n' % attr.default)
                val = attr.rtype.serialize(getattr(model, attrname))
                f.write('%s = %s\n\n' % (attr.name, val))
        f.close()

    def add_model(self, model):
        super(IniFileObserver, self).add_model(model)
        self.save(model)

