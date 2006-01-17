# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Bernard Pratz <guyzmo@m0g.net>

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

## TODO: Follow TODO markers in the code to see what needs to be done.
## TODO: Documentation will follow (soon :)

import time
import gtk

import pida.pidagtk.tree as tree
import pida.pidagtk.icons as icons
import pida.pidagtk.entry as entry
import pida.pidagtk.toolbar as toolbar
import pida.pidagtk.contentview as contentview
#import pida.pidagtk.HyperLink as hyperlink

# pida utils import
import pida.core.service as service

# using from imports to avoid to reexecute the logging package
from logging import Formatter
from logging import getLevelName

from cgi import escape

class log_item(tree.IconTreeItem):

    def __init__(self,record):
        self.__detailed = False
        ( img, self.color ) = self.__get_color_n_img(record)
        tree.IconTreeItem.__init__(self, record.created, record,image=img)

    def __get_color_n_img(self,record):
        if record.levelno == 0: # NOTSET
            return (icons.icons.get_image("about"), "#00FFFF")
        if record.levelno == 10: # DEBUG
            return (icons.icons.get_image("dialog-info"), "#3ba33b")
        if record.levelno == 20: # INFO
            return (icons.icons.get_image("info"), "#000000")
        if record.levelno == 30: # WARNING
            return (icons.icons.get_image("dialog-warning"), "#ffa33b")
        if record.levelno == 40: # ERROR
            return (icons.icons.get_image("no"), "#ff00fc")
        if record.levelno == 50: # CRITICAL
            return (icons.icons.get_image("stop"), "#FF0000")

    def set_detailed(self,det):
        self.__detailed = det
        if hasattr(self,'reset_markup'):
            self.reset_markup()
    
    def get_color(self,str):
        return '<span color="%s">%s</span>' % (self.color, str)

    def __get_markup(self):
        if self.__detailed == True:
            return escape('%s %s:%s\n%s\n%s %s' % ( self.name, 
                                    self.module, self.lineno, 
                                    self.message,
                                    self.levelname, self.created ))
        else:
            return self.get_color(escape('%s %s : %s' % ( self.name, 
                                    self.module, self.message )))
    markup = property(__get_markup)

    # properties
    def __get_name(self):
        return self.value.name
    name = property(__get_name)

    def __get_msg(self):
        return self.value.msg
    msg = property(__get_msg)

    def __get_args(self):
        return self.value.args
    args = property(__get_args)

    def __get_levelno(self):
        return self.value.levelno
    levelno = property(__get_levelno)

    def __get_levelname(self):
        return self.value.levelname
    levelname = property(__get_levelname)

    def __get_pathname(self):
        return self.value.pathname
    pathname = property(__get_pathname)

    def __get_filename(self):
        return self.value.filename
    filename = property(__get_filename)

    def __get_module(self):
        return self.value.module
    module = property(__get_module)

    def __get_exc_info(self):
        return self.value.exc_info
    exc_info = property(__get_exc_info)

    def __get_exc_text(self):
        return self.value.exc_text
    exc_text = property(__get_exc_text)

    def __get_lineno(self):
        return self.value.lineno
    lineno = property(__get_lineno)

    def __get_created(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", 
                                time.localtime(self.value.created))
    created = property(__get_created)

    def __get_message(self):
        return self.value.getMessage()
    message = property(__get_message)

class log_tree(tree.IconTree):
    '''Tree listing all the pastes'''
    EDIT_BUTTONS = False
    SORT_BY = 'created'

    def __init__(self):
        '''Initializes the tree'''
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', '%(markup)s')
        self.model.set_sort_column_id(0, gtk.SORT_ASCENDING)

    def push(self, record):
        '''Adds a paste to the Tree'''
        self.add_item(log_item(record))

    def pop(self):
        '''Deletes the currently selected paste'''
        self.del_item()

class log_watch(contentview.content_view):
    """View showing the last log entry"""
    LONG_TITLE = 'Log watch'
    SHORT_TITLE = 'log'
    ICON_TEXT = 'files'
    HAS_CONTROL_BOX = True
    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = True
    HAS_TITLE = True

    def init(self):
        self.__label = gtk.Label()
#        self.__label = hyperlink("")

    def markup(self,item):
        self.set_long_title("%s"%item.name)
        return "<b>%s</b> <i>%s</i>\n%s %s:%s\n<b>%s</b>\n" % (
            item.get_color(item.levelname), escape(item.created),
            item.name, item.module, item.lineno,
            escape(item.message))

    def show_log_item(self,record):
        self.widget.removeAll()
        self.__item = log_item(record)
        self.__label.set_text(self.markup(self.__item))
        self.__label.set_use_markup(True)
        self.__label.set_line_wrap(True)
#        self.__button = gtk.Button("TEST")
#        self.__button.connect('clicked', self.cb_clicked)
        self.widget.pack_start(self.__label,True)
#        self.widget.pack_start(self.__button,True)
        self.__label.show()

#        if hasattr(record,'callback'):
#            foo = record.callback()
#            foo.call()
#        else:
#            print 'has no attribute callback'

    def cb_clicked(self,but):
        pass
