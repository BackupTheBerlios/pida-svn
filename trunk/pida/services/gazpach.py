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

# system import(s)
import os

# gtk import(s)
import gtk

from gazpacho import main
main.setup_app()
import gazpacho.app.app as app
Application = app.Application
# gazpacho imports
from gazpacho.clipboard import clipboard
from gazpacho.palette import palette
from gazpacho.app.bars import bar_manager
from gazpacho import signaleditor
from gazpacho.editor import Editor
from gazpacho.workspace import WorkSpace
from gazpacho.actioneditor import GActionsView
from gazpacho.widgetview import WidgetTreeView
from gazpacho.sizegroupeditor import SizeGroupView
from gazpacho.properties import PropertyCustomEditor
from gazpacho.uimstate import WidgetUIMState, ActionUIMState, SizeGroupUIMState

# pida core import(s)
import pida.core.service as service
import pida.core.document as document

# pidagtk import(s)
import pida.pidagtk.contentview as contentview

from gazpacho.constants import STOCK_SIZEGROUP

class gazpacho_application(Application):
    
    def __init__(self, app_window, view):
        self.__app_window = app_window
        self.__view = view
        self.__disconnect_clipboard()
        Application.__init__(self)

    def __disconnect_clipboard(self):
        i = 0 
        while True:
            if clipboard.handler_is_connected(i):
                clipboard.disconnect(i)
                break
            i = i + 1

    def set_title(self, title):
        pass

    def get_container(self):
        return self._window

    def get_window(self):
        return self.__view.service.boss.get_main_window()
    window = property(get_window)
  
    def _application_window_create(self):
        application_window = gtk.VBox()
        # layout them on the window
        main_vbox = gtk.VBox()
        application_window.add(main_vbox)
        # Create actions that are always enabled
        main_vbox.show()

        # Create actions that are always enabled
        bar_manager.add_actions(
            'Normal',
            # File menu
            ('FileMenu', None, _('_File')),
            ('New', gtk.STOCK_NEW, None, None,
             _('New Project'), self._new_cb),
            ('Open', gtk.STOCK_OPEN, None, None,
             _('Open Project'), self._open_cb),
            ('Quit', gtk.STOCK_QUIT, None, None,
             _('Quit'), self._quit_cb),

            # Edit menu
            ('EditMenu', None, _('_Edit')),

            # Object menu
            ('ObjectMenu', None, _('_Objects')),

            # Project menu
            ('ProjectMenu', None, _('_Project')),
            # (projects..)

            # Debug menu
            ('DebugMenu', None, _('_Debug')),
            ('DumpData', None, _('Dump data'), '<control>M',
              _('Dump debug data'), self._dump_data_cb),
            ('Reload', None, _('Reload'), None,
             _('Reload python code'), self._reload_cb),
            ('Preview', None, _('Preview'), None,
             _('Preview current window'), self._preview_cb),

            # Help menu
            ('HelpMenu', None, _('_Help')),
            ('About', gtk.STOCK_ABOUT, None, None, _('About Gazpacho'),
             self._about_cb),
            )

        # Toggle actions
        bar_manager.add_toggle_actions(
            'Normal',
            ('ShowStructure', None, _('Show _structure'), '<control><shift>t',
             _('Show container structure'), self._show_structure_cb, False),
            ('ShowCommandStack', None, _('Show _command stack'), 'F3',
             _('Show the command stack'), self._show_command_stack_cb, False),
            ('ShowClipboard', None, _('Show _clipboard'), 'F4',
             _('Show the clipboard'), self._show_clipboard_cb, False),
            ('ShowWorkspace', None, _('Show _workspace'), '<control><shift>t',
             _('Show container workspace'), self._show_workspace_cb, False),
            )

        # Create actions that reqiuire a project to be enabled
        bar_manager.add_actions(
            'ContextActions',
            # File menu
            ('Save', gtk.STOCK_SAVE, None, None,
             _('Save Project'), self._save_cb),
            ('SaveAs', gtk.STOCK_SAVE_AS, _('Save _As...'), '<shift><control>S',
             _('Save project with different name'), self._save_as_cb),
            ('Close', gtk.STOCK_CLOSE, None, None,
             _('Close Project'), self._close_cb),
            # Edit menu
            ('Undo', gtk.STOCK_UNDO, None, '<control>Z',
             _('Undo last action'), self._undo_cb),
            ('Redo', gtk.STOCK_REDO, None, '<shift><control>Z',
             _('Redo last action'), self._redo_cb)
            )

        bar_manager.add_actions(
            'AlwaysDisabled',
            # Edit menu
            ('Cut', gtk.STOCK_CUT, None, None,
             _('Cut'), None),
            ('Copy', gtk.STOCK_COPY, None, None,
             _('Copy'), None),
            ('Paste', gtk.STOCK_PASTE, None, None,
             _('Paste'), None),
            ('Delete', gtk.STOCK_DELETE, None, '<control>D',
             _('Delete'), None)
            )

        bar_manager.build_interfaces()
        self._update_recent_project_items()
        #application_window.add_accel_group(bar_manager.get_accel_group())
        #main_vbox.pack_start(bar_manager.get_menubar(), False)
        #main_vbox.pack_start(bar_manager.get_toolbar(), False)

        hbox = gtk.HBox(spacing=6)
        main_vbox.pack_start(hbox)
        hbox.show()

        palette.connect('toggled', self._on_palette_toggled)
        pal_parent = palette.get_parent()
        if pal_parent is not None:
            pal_parent.remove(palette)
        hbox.pack_end(palette, False, False)
        palette.show_all()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(400, -1)
        hbox.pack_start(sw, True, True)

        self._workspace = WorkSpace()
        sw.add_with_viewport(self._workspace)
        self._workspace.show()
        sw.set_no_show_all(True)
        self._workspace_sw = sw
        self._workspace_action = bar_manager.get_action(
            'ui/MainMenu/EditMenu/ShowWorkspace')
        self._workspace_action.set_active(False)

        vpaned = gtk.VPaned()
        vpaned.set_position(150)
        hbox.pack_start(vpaned, True, True)
        vpaned.show()

        notebook = gtk.Notebook()
        vpaned.add1(notebook)
        notebook.show()

        # Widget view
        widget_view = WidgetTreeView(self)
        self._add_view(widget_view)
        page_num = notebook.append_page(widget_view, gtk.Label(_('Widgets')))
        widget_view.show()

        state = WidgetUIMState()
        self._uim_states[page_num] = state

        # Action view
        self.gactions_view = GActionsView(self)
        self._add_view(self.gactions_view)
        page_num = notebook.append_page(self.gactions_view,
                                        gtk.Label(_('Actions')))
        self.gactions_view.show()

        state = ActionUIMState(self.gactions_view)
        self._uim_states[page_num] = state

        # Sizegroup view
        self.sizegroup_view = SizeGroupView(self)
        self._add_view(self.sizegroup_view)
        page_num = notebook.append_page(self.sizegroup_view,
                                        gtk.Label(_('Size Groups')))
        self.sizegroup_view.show()

        state = SizeGroupUIMState(self.sizegroup_view)
        self._uim_states[page_num] = state

        # Add property editor
        self._editor = Editor(self)
        vpaned.add2(self._editor)
        self._editor.show_all()

        notebook.connect('switch-page', self._on_notebook_switch_page)

        # Statusbar
        statusbar = gtk.Statusbar()
        self._statusbar_menu_context_id = statusbar.get_context_id("menu")
        self._statusbar_actions_context_id = statusbar.get_context_id("actions")
        #main_vbox.pack_end(statusbar, False)
        self._statusbar = statusbar
        #statusbar.show()

        # dnd doesn't seem to work with Konqueror, at least not when
        # gtk.DEST_DEFAULT_ALL or gtk.DEST_DEFAULT_MOTION is used. If
        # handling the drag-motion event it will work though, but it's
        # a bit tricky.
        #application_window.drag_dest_set(gtk.DEST_DEFAULT_ALL,
        #                                 Application.targets,
        #                                 gtk.gdk.ACTION_COPY)

        #application_window.connect('drag-data-received',
        #                           self._dnd_data_received_cb)

        # Enable the current state
        self._active_uim_state = self._uim_states[0]
        self._active_uim_state.enable()
        

        return application_window

    def cb_signal_activated(self, editor, widget, signal):
        callbackname = 'on_%s__%s' % (widget.name, signal.replace('-', '_'))
        self._save_cb(None)
        self.__view.cb_signal_activated(callbackname, self._project.path)

