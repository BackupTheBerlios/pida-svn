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
import pida.pidagtk.contentview as contentview
import pida.pidagtk.filedialogs as filedialogs
import pida.pidagtk.tree as tree

#import pida.utils.pygrep as pygrep

import os
import re
import time
import gobject
import threading
import linecache
import cgi
import string
import gtk

import pida.core.actions as actions

from pida.model import attrtypes as types
defs = service.definitions

table = range(0,128) * 2
hi_bit_chars = string.join(map(chr, range(0200,0400)),"")
hi_lo_table = string.join(map(chr, table), "")
all_chars = string.join(map(chr, range(0, 256)), "")

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
        return RESULT_MU % (self.value.linenumber + 1,
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
        self.__pattern_entry.connect('activate', self.cb_activated)
        self.__pattern_entry.connect('changed', self.cb_pattern_changed)
        l = gtk.Label()
        l.set_markup(SMALL_MU % 'in')
        hb.pack_start(l, expand=False)
        self.__path_entry = filedialogs.FolderButton()
        hb.pack_start(self.__path_entry)
        self.__recursive = gtk.CheckButton('-R')
        hb.pack_start(self.__recursive, expand=False)
        #self.__stop_but = gtk.Button(stock=gtk.STOCK_STOP)
        #hb.pack_start(self.__stop_but, expand=False)
        #self.__stop_but.set_sensitive(False)
        #self.__stop_but.connect('clicked', self.cb_stop_clicked)
        self.__start_but = gtk.Button(label='gtk-find')
        self.__start_but.set_use_stock(True)
        hb.pack_start(self.__start_but, expand=False)
        self.__start_but.connect('clicked', self.cb_start_clicked)
        self.__start_but.set_sensitive(False)
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
        self.__results_tree.connect('clicked', self.cb_result_activated)
        hb = gtk.HBox()
        self.widget.pack_start(hb, expand=False)
        self.__status_bar = gtk.ProgressBar()
        self.__status_bar.set_size_request(-1, 6)
        self.__status_bar.set_pulse_step(0.01)
        hb.pack_start(self.__status_bar, padding=4)
        self.__status_bar.set_no_show_all(True)


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
        #lines = self.boss.option('grepper', 'context-lines')
        lines = 4
        pre, match, post = [cgi.escape(s) for s in
                            result.value.get_context(lines)]
        self.__context_label.set_markup(RESULT_CONTEXT_MU % (pre, match, post))

    def cb_result_activated(self, tree, result):
        self.service.boss.call_command('buffermanager', 'open_file_line',
                filename=result.value.value.filename,
                linenumber=result.value.value.linenumber + 1)

    def cb_pattern_changed(self, entry):
        self.__start_but.set_sensitive(len(entry.get_text()) > 0)

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

        if options.directories is not None and len(options.directories):
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
        self.__status_bar.show()
        self.__start_but.set_label(gtk.STOCK_STOP)

    def stop(self):
        self.__status_bar.hide()
        self.__start_but.set_label(gtk.STOCK_FIND)

    def cb_start_clicked(self, button):
        if button.get_label() == gtk.STOCK_STOP:
            self.service.grep_stop()
        else:
            self.service.grep_start()

    def cb_activated(self, entry):
        self.service.grep_start()

class GrepConfig:
    __order__  = ['default_options', 'results']
    class default_options(defs.optiongroup):
        """Options that the search will start with by default."""
        __order__ = ['start_detailed', 'recursive_search',
                     'ignore_version_control_directories']
        label = 'Default Search Options'
        class start_detailed(defs.option):
            """Whether the detailed search options will start expanded."""
            label = 'Start with details visible'
            rtype = types.boolean
            default = False
        class recursive_search(defs.option):
            """Whether the search will be recursive by default."""
            rtype = types.boolean
            default = True
            label = 'Recursive search'
        class ignore_version_control_directories(defs.option):
            """Whether version control directories will be ignored by default."""
            rtype = types.boolean
            default = True
            label = 'Ignore version control directories'
    class results(defs.optiongroup):
        """Options relating to search results."""
        __order__ = ['maximum_results']
        label = 'Result Options'
        class maximum_results(defs.option):
            """The maximum number of search results."""
            label = 'Maximum number of results'
            rtype = types.intrange(5, 5000, 5)
            default = 500

    __markup__ = lambda self: 'Text Searcher'

class Grepper(service.service):

    config_definition = GrepConfig

    class GrepView(defs.View):
        view_type = GrepView
        book_name = 'view'

    display_name = 'Grep Search'

    def grep_start(self):
        opts = self.single_view.get_options()
        if not opts.pattern:
            return
        self.single_view.clear_results()
        self.single_view.start()
        self.__grep = PidaGrep(opts)
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
        view = self.create_view('GrepView')
        self.show_view(view=view)
        options = GrepOptions()
        if directories is None:
            proj = self.boss.call_command('projectmanager',
                                          'get_current_project')
            if proj is not None:
                options.directories = [proj.source_directory]
            else:
                options.directories = [os.getcwd()]
        else:
            options.directories = directories
        if ignorevcs is None:
            options.ignorevcs = self.opt(
                'default_options', 'ignore_version_control_directories')
        else:
            options.ignorevcs = ignorevcs
        if recursive is None:
            options.recursive = self.opt(
                'default_options', 'recursive_search')
        else:
            options.recursive = recursive
        options.maxresults = self.opt('results', 'maximum_results')
        self.single_view.from_options(options)
        self.single_view.set_details_expanded(self.opt(
           'default_options', 'start_detailed'))

    def cmd_find(self, path, pattern):
        pass

    def cb_search_clicked(self, button):
        self.cmd_find_interactive()

    def cb_view_action(self, view, name):
        if name == 'apply':
            self.grep()
        if name == 'stop':
            self.__grep.stop()

    @actions.action(stock_id='gtk-searchtool',
                    label='Find in directory',
                    default_accel='<Control>slash')
    def act_find(self, action):
        """Find text on a document or in a directory"""
        self.call('find_interactive')

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_edit" action="base_edit_menu">
                <placeholder name="SubEditSearchMenu">
                    <menuitem name="grepper" action="grepper+find" />
                </placeholder>
            </menu>
            </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
                </placeholder>
                <placeholder name="SaveFileToolbar">
                </placeholder>
                <placeholder name="EditToolbar">
                </placeholder>
                <placeholder name="ProjectToolbar">
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
                <placeholder name="ToolsToolbar">
            <separator />
            <toolitem  name="grepper" action="grepper+find" />
                </placeholder>
                </toolbar>
            """

    def get_single_view(self):
        return self.get_first_view('GrepView')
    single_view = property(get_single_view)
    
    
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
                line = string.translate(line, all_chars, hi_bit_chars)
                line = string.translate(line, hi_lo_table)
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
