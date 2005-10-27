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
import pida.pidagtk.contentbook as contentbook

from gazpacho import application
import gtk
class GazpachoApplication(application.Application):
    
    def __init__(self, app_window):
        self.__app_window = app_window
        application.Application.__init__(self)

    def _change_action_state(self, sensitive=[], unsensitive=[]):
        return

    def set_title(self, title):
        pass

    def get_container(self):
        return self.window

    def get_window(self):
        return self.__app_window

    def _application_window_create(self):
        #application_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #application_window.move(0, 0)
        #application_window.set_default_size(700, -1)

        application_window = gtk.VBox()
        iconfilename = application.environ.find_pixmap('gazpacho-icon.png')
        #gtk.window_set_default_icon_from_file(iconfilename)
                                                
        application_window.connect('delete-event', self._delete_event)

        # Create the different widgets
        menubar, toolbar = self._construct_menu_and_toolbar(gtk.Window())

        self._palette = application.Palette(self._catalogs)
        self._palette.connect('toggled', self._palette_button_clicked)

        self._editor = application.Editor(self)

        widget_view = self._widget_tree_view_create()

        self.gactions_view = self._gactions_view_create()
        
        self._statusbar = self._construct_statusbar()

        # Layout them on the window
        main_vbox = gtk.VBox()
        application_window.add(main_vbox)

        main_vbox.pack_start(menubar, False)
        main_vbox.pack_start(toolbar, False)

        hbox = gtk.HBox(spacing=6)
        hbox.pack_start(self._palette, False, False)

        vpaned = gtk.VPaned()
        hbox.pack_start(vpaned, True, True)

        notebook = gtk.Notebook()
        notebook.append_page(widget_view, gtk.Label(('Widgets')))
        notebook.append_page(self.gactions_view, gtk.Label(('Actions')))

        vpaned.set_position(150)

        vpaned.add1(notebook)
        vpaned.add2(self._editor)

        main_vbox.pack_start(hbox)
        
        main_vbox.pack_end(self._statusbar, False)

        # dnd doesn't seem to work with Konqueror, at least not when
        # gtk.DEST_DEFAULT_ALL or gtk.DEST_DEFAULT_MOTION is used. If
        # handling the drag-motion event it will work though, but it's
        # a bit tricky.
        application_window.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                         application.Application.targets,
                                         gtk.gdk.ACTION_COPY)
        
        #application_window.connect('drag_data_received',
        #                           self._dnd_data_received_cb)
        
        self.refresh_undo_and_redo()

        self.application_window = application_window
        return application_window

    def icb_signal_activated(self, tv, path, column):
        model = tv.get_model()
        niter = model.get_iter(path)
        callbackname = model.get_value(niter, 1)
        widgetname = self._editor._loaded_widget.name
        widgettype =  self._editor._loaded_widget.gtk_widget
        signalname =  model.get_value(niter, 0)
        if callbackname and callbackname.startswith('<'):
            callbackname = '%s_%s' % (widgetname, signalname.replace('-', '_'))
            model.set_value(niter, 1, callbackname)
        if callbackname:
            if not self._project.path:
                mb = gtk.MessageDialog(parent=self.get_window(),
                        flags = 0,
                        type = gtk.MESSAGE_INFO,
                        buttons = gtk.BUTTONS_OK,
                        message_format='You must save your user interface '
                                       'file before continuing.')
                def mbok(*args):
                    mb.destroy()
                mb.connect('response', mbok)
                mb.run()
                self._save_cb(None)
            if not self._project.path:
                return
            self.cb.evt('signaledited', self._project.path,
                            widgetname,
                            widgettype,
                            signalname,
                            callbackname)
        #print self._project.path

    def _fconstruct_menu_and_toolbar(self, application_window):
        actions =(
            ('Gazpacho', None, ('_Gaz')),
            ('FileMenu', None, ('_File')),
            ('New', gtk.STOCK_NEW, ('_New'), '<control>N',
             ('New Project'), self._new_cb),
            ('Open', gtk.STOCK_OPEN, ('_Open'), '<control>O',
             ('Open Project'), self._open_cb),
            ('Save', gtk.STOCK_SAVE, ('_Save'), '<control>S',
             ('Save Project'), self._save_cb),
            ('SaveAs', gtk.STOCK_SAVE_AS, ('_Save As...'),
             '<shift><control>S', ('Save project with different name'),
             self._save_as_cb),
            ('Close', gtk.STOCK_CLOSE, ('_Close'), '<control>W',
             ('Close Project'), self._close_cb),
            ('Quit', gtk.STOCK_QUIT, ('_Quit'), '<control>Q', ('Quit'),
             self._quit_cb),
            ('EditMenu', None, ('_Edit')),
            ('Cut', gtk.STOCK_CUT, ('C_ut'), '<control>X', ('Cut'),
             self._cut_cb),
            ('Copy', gtk.STOCK_COPY, ('_Copy'), '<control>C', ('Copy'),
             self._copy_cb),
            ('Paste', gtk.STOCK_PASTE, ('_Paste'), '<control>V', ('Paste'),
             self._paste_cb),
            ('Delete', gtk.STOCK_DELETE, ('_Delete'), '<control>D',
             ('Delete'), self._delete_cb),
            ('ActionMenu', None, ('_Actions')),
            ('AddAction', gtk.STOCK_ADD, ('_Add action'), '<control>A',
             ('Add an action'), self._add_action_cb),
            ('RemoveAction', gtk.STOCK_REMOVE, ('_Remove action'), None,
             ('Remove action'), self._remove_action_cb),
            ('EditAction', None, ('_Edit action'), None, ('Edit Action'),
             self._edit_action_cb),
            ('ProjectMenu', None, ('_Project')),
            ('DebugMenu', None, ('_Debug')),
            ('HelpMenu', None, ('_Help')),
            ('About', None, ('_About'), None, ('About'), self._about_cb)
            )

        toggle_actions = (
            ('ShowCommandStack', None, ('Show _command stack'), 'F3',
             ('Show the command stack'), self._show_command_stack_cb, False),
            ('ShowClipboard', None, ('Show _clipboard'), 'F4',
             ('Show the clipboard'), self._show_clipboard_cb, False),
            )
        
        undo_action = (
            ('Undo', gtk.STOCK_UNDO, ('_Undo'), '<control>Z',
             ('Undo last action'), self._undo_cb),
            )

        redo_action = (
            ('Redo', gtk.STOCK_REDO, ('_Redo'), '<control>R',
             ('Redo last action'), self._redo_cb),
            )
        
        ui_description = """<ui>
              <menubar name="MainMenu">
                <menu action="Gazpacho">
                <menu action="FileMenu">
                  <menuitem action="New"/>
                  <menuitem action="Open"/>
                  <separator name="FM1"/>
                  <menuitem action="Save"/>
                  <menuitem action="SaveAs"/>
                  <separator name="FM2"/>
                  <menuitem action="Close"/>
                  <menuitem action="Quit"/>
                </menu>
                <menu action="EditMenu">
                  <menuitem action="Undo"/>
                  <menuitem action="Redo"/>
                  <separator name="EM1"/>
                  <menuitem action="Cut"/>
                  <menuitem action="Copy"/>
                  <menuitem action="Paste"/>
                  <menuitem action="Delete"/>
                </menu>
                <menu action="ActionMenu">
                  <menuitem action="AddAction"/>
                  <menuitem action="RemoveAction"/>
                  <menuitem action="EditAction"/>
                </menu>
                <menu action="ProjectMenu">
                </menu>
                <menu action="DebugMenu">
                  <menuitem action="ShowCommandStack"/>
                  <menuitem action="ShowClipboard"/>
                </menu>
                <menu action="HelpMenu">
                  <menuitem action="About"/>
                </menu>
                </menu>
              </menubar>
              <toolbar name="MainToolbar">
                <toolitem action="Open"/>
                <toolitem action="Save"/>
                <toolitem action="Undo"/>
                <toolitem action="Redo"/>    
              </toolbar>
              <toolbar name="EditBar">
                <toolitem action="Cut"/>
                <toolitem action="Copy"/>
                <toolitem action="Paste"/>
                                <toolitem action="Delete"/>
                              </toolbar>
                            </ui>
                            """
        self._ui_manager = gtk.UIManager()

        action_group = gtk.ActionGroup('MenuActions')
        action_group.add_actions(actions)
        action_group.add_toggle_actions(toggle_actions)
        self._ui_manager.insert_action_group(action_group, 0)

        action_group = gtk.ActionGroup('UndoAction')
        action_group.add_actions(undo_action)
        self._ui_manager.insert_action_group(action_group, 0)
        
        action_group = gtk.ActionGroup('RedoAction')
        action_group.add_actions(redo_action)
        self._ui_manager.insert_action_group(action_group, 0)
        
        self._ui_manager.add_ui_from_string(ui_description)
        
        #application_window.add_accel_group(self._ui_manager.get_accel_group())

        self.project_action_group = gtk.ActionGroup('ProjectActions')
        self._ui_manager.insert_action_group(self.project_action_group, 0)

        menu = self._ui_manager.get_widget('/MainMenu')
    
        self.menu = menu

        return menu
    
    def irefresh_undo_and_redo(self):
        undo_info = redo_info = None        
        if self._project is not None:
            undo_info = self._project.undo_stack.get_undo_info()
            redo_info = self._project.undo_stack.get_redo_info()

        undo_action = self._ui_manager.get_action('/MainToolbar/Undo')
        undo_group = undo_action.get_property('action-group')
        undo_group.set_sensitive(undo_info is not None)
        undo_widget = self.undo_button
        undo_widget.set_sensitive(undo_info is not None)
            
        redo_action = self._ui_manager.get_action('/MainToolbar/Redo')
        redo_group = redo_action.get_property('action-group')
        redo_group.set_sensitive(redo_info is not None)
        redo_widget = self.redo_button
        redo_widget.set_sensitive(redo_info is not None)
        if self._command_stack_window is not None:
            command_stack_view = self._command_stack_window.get_child()
            command_stack_view.update()


