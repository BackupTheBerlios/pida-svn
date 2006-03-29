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
import base
from pida.core.actions import split_function_name

class argument(base.pidacomponent):
    """An argument for a command."""

    def __init__(self, name, required):
        self.__name = name
        self.__required = required

    def get_name(self):
        """Return the name of the argument."""
        return self.__name
    """Property for the name."""
    name = property(get_name)
    
    def get_required(self):
        """Return whether the argument is required."""
        return self.__required
    """Property for whether the argument is required."""
    required = property(get_required)

class command(base.pidacomponent):
    """A class to represent a command."""
    
    def init(self, name, callback, arguments):
        self.__name = name
        self.__callback = callback
        self.__arguments = arguments
        self.__doc = arguments.__doc__

    def get_name(self):
        """Return the name of the command."""
        return self.__name
    name = property(get_name)

    def get_args(self):
        """Return a list of IArgument for the command."""
        return self.__arguments

    def get_doc(self):
        return self.__doc
    doc = property(get_doc)

    def __call__(self, **kw):
        """Call the command with the keyword args."""
        #for arg in self.__arguments:
        #    if arg.required and arg.name not in kw:
        #        raise exceptions.bad_arguments_error, 'Missing %s' % arg.name
        return self.__callback(**kw)

class commandgroup(base.pidagroup):

    component_type = command

class exceptions(object):

    class bad_arguments_error(Exception):
        pass

class commands_mixin(object):
    """Command support."""
    __commands__ = []

    def init(self):
        self.__commands = commandgroup(self.NAME)
        self.__init()

    def __init(self):
        for cmdfunc in self.__class__.__commands__:
            name = split_function_name(cmdfunc.func_name)
            selffunc = getattr(self, cmdfunc.func_name)
            self.__commands.new(name, selffunc, [])

    def get_commands(self):
        return self.__commands
    commands = property(get_commands)

    def call(self, commandname, **kw):
        command = self.commands.get(commandname)
        if command is not None:
            self.log.debug('calling "%s" with "%s"', commandname, kw)
            result = self.__call_command(command, **kw)
            self.log.debug('called "%s" with result "%s"',
                           commandname, result)
            return result
        else:
            raise CommandNotFoundError(commandname)

    def __call_command(self, command, **kw):
        return command(**kw)

    def call_external(self, servicename, commandname, **kw):
        svc = self.get_service(servicename)
        return svc.call(commandname, **kw)

