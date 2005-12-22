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
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.contentview as contentview
import pida.pidagtk.filedialogs as filedialogs
import pida.pidagtk.tree as tree

#import pida.utils.pygrep as pygrep

import os
import re
import time
import glob
import gobject
import threading
import linecache
import cgi

import gtk

EXPANDER_LABEL_MU = '<span size="small">Details</span>'
RESULTS_LABEL_MU = '<span size="small">Results</span>'
DIR_ENTRY_MU = '<span>Search Path </span>'
CURRENT_ONLY_MU = '<span> Search only current buffer</span>'

RESULT_MU = ('<span>'
                '<span color="#0000c0">%s</span>:'
                '<span weight="bold">%s</span>\n'
                '<tt>%s</tt>'
             '</span>')

RESULT_CONTEXT_MU = ('<span><tt>%s\n'
                     '<span weight="bold">%s</span>\n%s</tt></span>')

SMALL_MU = ('<span size="small" weight="bold">%s</span>')

class ResultsTreeItem(tree.TreeItem):
    
    def get_markup(self):
        return RESULT_MU % (self.value.linenumber,
                            cgi.escape(self.value.filename),
                            self.value.muline)
    markup = property(get_markup)

class ResultsTree(tree.Tree):
    pass

class GrepView(contentview.content_view):

    ICON_NAME = 'find'
    SHORT_TITLE = 'Find '

    LONG_TITLE = 'Find text in files.'

    def init(self):
        # Die RAD!
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False, padding=2)
        self.__pattern_entry = gtk.Entry()
        hb.pack_start(self.__pattern_entry)
        l = gtk.Label()
        l.set_markup(SMALL_MU % 'in')
        hb.pack_start(l, expand=False)
        self.__path_entry = filedialogs.FolderButton()
        hb.pack_start(self.__path_entry)
        self.__recursive = gtk.CheckButton('-R')
        hb.pack_start(self.__recursive, expand=False)
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False)
        self.__status_bar = gtk.ProgressBar()
        self.__status_bar.set_size_request(-1, 32)
        self.__status_bar.set_pulse_step(0.01)
        hb.pack_start(self.__status_bar, padding=4)
        self.__stop_but = gtk.Button(stock=gtk.STOCK_STOP)
        hb.pack_start(self.__stop_but, expand=False)
        self.__stop_but.set_sensitive(False)
        self.__stop_but.connect('clicked', self.cb_stop_clicked)
        self.__start_but = gtk.Button(stock=gtk.STOCK_FIND)
        hb.pack_start(self.__start_but, expand=False)
        self.__start_but.connect('clicked', self.cb_start_clicked)
        #self.add_button('apply', 'apply', 'Start the search')
        #self.add_button('stop', 'stop', 'Stop the search')
        hb = gtk.HBox()
        l = gtk.Label()
        hb.pack_start(l, expand=True)
        l.set_markup(EXPANDER_LABEL_MU)
        self.__details_expander = gtk.Expander()
        self.__details_expander.set_label_widget(hb)
        self.widget.pack_start(self.__details_expander, expand=False)
        details_box = gtk.Table(4, 3)
        self.__details_expander.add(details_box)
        details_box.set_col_spacings(4)
        self.__dir_box = gtk.HBox()
        details_box.attach(self.__dir_box, 1, 3, 0, 1)
        self.__ignore_vcs = gtk.CheckButton("Ignore Version Control Directories")
        details_box.attach(self.__ignore_vcs, 0, 1, 1, 2)
        resbox = gtk.HBox()
        self.widget.pack_start(resbox)
        butbox = gtk.VButtonBox()
        resbox.pack_start(butbox, expand=False)
        self.__results_tree = tree.Tree()
        self.__results_tree.set_property('markup-format-string', '%(markup)s')
        resbox.pack_start(self.__results_tree)
        self.__results_tree.connect('clicked', self.cb_result_selected)
        self.__results_tree.connect('double-clicked', self.cb_result_activated)
        self.__context_expander = gtk.Expander(label=RESULTS_LABEL_MU)
        self.__context_expander.set_use_markup(True)
        self.widget.pack_start(self.__context_expander, expand=False)
        self.__context_expander.set_expanded(True)
        contextbox = gtk.HBox()
        self.__context_expander.add(contextbox)
        self.__context_label = gtk.Label()
        self.__context_label.set_alignment(0, 0)
        contextbox.pack_start(self.__context_label, padding=4)

    def show_status(self, status):
        code, message = status
        if message is None:
            self.start()
            self.__status_bar.set_sensitive(True)
            self.__status_bar.pulse()
        else:
            self.stop()
            self.__status_bar.set_sensitive(False)
            #self.set_title(message)

    def set_details_expanded(self, expanded):
        self.__details_expander.set_expanded(expanded)

    def cb_result_selected(self, tree, result):
        lines = self.boss.option('grepper', 'context-lines')
        pre, match, post = [cgi.escape(s) for s in
                            result.value.get_context(lines)]
        self.__context_label.set_markup(RESULT_CONTEXT_MU % (pre, match, post))

    def cb_result_activated(self, tree, result):
        self.boss.command('editor', 'open-file-line',
                filename=result.value.filename,
                linenumber=result.value.linenumber)

    def get_options(self):
        options = GrepOptions()
        options.pattern = self.__pattern_entry.get_text()
        options.recursive = self.__recursive.get_active()
        options.directories = [self.__path_entry.get_filename()]
        options.ignorevcs = self.__ignore_vcs.get_active()
        options.maxresults = self.__maxresults
        return options

    def from_options(self, options):
        self.__pattern_entry.set_text(options.pattern)
        if len(options.directories):
            self.__path_entry.set_filename(options.directories[0])
        self.__recursive.set_active(options.recursive)
        self.__ignore_vcs.set_active(options.ignorevcs)
        self.__pattern_entry.grab_focus()
        self.__maxresults = options.maxresults

    def clear_results(self):
        self.__results_tree.clear()

    def add_result(self, result):
        self.__results_tree.add_item(ResultsTreeItem('', result))

    def start(self):
        self.__stop_but.set_sensitive(True)

    def stop(self):
        self.__stop_but.set_sensitive(False)

    def cb_stop_clicked(self, button):
        self.service.grep_stop()

    def cb_start_clicked(self, button):
        self.service.grep_start()
        
