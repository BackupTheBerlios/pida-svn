

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

    def __init__(self, model_attributes, current_callback):
        BaseMultiModelObserver.__init__(self, model_attributes)

    def __model_notify__(self, model, attr, val):
        self.save(model)

    def save(self, model):
        if model.__model_ini_filename__ is None:
            return
        f = open(model.__model_ini_filename__, 'w')
        f.write(self.file_intro)
        for groupname, doc, label, stock_id, attrkeys in \
                                            model.__model_groups__:
            f.write('\n[%s]\n' % groupname)
            for attrname in attrkeys:
                attr = model.__model_attrs_map__[attrname]
                f.write('# %s\n' % attr.name)
                f.write('# %s\n' % attr.doc.replace('\n', ' ').strip())
                f.write('# default value = %s\n' % attr.default)
                val = attr.rtype.serialize(getattr(model, attrname))
                f.write('%s = %s\n\n' % (attr.name, val))
        f.close()

    def add_model(self, model):
        super(IniFileObserver, self).add_model(model)
        self.save(model)

