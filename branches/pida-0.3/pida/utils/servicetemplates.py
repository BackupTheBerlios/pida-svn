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

import gtk

def split_function_name(name):
    return name.split('_', 1)[-1]


def build_optiongroup_from_class(classobj, rootregistry):
    group = rootregistry.add_group(classobj.__name__,
                                    classobj.__doc__)
    for classkey in dir(classobj):
        item = getattr(classobj, classkey)
        if len(getattr(item, '__bases__', [])):
            if item.__bases__[0].__name__ == 'option':
                opt = group.new(item.__name__, item.__doc__,
                                item.default, item.rtype)
    return group


def get_actions_for_funcs(funclist, svc):
    for func in  funclist:
        name = split_function_name(func.func_name)
        actname = '%s+%s' % (svc.NAME, name)
        words = [(s[0].upper() + s[1:]) for s in name.split('_')]
        label = ' '.join(words)
        stock_id = 'gtk-%s%s' % (words[0][0].lower(), words[0][1:])
        action = gtk.Action(actname, label, func.func_doc, stock_id)
        action.connect('activate', getattr(svc, func.func_name))
        yield action
