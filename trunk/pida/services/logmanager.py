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

#TODO Documentation

# still not really stable
__disabled__

import string

import time
import gtk

import pida.pidagtk.tree as tree
import pida.pidagtk.icons as icons
import pida.pidagtk.entry as entry
import pida.pidagtk.contentview as contentview
#import pida.pidagtk.HyperLink as hyperlink

# pida utils import
import pida.core.base as base
import pida.core.service as service

# using from imports to avoid to reexecute the logging package
from cgi import escape

defs = service.definitions
types = service.types

color = {'notset':  {'color':'#00FFFF','icon':"about"},
         'debug':   {'color':'#3ba33b','icon':"dialog-info"},
         'info':    {'color':'#000000','icon':"info"},
         'warning': {'color':'#ffa33b','icon':"dialog-warning"},
         'error':   {'color':'#ff00fc','icon':"no"},
         'critical':{'color':'#ff0000','icon':"stop"}}

markup = {'short':"$module $name:$lineno",
          'full':"$module $name:$lineno\n$message\n$levelname $created"}

view_option = {'font':None,
               'new':False,
               'length':70,
               'default_filter':None}

record_attributes = ['name',
                     'threadName',
                     'process',
                     'module',
                     'filename',
                     'lineno',
                     'msg',
                     'levelname']

class log_item(tree.IconTreeItem):
    '''Transformation of informations from LogRecord to TreeItem.'''

    def __init__(self,record):
        '''Sets the treeitem up'''
        self.__detailed = False
        ( img, self.color ) = self.__get_color_n_img(record)
        tree.IconTreeItem.__init__(self, record.created, record,image=img)

        self.__mark_up_keys={'module':self.module,
                              'name':self.name,
                              'lineno':self.lineno,
                              'message':self.message,
                              'levelname':self.levelname,
                              'created':self.created,
                              'msg':self.msg,
                              'args':self.args,
                              'levelno':self.levelno,
                              'pathname':self.pathname,
                              'filename':self.filename,
                              'exc_info':self.exc_info,
                              'exc_text':self.exc_text}
                              
#        self.set_property('font-desc', view_option['font'])

    def __get_color_n_img(self,record):
        '''Get a tuple containing a color and an icon for 
        the record's loglevel'''
        if record.levelno == 0: # NOTSET
            return (icons.icons.get_image(color['notset']['icon']), 
                                            color['notset']['color'])
        if record.levelno == 10: # DEBUG
            return (icons.icons.get_image(color['debug']['icon']), 
                                            color['debug']['color'])
        if record.levelno == 20: # INFO
            return (icons.icons.get_image(color['info']['icon']), 
                                            color['info']['color'])
        if record.levelno == 30: # WARNING
            return (icons.icons.get_image(color['warning']['icon']), 
                                            color['warning']['color'])
        if record.levelno == 40: # ERROR
            return (icons.icons.get_image(color['error']['icon']), 
                                            color['error']['color'])
        if record.levelno == 50: # CRITICAL
            return (icons.icons.get_image(color['critical']['icon']), 
                                            color['critical']['color'])
        if record.levelno == 100: # USER_NOTIFY
            return (icons.icons.get_image("dialog-question"), "#330000")
        if record.levelno == 110: # USER_INPUT
            return (icons.icons.get_image("dialog-question"), "#880000")

    def set_detailed(self,det):
        '''Sets wether the markup is detailed or not'''
        self.__detailed = det
        if hasattr(self,'reset_markup'):
            self.reset_markup()
    
    def get_color(self,str):
        '''Returns the color markup'''
        if self.color:
            return '<span color="%s">%s</span>' % (self.color, str)
        else:
            return str

    def __get_markup(self):
        '''Returns the full log item's markup
        Interprets the keys and display their values
        '''
        try:
            try:
                if self.__detailed == True:
                    mark_up = string.Template(markup['full'])
                    return escape(mark_up.substitute(self.__mark_up_keys))
                mark_up = string.Template(markup['short'])
                return  self.get_color(escape(mark_up.substitute(
                                                        self.__mark_up_keys)))
            except KeyError, ke:
                print "ERROR: Key %s not available for marking up." % ke
                raise ke
        except:
            print "Turned back log item's markup to default"
            if self.__detailed == True:
                    return escape('%s.%s:%s\n%s\n%s %s' % ( self.value.module, 
                                            self.value.name, self.value.lineno, 
                                            self.value.message,
                                            self.value.levelname, 
                                            self.value.created ))
            return self.get_color(escape('%s.%s : %s' % ( self.value.module, 
                            self.value.name, self.value.getMessage() )))
    markup = property(__get_markup)

    # properties
    def __get_created(self):
        '''Return the localized creation date'''
        return time.strftime("%Y-%m-%d %H:%M:%S", 
                                time.localtime(self.value.created))
    created = property(__get_created)

    def __get_message(self):
        '''Return the message (cropped at user's preference length)'''
        msg = self.value.getMessage()
        if len(msg) > view_option['length']:
            return msg[:view_option['length']-3]+"..."
        return msg
    message = property(__get_message)

    # properties
    def __get_name(self):
        '''Return the logrecord's name'''
        return self.value.name
    name = property(__get_name)

    def __get_msg(self):
        '''Return the logrecord's msg (with keys)'''
        return self.value.msg
    msg = property(__get_msg)

    def __get_args(self):
        '''Return the logrecord's msg keys'''
        return self.value.args
    args = property(__get_args)

    def __get_levelno(self):
        '''Return the logrecord's level #'''
        return self.value.levelno
    levelno = property(__get_levelno)

    def __get_levelname(self):
        '''Return the logrecord's level name'''
        return self.value.levelname
    levelname = property(__get_levelname)

    def __get_pathname(self):
        '''Return the logrecord's origin pathname'''
        return self.value.pathname
    pathname = property(__get_pathname)

    def __get_filename(self):
        '''Return the logrecord's origin filename'''
        return self.value.filename
    filename = property(__get_filename)

    def __get_module(self):
        '''Return the logrecord's origin module name'''
        return self.value.module
    module = property(__get_module)

    def __get_exc_info(self):
        '''Return the logrecord's exception information (if available)'''
        return self.value.exc_info
    exc_info = property(__get_exc_info)

    def __get_exc_text(self):
        '''Return the logrecord's exception text (if available)'''
        return self.value.exc_text
    exc_text = property(__get_exc_text)

    def __get_lineno(self):
        '''Return the logrecord's origin line #'''
        return self.value.lineno
    lineno = property(__get_lineno)

