# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005, 2006 Bernard Pratz aka Guyzmo, guyzmo@m0g.net

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

import pida.pidagtk.tree as tree
import pida.pidagtk.configview as configview
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.contentview as contentview
import pida.pidagtk.contextwidgets as contextwidgets

import pida.core.registry as registry
import pida.core.service as service
types = service.types
defs = service.definitions

import os
import os.path
import datetime
import urllib
import threading

import gtk
import gobject

class annotation(object):
    '''
    Defines an anotation object
    
    Still not finished... Has to be used and tested
    '''
    def __init__(self,paste):
        self.init()
        self.__paste = paste

    def init(self):
        self.__title = ''
        self.__option = None
        self.__input = None

    '''Setters'''

    def set_title(self,title):
        '''Sets the title'''
        self._title = title

    def set_options(self,options):
        '''Sets the options'''
        self._option = options

    def set_inputs(self,inputs):
        '''Sets the inputs'''
        self._input = inputs

    def set_text(self,text):
        '''Sets the text'''
        self._text = text

    def set_mgr(self, mgr):
        '''Sets the Tree, for latter callback'''
        self.__paste.set_mgr(mgr)

    '''Getters'''

    def get_date(self):
        '''Gets the date'''
        return self.__paste.get_date()
    date = property(get_date)

    def get_name(self):
        '''Gets the nickname'''
        return self.__paste.get_name()
    name = property(get_name)

    def get_pass(self):
        '''Gets the password'''
        return self.__paste.get_name()
    passwd = property(get_pass)

    def get_option(self, key):
        '''Get the option referenced by key'''
        if self._option != None:
            if self._option.has_key(key):
                return self._option[key]
        return None

    def get_syntax(self):
        '''Get the syntax if any. 
           Returns Default otherwise'''
        syntax = self.get_option('Syntax')
        if syntax != None:
            return syntax
        return 'Default'
    syntax = property(get_syntax)

    def get_input(self, key):
        '''Gets the input referenced by key'''
        if self._input != None:
            if self._input.has_key(key):
                return self._input[key]
        return None

    def get_text(self):
        '''Gets the annotation's text'''
        return self._text
    text = property(get_text)

    def get_title(self):
        '''Gets the annotation's title'''
        if self._title != '':
            return self._title
        return '[Untitled]'
    title = property(get_title)

    def get_url(self):
        '''Gets the paste's URL'''
        return self.__paste.get_url()
    url = property(get_url)

class paste_bin(object):
    '''Virtual type who defines a Paste bound to a pastebin'''
    URL = None
    OPTIONS = None
    INPUTS = None
        
    '''Initializator'''
    def init(self):
        self.readbuffer = []
        self._date = datetime.datetime.now()
        self._title = ""
        self._name = ""
        self._pass = ""
        self._chan = ""
        self._lang = ""
        self._text = ""
        self._url = ""
        self._option = {}
        self._input = {}

    '''Constructor'''
    def __init__(self):
        self.init()

    '''Resets the current paste'''
    def reset(self):
        self.init()

    '''Virtual method to post the current paste'''
    def paste(self):
        '''Method to actually do the paste'''
        self.post(())

    '''Setters'''

    def set_title(self,title):
        self._title = title

    def set_name(self,name):
        '''Sets the user's name'''
        self._name = name

    def set_pass(self,password):
        '''Sets the user's password for the site'''
        self._pass = password

    def set_options(self,options):
        self._option = options

    def set_inputs(self,inputs):
        self._input = inputs

    def set_text(self,text):
        '''Sets the text'''
        self._text = text

    def set_url(self,url):
        '''Sets the URL'''
        self._url = url

    def set_mgr(self, mgr):
        '''Sets the Tree, for latter callback'''
        self.__pastes = mgr

    def set_pulse(self, pulse):
        '''Sets the Pulse bar, for latter callback'''
        self.__pulse_bar = pulse

    def set_editor(self, editor):
        self.__editor = editor

    def set_id(self, id):
        self.__id = id

    '''Getters'''

    def get_date(self):
        '''Gets the date'''
        return self._date
    date = property(get_date)

    def get_name(self):
        '''Gets the nickname'''
        return self._name
    name = property(get_name)

    def get_pass(self):
        '''Gets the password'''
        return self._pass
    passwd = property(get_pass)

    def get_option(self, key):
        if self._option != {}:
            if self._option.has_key(key):
                return self._option[key]
        return None

    def get_syntax(self):
        syntax = self.get_option('Syntax')
        if syntax != None:
            return syntax
        return 'Default'
    syntax = property(get_syntax)

    def get_input(self, key):
        if self._input != {}:
            if self._input.has_key(key):
                return self._input[key]
        return None

    def get_text(self):
        '''Gets the paste's text'''
        return self._text
    text = property(get_text)

    def get_title(self):
        '''Gets the paste's title'''
        if self._title != '':
            return self._title
        return '[Untitled]'
    title = property(get_title)

    def get_url(self):
        '''Gets the paste's URL'''
        return self._url
    url = property(get_url)

    def get_id(self):
        '''for recognition of the paste'''
        return self._id
    id = property(get_id)

    def __wait_editor(self):
        self.__editor.service.single_view.pulse()

    def __close_editor(self):
        self.__editor.service.single_view.stop_pulse()
        self.__editor.close()

    def retrieve_data(self):
        '''Retrieve data from the site to update LANGS and CHANNELS'''
        pass

    def post(self, dataopts, text):
        '''Method to connect to the site, parse attributes and post the paste'''
        def t():
            data = urllib.urlencode(dataopts)
            page = urllib.urlopen(self.URL, data)
            gtk.threads_enter()
            gobject.io_add_watch(page, gobject.IO_IN, self.readable, text)
            gtk.threads_leave()
        t = threading.Thread(target=t)
        self.__wait_editor()
        t.start()

    def readable(self, fd, cond, text):
        '''If data can be read from the fd, returns true to keep the connection
           online (io_watch watching), or appends to the buffer'''
        data = fd.read(16)
        if not data:
            self.received(fd.geturl(), ''.join(self.readbuffer), text)
            self.readbuffer = []
            return False
        else:
            self.readbuffer.append(data)
            return True

    def received(self, url, page, text):
        '''Sets the members when getting paste url'''
        url = self.parse(url, page)
        self.set_text(text)
        self.set_url(url)
        gtk.threads_enter()
        self.__pastes.push(self)
        self.__close_editor()
        gtk.threads_leave()

    def parse(self, url, page):
        '''Returns the url to the paste'''
        return url