#class ContextOption(registry.Integer):
#    adjustment = 2, 9, 1

#class FindsTotalOption(registry.Integer):
#    adjustment = 100, 1000, 100

class Grepper(service.service):

    NAME = 'grepper'

    OPTIONS = [('start-detailed',
                'Whether the search dialog will start with the detailed view.'),
                #False, registry.Boolean),
               ('recursive',
                'Whether the search will recurse directories by default.'),
                #True, registry.Boolean),
               ('ignore-vcs',
                'whether the search will ignore .svn CNS and _darcs etc.'),
                #True, registry.Boolean),
               ('context-lines',
                'the number of lines of context that will be displayed.'),
                #3, ContextOption),
               ('start-directory',
                'the default search start directory'),
                #os.path.expanduser('~'), registry.Directory),
               ('maximum-matches',
                'the maximum number of matches for each search',)]
                #500, FindsTotalOption)]

    single_view_type = GrepView
    single_view_book = 'view'

    def grep_start(self):
        self.single_view.clear_results()
        self.single_view.start()
        self.__grep = PidaGrep(self.single_view.get_options())
        self.__grep.connect('found', self.cb_results_found)
        self.__grep.connect('status', self.cb_results_status)
        self.__grep.run()

    def grep_stop(self):
        self.__grep.stop()
        self.single_view.stop()

    def cb_results_found(self, grep, result):
        self.single_view.add_result(result)

    def cb_results_status(self, grep, status):
        self.single_view.show_status(status)
            

    def cmd_find_interactive(self, directories=None, ignorevcs=None,
                             recursive=None):
        self.create_single_view()
        options = GrepOptions()
        #if directories is None:
        #    options.directories = [self.options.get('start-directory').value()]
        #else:
        #    options.directories = directories
        #if ignorevcs is None:
        #    options.ignorevcs = self.options.get('ignore-vcs').value()
        #else:
        #    options.ignorevcs = ignorevcs
        #if recursive is None:
        #    options.recursive = self.options.get('recursive').value()
        #else:
        #    options.recursive = recursive
        options.maxresults = 100#self.options.get('maximum-matches').value()
        self.single_view.from_options(options)
        #self.editorview.set_details_expanded(
        #    self.options.get('start-detailed').value())

    def cmd_find(self, path, pattern):
        pass


    def cb_search_clicked(self, button):
        self.cmd_find_interactive()

    def cb_view_action(self, view, name):
        if name == 'apply':
            self.grep()
        if name == 'stop':
            self.__grep.stop()

    def act_find(self, action):
        self.call('find_interactive')

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_tools" action="base_tools_menu">
            <separator />
            <menuitem name="grepper" action="grepper+find" />
            </menu>
            </menubar>
            <toolbar>
            <toolitem  name="grepper" action="grepper+find" />
            </toolbar>
            """
    
    
BINARY_RE = re.compile(r'[\000-\010\013\014\016-\037\200-\377]')
class GrepOptions(object):
    files = []
    directories = []
    recursive = True
    pattern = ''
    ignorevcs = True
    ignoreglob = None

MATCH_MU = '<span color="#c00000">%s</span>'

class GrepResult(object):

    def __init__(self, linenumber, filename, line, matches):
        self.linenumber = linenumber
        self.filename = filename
        self.line = line = line.rstrip()
        muline = ''
        for match in matches:
            prematch, line = line.split(match, 1)
            muline = '%s%s' % (muline, cgi.escape(prematch))
            muline = '%s%s' % (muline, MATCH_MU % cgi.escape(match))
        self.muline = '%s%s' % (muline, cgi.escape(line))

    def get_context(self, lines=2):
        pre = []
        post = []
        for i in xrange(self.linenumber - lines, self.linenumber):
            readline = linecache.getline(self.filename, i).rstrip()
            pre.append('%s\t%s' % (i, readline))
        for i in xrange(self.linenumber + 1, self.linenumber + lines + 1):
            readline = linecache.getline(self.filename, i + 1).rstrip()
            post.append('%s\t%s' % (i, readline))
        pre = '\n'.join(pre)
        post = '\n'.join(post)
        return pre, '%s\t%s' % (self.linenumber, self.line), post

    def get_markup(self):
        return RESULT_MU % (self.linenumber,
                            cgi.escape(self.filename),
                            self.muline)
    markup = property(get_markup)

class PidaGrep(gobject.GObject):
    
    __gsignals__ = {'found' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'status' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,))}

    def __init__(self, options):
        gobject.GObject.__init__(self)
        self.__options = options
        self.__pattern = re.compile(options.pattern)
        self.__t = None
        self.__running = False

    def run(self):
        self.__t = threading.Thread(target = self.__run)
        self.__t.start()
        self.__running = True

    def get_files(self):
        for directory in self.__options.directories:
            for dirname, dirnames, filenames in os.walk(directory):
                if not self.__options.recursive:
                    dirnames[0:] = []
                else:
                    if self.__options.ignorevcs:
                        for d in dirnames:
                            if d in ['.svn', 'CVS', '_darcs']:
                                dirnames.remove(d)
                for filename in filenames:
                    filepath = os.path.join(dirname, filename)
                    yield filepath
        for filepath in self.__options.files:
                yield filepath

    def __run(self):
        try:
            self.__find()
        except StopIteration:
            return

    def __find(self):
        self.status(1, "searching")
        self.__nfound = 0
        for i, filename in enumerate(self.get_files()):
            if i % 16 == 0:
                self.status(self.__nfound)
            try:
                f = open(filename, 'r')
            except IOError:
                continue
            for linenumber, line in enumerate(f):
                if not self.__running:
                    self.__finished()
                if BINARY_RE.match(line):
                    break
                matches = self.__pattern.findall(line)
                if len(matches):
                    self.__nfound = self.__nfound + len(matches)
                    if self.__nfound >= self.__options.maxresults:
                        self.__finished()
                    result = GrepResult(linenumber, filename, line, matches)
                    gtk.threads_enter()
                    self.emit('found', result)
                    gtk.threads_leave()
            f.close()
        self.__finished()

    def status(self, code, message=None):
        gtk.threads_enter()
        self.emit('status', (code, message))
        gtk.threads_leave()

    def stop(self):
        self.__running = False

    def __finished(self):
        self.status(1, '%s found' % self.__nfound)
        raise StopIteration

gobject.type_register(PidaGrep)

Service = Grepper