class log_tree(tree.IconTree):
    '''Tree listing all the pastes'''
    EDIT_BUTTONS = False
    SORT_BY = 'created'

    def __init__(self):
        '''Initializes the tree'''
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', '%(markup)s')
        self.model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.view.set_model(self.model)

    def add_item(self, item, parent=None):
        '''overriden add in the tree method'''
        titem = log_item(item)
        pixbuf = titem.pixbuf
        key = titem.created
        row = [key, titem, self.get_markup(titem), pixbuf]
        niter = self.model.append(parent, row)
        def reset():
            self.model.set_value(niter, 2, self.get_markup(titem))
        titem.reset_markup = reset
        item.reset_markup = reset
        return niter

    def push(self, record):
        '''Adds a record to the Tree'''
        self.add_item(record)

    def pop(self):
        '''Deletes the currently selected paste'''
        self.del_item()

class markup_validate_string(types.string):
    '''Entry string with validation'''
    def validate(self,value):
        try:
            mup = string.Template(value)
            return escape(mup.substitute(log_item.__dict__))
        except KeyError, ke:
            self.log.error("Key %s not available for marking up." % ke)
            return False

class log_history(contentview.content_view):
    '''Log History view
    Where all the logs are displayed
    '''

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

        self.set_filter(filter)

        self.__logs = logs

        self.__tree_selected = None
        self.__tree_detailled = None
        
        hb = gtk.HBox()
        hb.pack_start(gtk.Label('Filter'),False,False)

        self.__filter_entry = entry.completed_keyword_entry(record_attributes)
       
        hb.add(self.__filter_entry)
        filter_add = gtk.Button("")
        filter_add.set_image(icons.icons.get_image("add"))
        filter_add.connect('clicked', self.cb_filter_add)
        hb.pack_start(filter_add,False,False)

        refresh = gtk.Button("")
        refresh.set_image(icons.icons.get_image("refresh"))
        refresh.connect('clicked', self.cb_refresh)
        hb.pack_start(refresh,False,False)

        self.widget.pack_start(hb,False,False)

        self.__log_tree = log_tree()
        self.widget.pack_start(self.__log_tree)
        self.__log_tree.connect('clicked', self.cb_record_clicked)
        self.__log_tree.connect('double-clicked', self.cb_record_db_clicked)
        self.__log_tree.connect('middle-clicked', self.cb_record_m_clicked)
        self.__log_tree.connect('right-clicked', self.cb_record_r_clicked)

    # Private interface
    def add_item(self,log):
        '''Adds an item to the tree'''
        self.__log_tree.push(log)
        for attr in record_attributes:
            self.__filter_entry.add_word(attr,getattr(log,attr))

    # Public interface

    def set_filter(self,filter):
        '''Sets a filter'''
        filter = view_option['default_filter']
        request = {}
        if " " in filter:
            pairs = filter.split(" ")
            for pair in pairs:
                if len(pair.split(":")) == 2:
                    (key,val) = pair.split(":")
                    if key not in request.keys():
                        request[key] = []
                    request[key].append(val)
        elif len(filter.split(":")) == 2:
            (key,val) = filter.split(":")
            if key not in request.keys():
                request[key] = []
            request[key].append(val)

        self.__filter = request
        if request != {}:
            self.set_long_title('Log filter : %s' % filter)
        else:
            self.__filter = None
            self.set_long_title('Log Viewer (with default filter)')

    def refresh(self,thread_lock=False):
        '''Refresh the treeview with the logs
        TODO: improve updates (only load changes, not the whole tree...)'''
        if thread_lock:
            gtk.threads_enter()
        self.__log_tree.clear()
        if self.__logs != None:                                           
            if self.__filter in  (None, ''):                              
                logs = self.__logs.iter
                for log in logs:
                    self.add_item(log)
            else:
                logs = {}
                for attr in self.__filter.keys():
                    if attr not in logs.keys():
                        logs[attr] = []
                    for log in self.__logs.filter_list(\
                                                     attr,self.__filter[attr]):
                        logs[attr].append(log)
                for attr in logs.keys():
                    for log in logs[attr]:
                        self.add_item(log)
        if thread_lock:
            gtk.threads_leave()

    # Actions

    def cb_filter_add(self,but):
        '''Creates a new log history with string filter parameter'''
        self.service.cmd_filter(filter=self.__filter_entry.get_text())
        if view_option['new']:
            self.service.log.debug("Opened a new log filter view")
        else:
            self.service.log.debug("Set a filter on the log view")

    def cb_refresh(self,but):
        '''Callback function to refresh the treeview'''
        self.refresh()

    def cb_record_clicked(self,record,tree_item):
        '''Callback function called when an item is selected in the TreeView'''
        if self.__tree_detailled != None:
            self.__tree_detailled.set_detailed(False)

        self.__tree_selected = tree_item
        self.__tree_selected.set_detailed(True)

        self.__tree_detailled = tree_item

    def cb_record_db_clicked(self,record,tree_item):
        '''Callback function called when an item is double clicked, and show it
        in the panel ? '''
        pass

    def cb_record_m_clicked(self,tree,tree_item):
        '''Callback function called when an item is middle clicked, and copy it
        to the mouse buffer clipboard ?'''
        pass

    def cb_record_r_clicked(self, paste, tree_item, event):
        '''Callback function called when an item is right clicked, and show the
        contextual menu...'''
        pass

