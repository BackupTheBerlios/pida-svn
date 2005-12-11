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
import pida.pidagtk.contentview as contentview
import pida.pidagtk.expander as expander

from gazpacho import application
from gazpacho import editor
from gazpacho.properties import PropertyCustomEditor, UNICHAR_PROPERTIES, prop_registry 
from gazpacho import signaleditor

import gtk
import gobject
import pida.core.document as document

class gazpacho_holder(contentview.content_view):

    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_LABEL = False


class GazpachoApplication(application.Application):
    
    def __init__(self, app_window):
        self.__app_window = app_window
        application.Application.__init__(self)

    def _change_action_state(self, sensitive=[], unsensitive=[]):
        return

    def set_title(self, title):
        pass

    def get_container(self):
        return self._window

    def get_window(self):
        return self.__app_window

    window = property(get_window)

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

        self._editor = Editor(self)
        editor_view = gtk.VBox()
        editor_view.pack_start(self._editor)
        self._editor.make_pages()

        widget_view = self._widget_tree_view_create()

        self.gactions_view = self._gactions_view_create()
        
        self._statusbar = self._construct_statusbar()

        # Layout them on the window
        main_vbox = gtk.VBox()
        application_window.add(main_vbox)

        #main_vbox.pack_start(menubar, False)
        #main_vbox.pack_start(toolbar, False)
        self.menubar = menubar

        hbox = gtk.HBox(spacing=6)
        vpaned = gtk.VBox()
        hbox.pack_start(vpaned, True, True)
        hbox.pack_start(self._palette, False, False)

        #vpaned = gtk.VPaned()

        #notebook = gtk.Notebook()
        #notebook.append_page(widget_view, gtk.Label(('Widgets')))
        #notebook.append_page(self.gactions_view, gtk.Label(('Actions')))

        notebook = gtk.Notebook()


        notebook.append_page(widget_view)
        notebook.append_page(self.gactions_view)
        notebook.set_page(0)
        #, gtk.Label(('Widgets')))

        #vpaned.set_position(150)

        vpaned.pack_start(notebook, expand=True, padding=2)
        vpaned.pack_start(editor_view, expand=True, padding=2)

        main_vbox.pack_start(hbox)
        
        #main_vbox.pack_end(self._statusbar, False)

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

    def cb_signal_activated(self, tv, path, column):
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

class EmbeddedGazpacho(contentview.content_view):


    def init(self):
        self.__main_window = self.service.boss.get_main_window()
        self.__gazpacho = GazpachoApplication(self.__main_window)
        self.widget.pack_start(self.__gazpacho.get_container())
        #self.add_button('open', 'open', 'save the file')
        #self.add_button('save', 'save', 'save the file')
        #self.add_button('saveas', 'saveas', 'save the file as')
        #self.add_button('cut', 'cut', 'cut to the clipboard')
        #self.add_button('copy', 'copy', 'copy to the clipboard')
        #self.add_button('paste', 'paste', 'paste from the clipboard')
        #for item in self.__gazpacho.menubar.get_children():
        #    l = item.get_children()[0]
        #    text = l.get_text()
        #    if text == 'File':
        #        text = 'Gazpacho'
        #    l.set_markup('<span size="small">%s</span>' % text.lower())
        #self.menu_area.pack_start(self.__gazpacho.menubar, expand=False)

    def open_file(self, filename):
        self.__gazpacho.open_project(filename)

    def get_gazpacho(self):
        return self.__gazpacho
    gaz = property(get_gazpacho)

