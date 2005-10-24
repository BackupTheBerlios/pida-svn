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
import os
import mimetypes
import stat
import gobject
import base
class Buffer(base.pidaobject):

    actions = [('undo', 'undo', 'undo'),
               ('redo', 'redo', 'redo'),
               ('close', 'close', 'close'),
               ('filemanager', 'filemanager', 'filemanager'),
               ('terminal', 'terminal', 'terminal')]
    contexts = ['file']
    
    def __init__(self, filename):
        self.__filename = filename
        self.__reset()

    def __reset(self):
        self.__lines = []
        self.__string = ''
        self.__stat = self.__load_stat()
        self.__mimetype = None
        
    def __iter__(self):
        if self.__lines == []:
            for line in self.__load_lines():
                yield line
        else:
            for line in self.__lines:
                yield line

    def __len__(self):
        return self.__stat[stat.ST_SIZE]
    length = property(__len__)

    def __load_lines(self):
        try:
            f = open(self.__filename)
        except IOError:
            return
        for line in f:
            self.__lines.append(line)
        self.__string = ''.join(self.__lines)
        f.close()

    def __load_stat(self):
        try:
            stat_info = os.stat(self.__filename)
        except OSError:
            stat_info = [0] * 10
        return stat_info

    def __get_filename(self):
        return self.__filename
    filename = property(__get_filename)

    def __get_lines(self):
        if self.__lines == []:
            self.__load_lines()
        return self.__lines
    lines = property(__get_lines)
    
    def __get_string(self):
        if self.__string == '':
            self.__load_lines()
        return self.__string
    string = property(__get_string)
        
    def __get_stat(self):
        return self.__stat
    stat = property(__get_stat)

    def __get_mimetype(self):
        if self.__mimetype is None:
            mime_type, encoding = mimetypes.guess_type(self.__filename)
            if mime_type is None:
                self.__mimetype = ('', '')
            else:
                self.__mimetype = tuple(mime_type.split('/'))
        return self.__mimetype
    mimetype = property(__get_mimetype)

    def get_parent_directory(self):
        directory = os.path.split(self.filename)[0]
        return directory
    directory = property(get_parent_directory)

    def poll(self):
        new_stat = self.__load_stat()
        if new_stat.st_mtime != self.__stat.st_mtime:
            self.__stat = new_stat
            self.__reset()
            return True
        else:
            return False
    
    def get_markup(self):
        """Return the markup for the item."""
        MU = ('<span size="small">'
              '<span foreground="#0000c0">%s/</span>'
              '<b>%s</b>'
              '</span>')
        fp = self.filename
        fd, fn = os.path.split(fp)
        dp, dn = os.path.split(fd)
        return MU % (dn, fn)
    markup = property(get_markup)

    def action_close(self):
        self.boss.command('buffermanager', 'close-current-file')

    def action_terminal(self):
        self.boss.command('terminal', 'execute-vt-shell',
        kwargs={'directory': self.directory})

    def action_filemanager(self):
        self.boss.command('filemanager', 'browse', directory=self.directory)

        


import tempfile

class TemporaryBuffer(Buffer):

    actions = [('save', 'save', 'save'),
               ('undo', 'undo', 'undo'),
               ('redo', 'redo', 'redo'),
               ('close', 'close', 'close')]

    contexts = []

    def __init__(self, prefix, name):
        self.__prefix = prefix
        self.__name = name
        self.__file, self.__filename = tempfile.mkstemp(prefix='%s_' % prefix,
                                                        suffix='_%s' % name)
        Buffer.__init__(self, self.__filename)
        print self.boss

    def get_file(self):
        return self.__filename
    file = property(get_file)

    def get_markup(self):
        """Return the markup for the item."""
        MU = ('<span size="small">'
              '<span foreground="#00c000">%s/</span>'
              '<b>%s</b>'
              '</span>')
        return MU % (self.__prefix, self.__name)
    markup = property(get_markup)
    details = markup

    def action_save(self):
        self.boss.command('buffermanager', 'rename-buffer', buffer=self,
                          filename='foo')



#b = Buffer('/home/ali/linkser.pyi')
#print b.mimetype
#print len(b), b.length
##print b.stat
#print b.string