view_location_map = {'View Pane':'view',
                     'Quick Pane':'content',
                     'Detached':'ext'}
class log_manager(service.service):
    NAME = 'log manager'
    LONG_TITLE = 'log manager'

    multi_view_type = log_history

    #Get configuration values

    def get_multi_view_book_type(self):
        '''Get view book destination of the log history from configuration'''
        opt = self.opt('general', 'history_view_location')
        return view_location_map[opt]
    multi_view_book = property(get_multi_view_book_type)

    def get_colors(self):
        '''Get level colors from configuration'''
        for levelname in color.keys():
            opt = self.opt('fonts_and_colours', '%s_color' % levelname)
            if opt:
                color[levelname]['color'] = opt

    def get_icons(self):
        '''Get level icons from configuration'''
        for levelname in color.keys():
            opt = self.opt('fonts_and_colours', '%s_icon' % levelname)
            if opt:
                color[levelname]['icon'] = opt

    def get_markups(self):
        '''Get logline's markup length from configuration'''
        for markup_length in markup.keys():
            opt = self.opt('advanced','markup_%s' % markup_length)
            if opt:
                markup[markup_length] = opt

    def get_msg_length(self):
        '''Get message's max length'''
        opt = self.opt('advanced','message_length')
        if opt:
            view_option['length'] = int(opt)

    def get_item_font(self):
        '''Get item's font'''
        opt = self.opt('fonts_and_colours','font')
        if opt != None:
            view_option['font'] = pango.FontDescription(opt)

    def get_new_views(self):
        '''Get wether the user wants to open new filters in new windows
        or not.'''
        opt = self.opt('general','open_new_views')
        if opt:
            view_option['new'] = opt

    def get_default_filter(self):
        '''Gets the default filter to apply'''
        opt = self.opt('general','default_filter')
        if opt:
            view_option['default_filter'] = opt

    # life cycle

    def start(self):
        self.__view = None
        self.__first = True
        self.__threads = False
        refresh_level = self.opt('general', 'history_level_refresh')
        if refresh_level in (None, ''):
            refresh_level = 'DEBUG'
        if self.boss.use_notification_handler(refresh_level,self.cmd_refresh):
            self.log.debug("Logging service started. Refreshing at"+\
                                " level"+refresh_level)
            self.get_options()