class gazpacho_view(contentview.content_view):

    HAS_TITLE = False
    HAS_CONTROL_BOX = False
    HAS_CLOSE_BUTTON = False
    HAS_DETACH_BUTTON = False


    def init(self):
        self.__main_window = self.service.boss.get_main_window()
        self.__gazpacho = gazpacho_application(self.__main_window, self)
        self.widget.pack_start(self.__gazpacho.get_container())
        self.set_border_width(2)
        

    def open_file(self, filename):
        for project in self.__gazpacho._projects:
            if filename == project.path:
                if project is not self.__gazpacho._project:
                    self.__gazpacho._set_project(project)
                return
        self.__gazpacho.open_project(filename)

    def save(self):
        self.__gazpacho._save_cb(None)

    def save_as(self):
        self.__gazpacho._save_as_cb(None)

    def cut(self):
        """broken"""
        self.uim_state._cut_cb(None)

    def copy(self):
        """broken"""
        self.uim_state._copy_cb(None)

    def paste(self):
        """broken"""
        self.uim_state._paste_cb(None)

    def delete(self):
        """broken"""
        self.uim_state._delete_cb(None)

    def undo(self):
        self.__gazpacho._undo_cb(None)
    
    def redo(self):
        self.__gazpacho._redo_cb(None)

    def about(self):
        self.__gazpacho._about_cb(None)

    def close_all(self):
        for project in self.gaz._projects:
            project.selection_clear(False)
            project.selection_changed()
            for widget in project.widgets:
                widget.destroy()
            #self.gaz._ui_manager.remove_ui(project.uim_id)

    def confirm_close_all(self):
        unsaved = [p for p in self.__gazpacho._projects if p.changed]
        close = self.__gazpacho._confirm_close_projects(unsaved)
        #self.__gazpacho._config.save()
        if close:
            self.close_all()
        return close

    def confirm_close(self):
        proj = self.__gazpacho._project
        if proj is not None:
            if proj.changed:
                close = self.__gazpacho._confirm_close_projects([proj])
            else:
                close = True
            if close:
                for widget in proj.widgets:
                    widget.destroy()
            return close
        return True

    def get_gazpacho(self):
        return self.__gazpacho
    gaz = property(get_gazpacho)

    def get_uim_state(self):
        return self.__gazpacho._active_uim_state

    uim_state = property(get_uim_state)

    def cb_signal_activated(self, signalname, projectpath):
        callback_file_path = '%s.py' % projectpath.rsplit('.', 1)[0]
        if not os.path.exists(callback_file_path):
            mb = gtk.MessageDialog(parent=self.gaz.get_window(),
                flags = 0,
                type = gtk.MESSAGE_INFO,
                buttons = gtk.BUTTONS_YES_NO,
                message_format='You must save your user interface '
                                       'file before continuing.')
            def mbox(messagebox, response):
                if response == gtk.RESPONSE_YES:
                    self.service.call('goto_signal_handler',
                                      glade_filename=projectpath,
                                      callback_filename=callback_file_path,
                                      callback_name=signalname)
                messagebox.destroy()
            mb.connect('response', mbox)
            mb.run()
        else:
            self.service.call('goto_signal_handler',
                              glade_filename=projectpath,
                              callback_filename=callback_file_path,
                              callback_name=signalname)