class rafb_paste_bin(paste_bin):
    '''Rafb paste bin handler'''
    URL = 'http://www.rafb.net/paste/paste.php'
    OPTIONS = {'Syntax':['C89', 'C', 'C++', 'C#', 'Java', 'Pascal', 'Perl', 
                          'PHP', 'PL/I', 'Python', 'Ruby', 'SQL', 'VB', 
                          'Plain Text']}
#    INPUTS = {'foo':'bar'}

    def paste(self):
        dataopts = [('text', self.text),
                    ('name', self.name),
                    ('desc', self.title),
                    ('lang', self.syntax),
                    ('cvt_tabs', 4),
                    ('submit', 'Paste')]
        self.post(dataopts, self.get_text())


class pida_paste_bin(paste_bin):
    '''Pida's paste bin handler'''

    URL = 'http://pseudoscience.co.uk:8080/freenode/pida/PasteBin'

    def paste(self):
        dataopts = [('nick', self.get_name()),
                    ('text', self.get_text())]
        self.post(dataopts, self.get_text())

    def parse(self, url, page):
        for s in page.split():
            if s.startswith('href'):
                if s.count('view='):
                    for t in s.split('"'):
                        if t.startswith('/'):
                            return self.URL+'?'+t.split('?')[1]
        return "Error: URL uncaught :("

class lisp_paste_bin(paste_bin):
    '''Lisp.org paste bin handler'''

    URL = 'http://paste.lisp.org/submit'

    OPTIONS = {
    # TODO: make it dynamic and parsed from http://paste.lisp.org/new
     'Channel':['#lisp','#scheme','#opendarwin','#macdev','#fink','#jedit',
                 '#DYLAN','#emacs','#xemacs','#colloquy','#adium','#growl',
                 '#CHICKEN','#quicksilver','#svn','#slate','#squeak','#wiki',
                 '#nebula','#myko','#lisppaste','#pearpc','#fpc','#hprog',
                 '#concatenative','#slate-users','#swhack','#ud','#t',
                 '#compilers','#erights','#esp','#scsh','#sisc','#haskell',
                 '#rhype','#sicp','#darcs','#hardcider','#lisp-it','#webkit',
                 '#launchd','#mudwalker','#darwinports','#muse','#chatkit',
                 '#kowaleba','#vectorprogramming','#opensolaris',
                 '#oscar-cluster','#ledger','#cairo','#idevgames','#hug-bunny',
                 '##parsers','#perl6','#sdlperl','#ksvg','#rcirc','#code4lib'],
     'Syntax':['','None','Basic Lisp','Scheme','Emacs Lisp','Common Lisp','C',
                'C++','Java','Objective C']
               }

    def paste(self):
        dataopts = [('chan', self.get_option('Channel')),
                    ('username', self.get_name()),
                    ('title', self.get_title),
                    ('colorize', self.get_option('Syntax')),
                    ('text', self.get_text())]
        self.post(dataopts, self._text)

    def parse(self, url, page):
        for s in page.split():
            if s.startswith('HREF'):
                if s.count('display/'):
                    return s.split('"')[1]
        return "Error: URL uncaught :("

class husk_paste_bin(paste_bin):
    '''husk.org paste bin handler'''

    URL = 'http://paste.husk.org'

    # TODO: make it dynamic and parsed from http://paste.husk.org/
    OPTIONS = {'Channel':['','#2lmc','#axkit','#axkit-dahut','#bots',
                '#dbix-class','#fotango','#london.pm','#openguides','#p5p',
                '#parrot','#perl','#siesta','#spamassassin','#thegestalt','#void']}

    def paste(self):
        dataopts = [('nick', self.get_name()),
                    ('summary', self.get_title()),
                    ('paste', self.get_text()),
                    ('Paste+it', 'Paste+it')]
        self.post(dataopts, self.get_text())

    # Does not work, doesn't parse the right page
    def parse(self, url, page):
        for s in page.split():
            if s.startswith('href'):
                if s.count('display/'):
                    return s.split('"')[1]
        return "Error: URL uncaught :("

# pastebin.ca
# pastebin.com
BINS = {'#pida pastebin':pida_paste_bin,
        'rafb.net':rafb_paste_bin,
        'lisp.org paste':lisp_paste_bin,
        'husk.org paste':husk_paste_bin,}