#            self.get_icons()
            self.get_markups()
            self.get_msg_length()
            self.get_multi_view_book_type()
            self.get_default_filter()
            self.get_new_views()
        else: 
            self.log.warning("Logging notification service couldn't be started.")
            self.stop()

    def reset(self):
        self.log.debug("Logging service reset.")
        self.get_colors()
#        self.get_icons()
        self.get_markups()
        self.get_msg_length()
        self.get_multi_view_book_type()
        self.get_new_views()
        self.get_default_filter()
        self.cmd_refresh()

    def stop(self):
        self.log.debug("Logging service stopped.")
        self.boss.stop_logging()

    #private interface

    #public interface

    def threads_enter(self):
        self.__threads = True

    def threads_leave(self):
        self.__threads = False

    class general(defs.optiongroup):
        '''Logging options'''
        class history_level_refresh(defs.option):
            '''Minimum level (included) shall the history be refreshed'''
            rtype = types.stringlist('DEBUG','INFO','WARNING','CRITICAL')
            default = 'INFO'

        class history_view_location(defs.option):
            '''Where newly started histories will appear per default'''
            rtype = types.stringlist(*view_location_map.keys())
            default = 'View Pane'

        class default_filter(defs.option):
            '''Default filter to apply on the logs'''
            rtype = types.string
            default = 'levelname:INFO levelname:WARNING levelname:ERROR '+\
                      'levelname:CRITICAL'

    class advanced(defs.optiongroup):
        '''Advanced logging options'''
        class markup_short(defs.option):
            '''The default markup to display. To customize it is available: 
$module, $name, $lineno, $message, $levelname, $created, $msg, $args
$levelno, $pathname, $filename, $exc_info and/or $exc_text'''
            default = markup['short']
            rtype = markup_validate_string

        class markup_full(defs.option):
            '''The default markup to display, when selected. To customize 
it is available: 
$module, $name, $lineno, $message, $levelname, $created, $msg, $args
$levelno, $pathname, $filename, $exc_info and/or $exc_text'''
            default = escape(markup['full'])
            rtype = markup_validate_string 

        class message_length(defs.option):
            '''How much shall the size of the main message be shortened'''
            default = view_option['length']
            rtype = types.integer

        class open_new_views(defs.option):
            '''If set to true, open new history filters in new views'''
            rtype = types.boolean
            default = False
        
    class fonts_and_colours(defs.optiongroup):
        '''Fonts and colors for the markup'''
        class notset_color(defs.option):
            '''Change the color of unset log lines'''
            default = color['notset']['color']
            rtype = types.color

        class debug_color(defs.option):
            '''Change the color of the DEBUG log lines'''
            default = color['debug']['color']
            rtype = types.color

        class info_color(defs.option):
            '''Change the color of the INFO log lines'''
            default = color['info']['color']
            rtype = types.color

        class warning_color(defs.option):
            '''Change the color of the WARNING log lines'''
            default = color['warning']['color']
            rtype = types.color

        class critical_color(defs.option):
            '''Change the color of the CRITICAL log lines'''
            default = color['critical']['color']
            rtype = types.color

        class font(defs.option):
            '''TODO: Change the font of log history'''
            default = 'None'
            rtype = types.font
            
    # commands

    def cmd_filter(self,filter):
        if view_option['new']:
            view = self.create_multi_view(filter=filter,logs=self.boss.logs)
        else:
            for view in self.multi_views:
                view.set_filter(filter)
        self.cmd_refresh()

    def cmd_refresh(self):
        for view in self.multi_views:
            view.refresh(self.__threads)

    def cmd_show_history(self):
        view = self.create_multi_view(logs=self.boss.logs)
        view.refresh()

    # ui actions

    def act_show_log_history(self,action):
        self.call('show_history')

    def get_menu_definition(self):
        return '''
        <menubar>
        <menu name="base_tools" action="base_tools_menu">
        <separator />
        <menuitem name="logmanager+show_log_history" action="logmanager+show_log_history" />
        </menu>
        </menubar>        
        '''

Service = log_manager

