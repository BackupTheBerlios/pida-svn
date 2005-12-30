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

import pida.pidagtk.contentbook as contentbook

import pida.core.service as service

import pida.core.registry as registry
import os
import os.path

SCRIPTS_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "scripts")

#class ScriptView(contentbook.TabView):

 #   ICON = 'scripts'


class Scripts(service.ServiceWithListedTab):

    NAME = 'scripts'

    OPTIONS = [('directory', 'The scripts directory',
                SCRIPTS_CONF, registry.CreatingDirectory)]

#    EDITOR_VIEW = ScriptView
    
    def reset(self):
        directory = self.options.get('directory').value()
        self.__registry = registry.Registry()
        files = self.__get_names()
        for filename in files:
            path = os.path.join(directory, filename)
            group = self.__registry.add_group(filename, '')
            opt = group.add('script', 'the script contents.',
                            path, registry.EmbedFile)
            opt.setdefault()

    def __get_names(self):
        directory = self.options.get('directory').value()
        try:
            files = os.listdir(directory)
            if files == []:
                example = open(os.path.join(directory, "example"), 'w')
                example.write("command('terminal', 'execute-py-shell')\n")
                example.close()
                return self.__get_names()
        except OSError:
            self.log_warn("Unable to read scripts directory '%s'" % directory)
            files = []
        return files
    
    def __get_script(self, scriptname):
        if scriptname in self.__get_names():
            directory = self.options.get('directory').value()
            f = open(os.path.join(directory, scriptname))
            script = f.read()
            f.close()
            return script

    def cmd_execute_file(self, scriptname, filename):
        globaldict = {'filename':filename}
        self.cmd_execute(scriptname, globaldict)

    def cmd_execute(self, scriptname, globaldict={}):
        script = self.__get_script(scriptname)
        if script is not None:
            self.execute(script, globaldict)
        else:
            self.log_warn("Unknown script '%s'" % scriptname)
            
    def execute(self, script, globaldict={}):
        globaldict['command'] = self.boss.command
        exec script in globaldict

    def cmd_show_editor(self):
        self.create_editorview(self.__registry)

    def cb_show_editor(self, button):
        self.cmd_show_editor()


Service = Scripts