class Gazpacho(service.service):


    single_view_type = EmbeddedGazpacho
    single_view_book = 'edit'

    class glade_handler(document.document_handler):
        """The glade file handler."""

        globs = ["*.glade"]

        def create_document(self, filename):
            doc = gazpacho_document(filename=filename, handler=self)
            return doc

        def view_document(self, document):
            self.service.call('start')
            self.service.single_view.open_file(document.filename)
            self.service.current_document = document

        def act_copy(self, action):
            pass

        def act_edit(self, action):
            pass

        def get_menu_definition(self):
            return """
                <menubar>
                <menu name="base_edit" action="gazpachdocument+edit">
                <menuitem name="gazcopy" action="gazpach+document+copy" />
                </menu>
                <menu name="base_project" action="base_project_menu">
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                <toolbar>   
                <toolitem name="tgazcopy" action="gazpach+document+copy" />
                </toolbar>
                """

    def cmd_open(self, filename):
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)

    def cmd_start(self):
        self.create_single_view()
        self.single_view.raise_page()

    def act_user_interface_designer(self, action):
        """Start the user interface designer Gazpacho."""
        self.call('start')
        
    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_tools" action="base_tools_menu">
            <separator />
            <menuitem name="gazpacho" action="gazpach+user_interface_designer" />
            </menu>
            </menubar>
            """

    def cb_single_view_closed(self, view):
        self.boss.call_command('buffermanager', 'file_closed',
                        filename=self.current_document.filename)
        
    def get_current_document(self):
        return self.__current_document

    def set_current_document(self, value):
        self.__current_document = value
    
    current_document = property(get_current_document, set_current_document)
            

import pida.core.document as document
import os

class gazpacho_document(document.dummyfile_document):

    ICON_NAME = 'gazpacho'

    def get_markup(self):
        """Return the markup for the item."""
        MU = ('<span><tt><b>ui </b></tt>'
              '<span foreground="#c00000">%s/</span>'
              '<b>%s</b>'
              '</span>')
        fp = self.filename
        fd, fn = os.path.split(fp)
        dp, dn = os.path.split(fd)
        return MU % (dn, fn)
    markup = property(get_markup)

class Editor(gtk.Notebook):

    __gsignals__ = {
        'add_signal':(gobject.SIGNAL_RUN_LAST, None,
                      (str, long, int, str))
        }
    
    def __init__(self, app):
        gtk.Notebook.__init__(self)
        self._app = app

    def make_pages(self):

        # The editor has (at this moment) four tabs this are pointers to the
        # vboxes inside each tab.
        self._vbox_widget, v1 = self._notebook_page(_('Widget'))
        self._vbox_packing, v2 = self._notebook_page(_('Packing'))
        self._vbox_common, v3 = self._notebook_page(_('Common'))
        self._vbox_signals, v4 = self._notebook_page(_('Signals'))
        self.set_page(0)

        # A handy reference to the widget that is loaded in the editor. None
        # if no widgets are selected
        self._loaded_widget = None

        # A list of properties for the current widget
        # XXX: We might want to cache this
        self._widget_properties = []
        
        self._signal_editor = None

        self._tooltips = gtk.Tooltips()

        # Display some help
        help_label = gtk.Label(_("Select a widget to edit its properties"))
        help_label.show()
        self._vbox_widget.pack_start(help_label)
        
    def _notebook_page(self, name):
        vbox = gtk.VBox()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add_with_viewport(vbox)
        scrolled_window.set_shadow_type(gtk.SHADOW_NONE)
        self.append_page(scrolled_window)
        return vbox, scrolled_window
        
    def do_add_signal(self, id_widget, type_widget, id_signal, callback_name):
        pass

    def _create_property_pages(self, widget, adaptor):
        # Create the pages, one for widget properties and
        # one for the common ones
        widget_table = editor.EditorPage()
        widget_table.append_name_field(adaptor)
        self._vbox_widget.pack_start(widget_table, False)
        
        common_table = editor.EditorPage()
        self._vbox_common.pack_start(common_table, False)

        packing_table = editor.EditorPage()
        self._vbox_packing.pack_start(packing_table, False)
        
        # Put the property widgets on the right page
        widget_properties = []
        parent = widget.gtk_widget.get_parent()
        for property_class in prop_registry.list(adaptor.type_name,
                                                 parent):

            if not property_class.editable:
                continue
            
            if property_class.child:
                page = packing_table
            elif property_class.owner_type in (gtk.Object.__gtype__,
                                               gtk.Widget.__gtype__):
                page = common_table
            else:
                page = widget_table

            property_widget = page.append_item(property_class,
                                               self._tooltips,
                                               self._app)
            if property_widget:
                widget_properties.append(property_widget)
                
        self._widget_properties = widget_properties

        # XXX: Remove this, show all widgets individually instead
        widget_table.show_all()
        common_table.show_all()
        packing_table.show_all()
        
    def _create_signal_page(self):
        if self._signal_editor:
            return self._signal_editor
        
        self._signal_editor = signaleditor.SignalEditor(self, self._app)
        self._vbox_signals.pack_start(self._signal_editor)

    def _get_parent_types(self, widget):
        retval = [type(widget)]
        while True:
            parent = widget.get_parent()
            if not parent:
                return retval
            retval.append(type(parent))
            widget = parent
    
    def _needs_rebuild(self, widget):
        """
        Return True if we need to rebuild the current property pages, False
        if it's not require.
        """
        
        if not self._loaded_widget:
            return True

        # Check if we need to rebuild the interface, otherwise we might end
        # up with a (child) properties which does not belong to us
        # FIXME: This implementation is not optimal, in some cases it'll
        # rebuild even when it doesn't need to, a better way would be
        # to compare child properties.
        if (self._get_parent_types(self._loaded_widget.gtk_widget) !=
            self._get_parent_types(widget.gtk_widget)):
            return True

        return False
        
    def _load_widget(self, widget):
        if self._needs_rebuild(widget):
            self.clear()
            self._create_property_pages(widget, widget.adaptor)
            self._create_signal_page()

        for widget_property in self._widget_properties:
            widget_property.load(widget)
        self._signal_editor.load_widget(widget)

        self._loaded_widget = widget

    def clear(self):
        "Clear the content of the editor"
        for vbox in (self._vbox_widget,
                     self._vbox_common,
                     self._vbox_packing):
            map(vbox.remove, vbox.get_children())
        self._loaded_widget = None
 
    def display(self, widget):
        "Display a widget in the editor"
        
        # Skip widget if it's already loaded or None
        if self._loaded_widget == widget or not widget:
            return

        self._load_widget(widget)

    def refresh(self):
        "Reread properties and update the editor"
        if self._loaded_widget:
            self._load_widget(self._loaded_widget)


Service = Gazpacho
