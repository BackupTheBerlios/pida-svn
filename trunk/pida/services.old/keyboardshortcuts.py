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
import pida.core.registry as registry
import gtk

KEYS = [('shrink-viewbook', 'C 1',
            ('window', 'shrink-viewbook', {})),
        ('shrink-contentbook', 'C 2',
            ('window', 'shrink-contentbook', {})),
        ('toggle-viewbook', 'C a',
            ('window', 'toggle-viewbook', {})),
        ('toggle-contentbook', 'C s',
            ('window', 'toggle-contentbook', {})),
        ('new-terminal', 'C t',
            ('terminal', 'execute-vt-shell', {})),
        ('python-terminal', 'C p',
            ('terminal', 'execute-py-shell', {})),
        ('vcs-commit-buffer', 'C i',
            ('versioncontrol', 'commit-current-file', {})),
        ('vcs-diff-buffer', 'C o',
            ('versioncontrol', 'diff-current-file', {})),
        ('vcs-up', 'C u',
            ('versioncontrol', 'update', {}))]

def build_map():
    keymap = {}
    for name, default, command in KEYS:
        keymap[name] = command
    return keymap


def build_options():
    for name, default, command in KEYS:
        yield (name,
               'The shortcut key for %s' % name,
               default,
               registry.RegistryItem)

class Keycuts(service.Service):
    NAME = 'keyboardshortcuts'
    OPTIONS = build_options()
    COMMANDMAP = build_map()

    COMMANDS = [('keypress-by-name', [('kpname', True)])]

    def populate(self):
        self.__accel = None
        self.__map = {}
        self.__namemap = {}

    def reset(self):
        window = self.boss.get_main_window()
        if self.__accel is not None:
            window.remove_accel_group(self.__accel)
        self.__accel = gtk.AccelGroup()
        self.__map = {}
        window.add_accel_group(self.__accel)
        for option in self.options:
            vals = option.value().split()
            if len(vals) == 2:
                mods, key = vals
                if len(key) > 1:
                    key = key[0]
                mod = gtk.accelerator_get_default_mod_mask()
                if 'M' in mods:
                    mod = mod & gtk.gdk.MOD1_MASK
                if 'S' in mods:
                    mod = mod & gtk.gdk.SHIFT_MASK
                if 'C' in mods:
                    mod = mod & gtk.gdk.CONTROL_MASK
                keyval = ord(key)
                self.__accel.connect_group(keyval, mod, gtk.ACCEL_VISIBLE,
                                           self.cb_keypress)
                self.__map[(keyval, mod)] = self.COMMANDMAP[option._name]
                self.__namemap[option.value()] = self.COMMANDMAP[option._name]

    def cb_keypress(self, group, table, keyval, modifier):
        service, command, argdict = self.__map[(keyval, modifier)]
        self.boss.command(service, command, **argdict)

    def cmd_keypress_by_name(self, kpname):
        if kpname in self.__namemap:
            service, command, argdict = self.__namemap[kpname]
            self.boss.command(service, command, **argdict)
                
    def get_accel_group(self):
        return self.__accel
    accel_group = property(get_accel_group)

Service = Keycuts
