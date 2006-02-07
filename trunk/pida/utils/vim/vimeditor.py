# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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

import os

import pida.core.service as service
from pida.core import errors

defs = service.definitions
types = service.types

import vimcom

class vim_editor(object):

    class display(defs.optiongroup):
        class colour_scheme(defs.option):
            """The colour scheme to use in vim (Empty will be ignored)."""
            rtype = types.string
            default = ''
        class hide_vim_menu(defs.option):
            """Whether the vim menu will be hidden."""
            rtype = types.boolean
            default = False

    def init(self):
        self.__files = {}
        self.__old_shortcuts = {'n':{}, 'v':{}}
        self.__currentfile = None
        self.__cw = vimcom.communication_window(self)

    def get_server(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def vim_new_serverlist(self, serverlist):
        raise NotImplementedError

    def cmd_start(self):
        self.start()

    def cmd_revert(self):
        self.__cw.revert(self.server)

    def cmd_close(self, filename):
        self.__cw.close_buffer(self.server, filename)

    def cmd_edit(self, document):
        """Open and edit."""
        filename = document.filename
        self.boss.call_command('documenttypes',
                               'disable_document_accelerators')
        if filename != self.__currentfile:
            if filename in self.__files.setdefault(self.server, []):
                self.__cw.change_buffer(self.server, filename)
                self.__cw.foreground(self.server)
            else:
                found = False
                for server in self.__files:
                    serverfiles = self.__files[server]
                    if filename in serverfiles:
                        self.__cw.change_buffer(server, filename)
                        self.__cw.foreground(server)
                        found = True
                        break
                if not found:
                    self.__cw.open_file(self.server, filename)
                    self.__files[self.server].append(filename)
            self.__currentfile = filename
        if self.single_view is not None:
            self.single_view.raise_page()
            self.single_view.long_title = filename

    def cmd_undo(self):
        self.__cw.undo(self.server)

    def cmd_redo(self):
        self.__cw.redo(self.server)

    def cmd_cut(self):
        self.__cw.cut(self.server)

    def cmd_copy(self):
        self.__cw.copy(self.server)

    def cmd_paste(self):
        self.__cw.paste(self.server)

    def cmd_save(self):
        self.__cw.save(self.server)

    def cmd_goto_line(self, linenumber):
        self.__cw.goto_line(self.server, linenumber)

    def __load_shortcuts(self):
        for mapc in ['n']:
            if self.__old_shortcuts[mapc].setdefault(self.server, []):
                for sc in self.__old_shortcuts[mapc][self.server]:
                    self.__cw.send_ex(self.server, UNMAP_COM % (mapc, sc))
            self.__old_shortcuts[mapc][self.server] = []
            #l = self.options.get('shortcut-leader').value
            globalkpsopts = self.boss.option_group('keyboardshortcuts')
            globalkps = []
            for opt in globalkpsopts:
                vals = opt.value().split()
                if len(vals) == 2:
                    mod, k = vals
                v = '<lt>%s-%s>' % (mod, k)
                globalkps.append((v, '''Async_event("globalkp,%s")''' %
                                  opt.value().replace('\\', '\\\\')))
            def load():
                for c, command in globalkps:
                    try:
                        #c = self.options.get(name).value()
                        sc = ''.join([l, c])
                        self.__old_shortcuts[mapc][self.server].append(sc)
                        self.__cw.send_ex(self.server, NMAP_COM % (mapc, c, command))
                    except errors.BadRegistryKeyError:
                        pass
            gobject.timeout_add(200, load)

    def reset(self):
        colorscheme = self.opt('display', 'colour_scheme')
        if colorscheme:
            self.__cw.set_colorscheme(self.server, colorscheme)
        if self.opt('display', 'hide_vim_menu'):
            self.__cw.set_menu_visible(self.server, False)
            #self.__load_shortcuts()

    def open_file_line(self, filename, linenumber):
        if self.__currentfile != filename:
            self.open_file(filename)
            self.__bufferevents.append([self.goto_line, (linenumber, )])
        else:
            self.goto_line(linenumber)

    def goto_line(self, linenumber):
        self.__cw.change_cursor(self.server, 1, linenumber)

    def vim_bufferchange(self, server, cwd, filename):
        if not filename:
            return
        if os.path.abspath(filename) != filename:
            filename = os.path.join(cwd, filename)
        self.log.debug('vim buffer change "%s"', filename)
        if filename != self.__currentfile:
            self.__currentfile = filename
            if filename not in self.__files.setdefault(server, []):
                self.__files[server].append(filename)
            self.boss.call_command('buffermanager', 'open_file',
                                    filename=filename)

    def vim_bufferunload(self, server, filename, *args):
        self.log.debug('vim unloaded "%s"', filename)
        if filename != '':
            # unloaded an empty new file
            if filename in self.__files.setdefault(server, []):
                self.__files[server].remove(filename)
                self.boss.call_command('buffermanager', 'file_closed',
                                        filename=filename)
                self.__currentfile = None
            else:
                self.log.info('vim unloaded an unknown file %s', filename)

    def vim_filesave(self, server, *args):
        self.boss.call_command('buffermanager', 'reset_current_document')

    def vim_globalkp(self, server, name):
        self.boss.command('keyboardshortcuts', 'keypress-by-name',
                           kpname=name)

    def vim_shutdown(self, server, *args):
        self.clean_after_shutdown(server)
        self.after_shutdown(server)

    def clean_after_shutdown(self, server):
        for filename in self.__files.setdefault(server, []):
            self.boss.call_command('buffermanager', 'file_closed',
                                    filename=filename)
        self.__files = {}
        self.__currentfile = None

    def after_shutdown(self, server):
        pass

    def get_vim_window(self):
        return self.__cw
    vim_window= property(get_vim_window)

    def get_current_file(self):
        return self.__currentfile
    current_file = property(get_current_file)