class ExternalGazpacho(object):

    def __init__(self, service):
        self.service = service
        self.boss = service.boss

    def launch():
        # Delay imports, so command line parsing is not slowed down
        from gazpacho.app.app import gazpacho
        from gazpacho.debugwindow import DebugWindow, show
        gazpacho.window.show()
        self.gazpacho = gazpacho

        #open_project(gazpacho, filename, options.profile)
    def open_project(app, filename, profile):
        return self.gazpacho.open_project(filename)


import pida.core.actions as actions



class gazpacho_service(service.service):

    display_name = 'Gazpacho'

    single_view_type = gazpacho_view
    single_view_book = 'edit'

    class glade_handler(document.document_handler):
        """The glade file handler."""

        globs = ["*.glade"]

        def init(self):
            self.service.handler = self
            document.document_handler.init(self)

        def create_document(self, filename, document_type):
            doc = gazpacho_document(filename=filename, handler=self)
            return doc

        def view_document(self, document):
            new = self.service.call('start')
            self.service.single_view.open_file(document.filename)
            if new:
                self.service.connect_actions()

        def close_document(self, document):
            self.service.single_view.gaz.close_current_project()
            self.service.boss.call_command('buffermanager', 'document_closed',
                                           document=document)

        def act_cut(self, action):
            """Cut the selected item"""
            self.service.single_view.cut()

        def act_copy(self, action):
            """Copy the selected item"""
            self.service.single_view.copy()

        def act_paste(self, action):
            """Paste the selected item"""
            self.service.single_view.paste()

        def act_delete(self, action):
            """Delete the selected item"""
            self.service.single_view.delete()

        def act_save(self, action):
            """Save the user interface file"""
            self.service.single_view.save()

        @actions.action(stock_id=gtk.STOCK_SAVE_AS, label=None)
        def act_save_as(self, action):
            """Save the user interface file as"""
            self.service.single_view.save_as()

        def act_undo(self, action):
            self.service.single_view.undo()

        def act_redo(self, action):
            self.service.single_view.redo()

        def act_about_gazpacho(self, action):
            self.service.single_view.about()

        def get_menu_definition(self):
            return """
              <menubar>
                <menu name="base_file" action="base_file_menu">
                  <placeholder name="SaveFileMenu">
                  <separator />
                  <menuitem action="gazpach+document+save"/>
                  <menuitem action="gazpach+document+save_as"/>
                  <separator />
                  </placeholder>
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                <placeholder name="EditMenu">
                <menuitem action="gazpach+document+undo"/>
                <menuitem action="gazpach+document+redo"/>
                <menuitem action="gazpach+document+cut"/>
                <menuitem action="gazpach+document+copy"/>
                <menuitem action="gazpach+document+paste"/>
                <menuitem action="gazpach+document+delete"/>
                </placeholder>
                <separator />
                </menu>
                <menu name="base_help" action="base_help_menu">
                <menuitem action="gazpach+document+about_gazpacho"/>
                </menu>
              </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
            </placeholder>
            <placeholder name="SaveFileToolbar">
                <separator />
               <toolitem action="gazpach+document+save"/>
               <toolitem action="gazpach+document+save_as"/>
                <separator />
            </placeholder>
            <placeholder name="EditToolbar">
                <separator />
                <toolitem action="gazpach+document+undo"/>
                <toolitem action="gazpach+document+redo"/>    
                <separator />
                <toolitem action="gazpach+document+cut"/>
                <toolitem action="gazpach+document+copy"/>
                <toolitem action="gazpach+document+paste"/>
                <toolitem action="gazpach+document+delete"/>
                <separator />
            </placeholder>
            <placeholder name="ProjectToolbar">
            </placeholder>
            <placeholder name="VcToolbar">
            </placeholder>
            </toolbar>
                            """

    def cmd_open(self, filename):
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)

    def cmd_start(self):
        if 1:
            if self.single_view is None:
                self.__view = self.create_single_view()
                return True
            else:
                self.single_view.raise_page()
                return False
        else:
            self.__view = ExternalGazpacho(self)

    def connect_actions(self):
        for pact, gact in [('gazpach+document+save', 'Save'),
                           ('gazpach+document+save_as', 'SaveAs'),
                           ('gazpach+document+undo', 'Undo'),
                           ('gazpach+document+redo', 'Redo'),
                           ('gazpach+document+cut', 'Cut'),
                           ('gazpach+document+copy', 'Copy'),
                           ('gazpach+document+paste', 'Paste'),
                           ('gazpach+document+delete', 'Delete'),
                           ]:
            self.__connect_action(pact, gact)

    def __connect_action(self, pidaname, gazname):
        pact = self.handler.action_group.get_action(pidaname)
        def _up(act, prop):
            pact.set_sensitive(act.get_sensitive())
        gact = bar_manager._get_action(gazname)
        gact.connect('notify', _up)



    def cmd_create(self, filename):
        f = open(filename, 'w')
        f.write(empty_gazpacho_document)
        f.close()
        self.call('open', filename=filename)

    def cmd_goto_signal_handler(self, glade_filename, callback_filename,
                                callback_name):
        import pida.utils.tepache as tepache
        class dummyopts(object):
            pass
        def get_options_status():
            opts = dummyopts()
            opts.glade_file = glade_filename
            opts.output_file = callback_filename
            opts.use_tabs = False
            opts.no_helper = False
            return opts, True
        tepache.get_options_status = get_options_status
        tepache.main()
        f = open(callback_filename)
        fundef = 'def %s' % callback_name
        for linenumber, line in enumerate(f):
            print line, fundef
            if fundef in line:
                break
        f.close()
        self.boss.call_command('buffermanager', 'open_file_line',
                               filename=callback_filename,
                               linenumber=linenumber + 2)

class gazpacho_document(document.realfile_document):

    ICON_NAME = 'gazpacho'

class widget_editor(Editor):

    def _create_signal_page(self):
        if self._signal_editor:
            return self._signal_editor
        self._signal_editor = signaleditor.SignalEditor(self, self._app)
        self._signal_editor.connect('signal-activated',
            self.row_activated_cb)
        self._vbox_signals.pack_start(self._signal_editor)


empty_gazpacho_document = """<?xml version="1.0" standalone="no"?>
<!--*- mode: xml -*-->
<!DOCTYPE glade-interface SYSTEM "http://gazpacho.sicem.biz/gazpacho-0.1.dtd">
<glade-interface/>
"""

Service = gazpacho_service

