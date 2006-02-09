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
import gobject
import subprocess
import threading
import pty
import sys
import os
import pida.core.service as service
import pida.pidagtk.contentview as contentview
import pida.core.registry as registry
import rlcompleter
import pida.utils.pyconsole as pyconsole

class Holder(object):
    def __init__(self, name):
        self.__name = name

    def __repr__(self):
        return self.__name

defs = service.definitions

class PytermContent(contentview.content_view):

    ICON_NAME = 'manhole'

    SHORT_TITLE = 'manhole'

    LONG_TITLE = 'PIDA internal shell'

    BORDER = 4

    def init(self, localdict):
        console = pyconsole.Console(locals=localdict,
                                    banner="PIDA Shell. Keep breathing.",
                                    use_rlcompleter=False)
        sw = gtk.ScrolledWindow()
        self.widget.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(console)
        self.show_all()

class Manhole(service.service):
    """Debugging Python shell."""
    NAME = 'manhole'

    
    class Manhole(defs.View):
        view_type = PytermContent
        book_name = 'plugin'

    def cmd_run(self):
        localdict = {'pida':self.boss,
                     'cmd':self.get_commands()}
        content = self.create_view('Manhole', localdict=localdict)
        self.show_view(view=content)

    def act_run_manhole(self, action):
        """Run the internal manhole shell."""
        self.call('run')

    def get_commands(self, group=None):
        L = []
        H = Holder('cmd')
        command_groups = self.boss.services
        if group is not None:
            command_groups = filter(lambda c: c.name == group, command_groups)
        for command_group in command_groups:
            setattr(H, command_group.NAME, Holder(command_group.NAME))
            J = getattr(H, command_group.NAME)
            for command in command_group.commands:
                setattr(J, command.name.replace('-', '_'), command)
                L.append((command_group.NAME, command.name))
        return H

    def ex(self, commandline):
        self.boss.command('terminal', 'execute-line', commandline=commandline)

    def test_vcs(self):
        self.boss.command('versioncontrol', 'call', command='status',
                           directory = '/home/ali/working/pida/pida/trunk')

    def test_hidden(self):
        def p(data):
            self.log_debug("&&" + data)
        self.boss.command('versioncontrol', 'get-statuses',
                           datacallback=p,
                           directory='/home/ali/working/pida/pida/trunk')

    def toolbar_action_commands(self):
        self.list_commands()

    def get_menu_definition(self):
        return """
        <menubar>
        <menu name="base_tools" action="base_tools_menu">
        <menu name="base_pida" action="base_pida_menu">
        <separator />
        <menuitem name="manhole+run" action="manhole+run_manhole" />
        </menu>
        </menu>
        </menubar>        
        """


import code
import termios
import tty
class Interpreter(code.InteractiveConsole, object):

    def __init__(self, fd, localdict={}):
        self.__fd = fd
        code.InteractiveConsole.__init__(self, localdict)
        gobject.io_add_watch(fd, gobject.IO_IN, self.cb_stdin)
        self.__buffer = ''
        self.write_banner()
        self.write_ps()
        self.__completer = Completer(localdict)

    def write(self, data):
        os.write(self.__fd, data)

    def cb_stdin(self, fd, cond):
        data = os.read(fd, 1024)
        self.__buffer = '%s%s' % (self.__buffer, data)
        if '\n' in self.__buffer:
            lines = self.__buffer.splitlines()
            command = lines.pop(0)
            self.__buffer = '\n'.join(lines)
            t = threading.Thread(target=self.push, args=[command])
            t.run()
        return True

    def write_ps(self, more=False):
        if more:
            self.write('... ')
        else:
            self.write('>>> ')

    def write_banner(self):
        self.write("PIDA Python Shell.\n"
                   "Be careful, you are inside the PIDA main loop.\n")

    def __get_completer(self):
        return self.__completer
    completer = property(__get_completer)

    def push(self, command):
        tempstdout = sys.stdout
        sys.stdout = Stdout(self)
        more = code.InteractiveConsole.push(self, command)
        sys.stdout = tempstdout
        self.write_ps(more)
        
class Stdout(object):

    def __init__(self, interpreter):
        self.__interpreter = interpreter

    def write(self, data):
        self.__interpreter.write(data)

class Completer(object):
  """
  Taken from rlcompleter, with readline references stripped, and a local dictionary to use.
  """
  def __init__(self,locals):
    self.locals = locals

  def complete(self, text, state):
    """Return the next possible completion for 'text'.
    This is called successively with state == 0, 1, 2, ... until it
    returns None.  The completion should begin with 'text'.

    """
    if state == 0:
      if "." in text:
        self.matches = self.attr_matches(text)
      else:
        self.matches = self.global_matches(text)
    try:
      return self.matches[state]
    except IndexError:
      return None

  def global_matches(self, text):
    """Compute matches when text is a simple name.

    Return a list of all keywords, built-in functions and names
    currently defines in __main__ that match.

    """
    import keyword
    matches = []
    n = len(text)
    for list in [keyword.kwlist, __builtin__.__dict__.keys(), self.locals.keys()]:
      for word in list:
        if word[:n] == text and word != "__builtins__":
          matches.append(word)
    return matches

  def attr_matches(self, text):
    """Compute matches when text contains a dot.

    Assuming the text is of the form NAME.NAME....[NAME], and is
    evaluatable in the globals of __main__, it will be evaluated
    and its attributes (as revealed by dir()) are used as possible
    completions.  (For class instances, class members are are also
    considered.)

    WARNING: this can still invoke arbitrary C code, if an object
    with a __getattr__ hook is evaluated.

    """
    import re
    m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
    if not m:
      return
    expr, attr = m.group(1, 3)
    object = eval(expr, self.locals, self.locals)
    words = dir(object)
    if hasattr(object,'__class__'):
      words.append('__class__')
      words = words + get_class_members(object.__class__)
    matches = []
    n = len(attr)
    for word in words:
      if word[:n] == attr and not word.startswith('__'):
        matches.append("%s.%s" % (expr, word))
    return matches

def get_class_members(klass):
  ret = dir(klass)
  if hasattr(klass,'__bases__'):
     for base in klass.__bases__:
       ret = ret + get_class_members(base)
  return ret

Service = Manhole