class EmbeddedGazpacho(contentbook.ContentView):

    def __init__(self, main_window):
        self.__main_window = main_window
        contentbook.ContentView.__init__(self)

    def populate(self):
        self.__gazpacho = GazpachoApplication(self.__main_window)
        self.pack_start(self.__gazpacho.get_container())

    def open_file(self, filename):
        self.__gazpacho.open_project(filename)

class Gazpacho(service.Service):
    NAME = 'gazpacho'

    def populate(self):
        self.__view = None
        self.boss.command("buffermanager", "register-file-handler",
                          filetype="*.glade", handler=self)

    def open_file(self, filename):
        if self.__view is None:
            self.__view = EmbeddedGazpacho(self.boss.get_main_window())
            self.boss.command("editor", "add-page",
                              contentview=self.__view)
        self.__view.open_file(filename)
        buffer = GazpachoBuffer(filename)
        buffer.boss = self.boss
        self.boss.command("buffermanager", "add-buffer", buffer=buffer)
        self.__view.raise_tab()
            

import pida.core.buffer as buffer
import os

class GazpachoBuffer(buffer.Buffer):
    def get_markup(self):
        """Return the markup for the item."""
        MU = ('<span size="small">'
              '<span foreground="#c00000">%s/</span>'
              '<b>%s</b>'
              '</span>')
        fp = self.filename
        fd, fn = os.path.split(fp)
        dp, dn = os.path.split(fd)
        return MU % (dn, fn)
    markup = property(get_markup)

Service = Gazpacho
