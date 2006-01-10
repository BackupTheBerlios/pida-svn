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



import pida.core.service as service
import os
import string
TEMPLATES_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "templates")

class Template(string.Template):

    def __init__(self, name, group, filename):
        self.__name = name
        self.__group = group
        self.__text = None
        if os.path.exists(filename):
            try:
                f = open(t, 'r')
                self.__text = f.read()
                f.close()
            except (OSError, IOError):
                pass
        string.Template.__init__(self, self.__text)

    def __get_vars(self):
        for match in self.pattern.finditer(self.template):
            groups = match.groupdict()
            if groups['braced']:
                yield groups['braced']
   
    def get_vars(self):
        return set([i for i in self.__get_vars()])

    def get_name(self):
        return self.__name
    name = property(get_name)

    def get_group(self):
        return self.__group
    group = property(get_group)

class FileTemplates(service.Service):
    
    NAME = 'filetemplates'

    COMMANDS = [('get-template-names', []),
                ('get-license', [('licensename', True)]),
                ('get-template', [('templatename', True), ('group', True)])]

    def init(self):
        self.__templatesdir = TEMPLATES_CONF
        if not os.path.exists(TEMPLATES_CONF):
            os.mkdir(TEMPLATES_CONF)
        self.__licensesdir = os.path.join(TEMPLATES_CONF, 'licenses')
        if not os.path.exists(self.__licensesdir):
            os.mkdir(self.__licensesdir)

    def cmd_get_license_names(self):
        return [name for name in self.get_license_names()]

    def cmd_get_license(self, licensename):
        return self.get_license(licensename)

    def get_license_names(self):
        for license in os.listdir(self.__licensesdir):
            yield license

    def get_license(self, licensename):
        return self.get_template('licenses', licensename)

    def cmd_get_template_names(self):
        templates = {}
        for group, name in self.__get_template_names():
            templates.setdefault(group, []).append(name)
        return templates

    def __get_template_names(self):
        for dirname in os.listdir(self.__templatesdir):
            dirpath = os.path.join(self.__templatesdir, dirname)
            for filename in os.listdir(dirpath):
                yield (dirname, filename)

    def get_template(self, group, templatename):
        text = load_template(group, templatename)
        if text:
            template = string.Template(text)
            return template

    def load_template(self, group, templatename):
        filename = os.path.join(self.__templatesdir, group, templatename)
        return Template(filename, templatename, group)

Service = FileTemplates