#        self.service.boss.call_command('editormanager', 'edit',
#            linenumber=self.__item.pathname)
#        self.service.boss.call_command('editormanager', 'goto_line',
#            linenumber=self.__item.lineno)

class log_history(contentview.content_view):
    ICON_NAME = 'logviewer'
    LONG_TITLE = 'Log viewer'
    SHORT_TITLE = 'log'
    ICON_TEXT = 'files'
    HAS_CONTROL_BOX = True
    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = True
    HAS_SEPARATOR = False
    HAS_TITLE = True

    def init(self,filter=None,logs=None):
        '''Constructor of the Paste History View.'''

        self.service.log.debug('new log manager with filter on %s' % filter)

        self.__filter = filter
        if filter not in (None , ''):
            self.set_long_title('Log filter : %s' % filter)

        self.__logs = logs

        self.__tree_selected = None
        self.__tree_detailled = None
        
        hb = gtk.HBox()
        hb.add(gtk.Label('Filter'))

        self.__filter_entry = entry.completed_entry()
        
        hb.add(self.__filter_entry)
        self.__filter_add = gtk.Button("")
        self.__filter_add.set_image(icons.icons.get_image("add"))
        self.__filter_add.connect('clicked', self.cb_filter_add)
        hb.add(self.__filter_add)
        self.widget.pack_start(hb,False,False)

        self.__log_tree = log_tree()
        self.widget.pack_start(self.__log_tree)
        self.__log_tree.connect('clicked', self.cb_record_clicked)
        self.__log_tree.connect('double-clicked', self.cb_record_db_clicked)
        self.__log_tree.connect('middle-clicked', self.cb_record_m_clicked)
        self.__log_tree.connect('right-clicked', self.cb_record_r_clicked)

    # Private interface
    def add_item(self,log):
        self.__log_tree.push(log)
        self.__filter_entry.add_words([log.levelname])

    # Public interface

    def refresh(self):
        self.__log_tree.clear()
        if self.__logs != None:                                           
            if self.__filter in  (None, ''):                              
                logs = self.__logs.iter                                   
            else:                                                         
                logs = self.__logs.filter_list('levelname',self.__filter) 
            for log in logs:                                              
                self.add_item(log)

    # Actions

    def cb_filter_add(self,but):
        self.service.cmd_filter(filter=self.__filter_entry.get_text())
        self.service.log.debug("Opened a new log filter view")
#        callback=foo
#        print 'testing callback'
#        self.service.log.critical("TEST INPUT",callback)

    def cb_record_clicked(self,record,tree_item):
        '''Callback function called when an item is selected in the TreeView'''
        if self.__tree_detailled != None:
            self.__tree_detailled.set_detailed(False)

        self.__tree_selected = tree_item.value
        self.__tree_selected.set_detailed(True)

        self.__tree_detailled = tree_item.value

    def cb_record_db_clicked(self,record,tree_item):
        '''Callback function called when an item is double clicked, and show it
        in the panel ? '''
        pass ## TODO: Show the record in the watcher

    def cb_record_m_clicked(self,record,tree_item):
        '''Callback function called when an item is middle clicked, and copy it
        to the mouse buffer clipboard ?'''
        pass ## TODO: copy the message in the buffer clipboard

    def cb_record_r_clicked(self, paste, tree_item, event):
        '''Callback function called when an item is right clicked, and show the
        contextual menu...'''
        pass ## TODO: show contextual menu

#class foo:
#    def call(self):
#        print 'clicked !'

class log_manager(service.service):
    NAME = 'log manager'
    LONG_TITLE = 'log manager'

    single_view_type = log_watch

    multi_view_type = log_history
    multi_view_book = 'view'

    # life cycle

    def start(self):
        self.__view = None
        self.__first = True
        if self.boss.use_notification_handler():
            self.log.debug("Logging service started.")
        else: 
            self.stop()

    def reset(self):
        self.log.debug("Logging service reset.")

    def stop(self):
        self.log.debug("Logging service stopped.")
        #Do more..

    #private interface
    #public interface
    # commands

    def cmd_filter(self,filter):
        view = self.create_multi_view(filter=filter,logs=self.boss.logs)
        self.cmd_refresh()

    def cmd_refresh(self):
        for view in self.multi_views:
            view.refresh()
        if self.single_view:
            self.single_view.show_log_item(self.boss.logs.last)

    def cmd_show_history(self):
        view = self.create_multi_view(logs=self.boss.logs)
        view.refresh()

    def cmd_show_watcher(self):
        self.create_single_view()
        self.single_view.show_log_item(self.boss.logs.last)

    # ui actions

    def act_show_log_history(self,action):
        self.call('show_history')

    def act_show_log_watcher(self,action):
        self.call('show_watcher')

    def get_menu_definition(self):
        return """
        <menubar>
        <menu name="base_tools" action="base_tools_menu">
        <separator />
        <menuitem name="logmanager+show_log_history" action="logmanager+show_log_history" />
        <menuitem name="logmanager+show_log_watcher" action="logmanager+show_log_watcher" />
        </menu>
        </menubar>        
        """

Service = log_manager

