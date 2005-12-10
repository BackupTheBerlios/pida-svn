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


class source_code_node(object):

    def __init__(self, filename, linenumber, nodename, nodetype, additional):
        self.__filename = filename
        self.__linenumber = linenumber
        self.__nodename = nodename
        self.__nodetype = nodetype
        self.__additional = additional
        self.__children = []

    def get_children(self):
        return self.__children
    children = property(get_children)

    def add_child(self, node):
        self.__children.append(node)

    def get_filename(self):
        return self.__filename
    filename = property(get_filename)

    def get_linenumber(self):
        return self.__linenumber
    linenumber = property(get_linenumber)

    def get_name(self):
        return self.__nodename
    name = property(get_name)


try:
    from bike.parsing import fastparser
except ImportError:
    fastparser = None


def adapt_brm_node(node):
    pida_node = source_code_node(node.filename,
                                 node.linenum,
                                 node.name,
                                 node.type,
                                 'additional')
    return pida_node


def adapt_tree(roots, built=None):
    if built is None:
        built = source_code_node(None, None, None, None, None)
    for root in roots:
        pnode = adapt_brm_node(root)
        built.add_child(pnode)
        adapt_tree(root.getChildNodes(), pnode)
    return built


def parse(stringdata):
    return fastparser.fastparser(stringdata).getChildNodes()


def get_nodes_from_string(stringdata):
    return adapt_tree(parse(stringdata))


