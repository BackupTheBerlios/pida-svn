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
import time
import tempfile

import actions

class document_handler(actions.action_handler):
    
    globs = []
    type_name = 'document'

    def init(self):
        self.__filenames = {}
        self.__docids = {}

    def create_document(self, filename):
        pass

    def view_document(self, document):
        pass


class document(base.pidacomponent):
    """Base document class."""
    contexts = []

    icon_name = None

    markup_prefix = ''
    markup_attributes = ['filename']
    markup_string = '%(filename)s'

    def __init__(self, filename=None,
                       markup_attributes=None,
                       markup_string=None,
                       contexts=None,
                       icon_name=None,
                       handler=None):
        self.__handler = handler
        self.__filename = filename
        self.__unique_id = time.time()
        if markup_attributes is not None:
            self.markup_attributes = markup_attributes
        if markup_string is not None:
            self.markup_string = markup_string
        base.pidacomponent.__init__(self)

    def get_filename(self):
        return self.__filename
    filename = property(get_filename)

    def get_unique_id(self):
        return self.__unique_id
    unique_id = property(get_unique_id)

    def get_markup(self):
        prefix = '<b><tt>%s </tt></b>' % self.markup_prefix
        s = self.markup_string % self.__build_markup_dict()
        return '%s%s' % (prefix, s)
    markup = property(get_markup)

    def __build_markup_dict(self):
        markup_dict = {}
        for attr in self.markup_attributes:
            markup_dict[attr] = getattr(self, attr)
        return markup_dict

    def get_handler(self):
        return self.__handler
    handler = property(get_handler)


class filesystem_document(document):
    """Any file system object"""
    def get_parent_directory(self):
        directory = os.path.split(self.filename)[0]
        return directory
    directory = property(get_parent_directory)


class directory_document(filesystem_document):
    """A directory on disk"""
    contexts = ['directory']


class dummyfile_document(document):
    """A totally fake document."""
    contexts = []
    lines = []

    

class realfile_document(document):
    """A real file on disk."""
    icon_name = 'new'

    markup_prefix = ''
    markup_directory_color = '#0000c0'
    markup_attributes = ['directory_basename', 'basename', 'directory_colour']
    markup_string = ('<span color="%(directory_colour)s">%(directory_basename)s</span>/'
                     '<b>%(basename)s</b>')

    is_new = False
                     
    def init(self):
        self.__reset()

    def __reset(self):
        self.__lines = None
        self.__string = None
        self.__stat = None
        self.__mimetype = None
    reset = __reset
        
    def __load(self):
        if self.__stat is None:
            self.__stat = self.__load_stat()
        if self.__lines is None:
            self.__lines = self.__load_lines()
        if self.__mimetype is None:
            self.__mimetype = self.__load_mimetype()

    def __load_lines(self):
        self.__lines = []
        try:
            f = open(self.filename)
            for line in f:
                self.__lines.append(line)
            self.__string = ''.join(self.__lines)
            f.close()
        except IOError:
            self.log.warn('failed to open file %s', self.filename)
        return self.__lines

    def __load_stat(self):
        try:
            stat_info = os.stat(self.filename)
        except OSError:
            stat_info = None
        return stat_info

    def __load_mimetype(self):
        typ, encoding = mimetypes.guess_type(self.filename)
        if typ is None:
            mimetype = ('', '')
        else:
            mimetype = tuple(typ.split('/'))
        return mimetype

    def __iter__(self):
        self.__load()
        for line in self.__lines:
            yield line

    def get_lines(self):
        return [line for line in self]

    lines = property(get_lines)

    def __len__(self):
        self.__load()
        return self.__stat[stat.ST_SIZE]

    length = property(__len__)
    
    def __get_string(self):
        self.__load()
        return self.__string

    string = property(__get_string)
        
    def __get_stat(self):
        return self.__stat

    stat = property(__get_stat)

    def __get_mimetype(self):
        return self.__mimetype

    mimetype = property(__get_mimetype)

    def get_directory(self):
        return os.path.dirname(self.filename)
    directory = property(get_directory)

    def get_directory_basename(self):
        return os.path.basename(self.directory)

    directory_basename = property(get_directory_basename)

    def get_basename(self):
        return os.path.basename(self.filename)

    basename = property(get_basename)

    def get_directory_colour(self):
        return self.markup_directory_color
    directory_colour = property(get_directory_colour)

    def poll(self):
        self.__load()
        new_stat = self.__load_stat()
        if new_stat is None:
            return False
        if new_stat.st_mtime != self.__stat.st_mtime:
            self.__stat = new_stat
            self.__reset()
            return True
        else:
            return False

    def poll_until_change(self, callback, delay=1000):
        def do_poll():
            poll = self.poll()
            if poll:
                callback()
                return False
            else:
                return True
        gobject.timeout_add(delay, do_poll)


class temporary_document(realfile_document):
    """A temporary file on disk"""
    contexts = ['temporary']


    markup_prefix = 'tp'
    markup_directory_color = '#600060'
    markup_attributes = ['title', 'prefix', 'directory_colour']
    markup_string = ('<span color="%(directory_colour)s">%(title)s</span> '
                     '<b>%(prefix)s</b>')
    

    def __init__(self, filename, handler, prefix, title):
        self.__prefix = prefix
        self.__title = title
        f, filename = tempfile.mkstemp(prefix=prefix)
        os.close(f)
        realfile_document.__init__(self, filename=filename, handler=handler)

    def get_title(self):
        return self.__title
    title = property(get_title)
        
    def get_prefix(self):
        return self.__prefix
    prefix = property(get_prefix)


