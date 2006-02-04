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

# gazpacho imports
from gazpacho import palette
from gazpacho import signaleditor
from gazpacho.editor import Editor
import gazpacho.app.app as application
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


class gazpacho_application(application.Application):
    
    def __init__(self, app_window, view):
        self.__app_window = app_window
        self.__view = view
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
        application_window = gtk.VBox()
        # Layout them on the window
        main_vbox = gtk.VBox()
        application_window.add(main_vbox)
        # Create actions that are always enabled

        hbox = gtk.HBox(spacing=6)
        main_vbox.pack_start(hbox)
        
        pal = palette.Palette()
        pal.connect('toggled', self._palette_button_clicked)
        pal_parent = pal.get_parent()
        if pal_parent is not None:
            pal_parent.remove(pal)
        hbox.pack_start(pal, False, False)

        vpaned = gtk.VPaned()
        vpaned.set_position(150)
        hbox.pack_start(vpaned, True, True)

        notebook = gtk.Notebook()
        vpaned.add1(notebook)

        # Widget view
        widget_view = WidgetTreeView(self)
        self._add_view(widget_view)
        page_num = notebook.append_page(widget_view, gtk.Label(('Widgets')))

        state = WidgetUIMState()
        self._uim_states[page_num] = state
        
        # Action view
        self.gactions_view = GActionsView(self)
        self._add_view(self.gactions_view)
        page_num = notebook.append_page(self.gactions_view, gtk.Label(('Actions')))

        state = ActionUIMState(self.gactions_view)
        self._uim_states[page_num] = state

        # Sizegroup view
        self.sizegroup_view = SizeGroupView(self)
        self._add_view(self.sizegroup_view)
        page_num = notebook.append_page(self.sizegroup_view, gtk.Label(('Size Groups')))

        state = SizeGroupUIMState(self.sizegroup_view)
        self._uim_states[page_num] = state

        # Add property editor
        self._editor = widget_editor(self)
        self._editor.row_activated_cb = self.cb_signal_activated
        vpaned.add2(self._editor)

        notebook.connect('switch-page', self._switch_page_cb)

        # Statusbar
        statusbar = gtk.Statusbar()
        self._statusbar_menu_context_id = statusbar.get_context_id("menu")
        self._statusbar_actions_context_id = statusbar.get_context_id("actions")
        main_vbox.pack_end(statusbar, False)
        self._statusbar = statusbar
        
        # dnd doesn't seem to work with Konqueror, at least not when
        # gtk.DEST_DEFAULT_ALL or gtk.DEST_DEFAULT_MOTION is used. If
        # handling the drag-motion event it will work though, but it's
        # a bit tricky.
        #application_window.drag_dest_set(gtk.DEST_DEFAULT_ALL,
        #                                 Application.targets,
        #                                 gtk.gdk.ACTION_COPY)
        
        #application_window.connect('drag_data_received',
        #                           self._dnd_data_received_cb)

        # Enable the current state
        self._active_uim_state = self._uim_states[0]
        #self._active_uim_state.enable()
        
        return application_window
       
    def cb_signal_activated(self, editor, widget, signal):
        callbackname = 'on_%s__%s' % (widget.name, signal.replace('-', '_'))
        self._save_cb(None)
        self.__view.cb_signal_activated(callbackname, self._project.path)


class gazpacho_view(contentview.content_view):

    HAS_TITLE = False

    def init(self):
        self.__main_window = self.service.boss.get_main_window()
        self.__gazpacho = gazpacho_application(self.__main_window, self)
        self.widget.pack_start(self.__gazpacho.get_container())
        

    def open_file(self, filename):
        for project in self.__gazpacho._projects:
            if filename == project.path:
                self.__gazpacho._set_project(project)
                return
        self.__gazpacho.open_project(filename)

    def save(self):
        self.__gazpacho._save_cb(None)

    def save_as(self):
        self.__gazpacho._save_as_cb(None)

    def cut(self):
        self.__gazpacho._cut_cb(None)

    def copy(self):
        self.__gazpacho._copy_cb(None)

    def paste(self):
        self.__gazpacho._paste_cb(None)

    def delete(self):
        self.__gazpacho._delete_cb(None)

    def undo(self):
        self.__gazpacho._undo_cb(None)
    
    def redo(self):
        self.__gazpacho._redo_cb(None)

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


class gazpacho_service(service.service):

    display_name = 'Gazpacho'

    single_view_type = gazpacho_view
    single_view_book = 'edit'

    class glade_handler(document.document_handler):
        """The glade file handler."""

        globs = ["*.glade"]

        def create_document(self, filename, document_type):
            doc = gazpacho_document(filename=filename, handler=self)
            return doc

        def view_document(self, document):
            self.service.call('start')
            self.service.single_view.open_file(document.filename)
            self.service.current_document = document

        def act_cut(self, action):
            self.service.single_view.cut()

        def act_copy(self, action):
            self.service.single_view.copy()

        def act_paste(self, action):
            self.service.single_view.paste()

        def act_delete(self, action):
            self.service.single_view.delete()

        def act_save(self, action):
            self.service.single_view.save()

        def act_save_as(self, action):
            self.service.single_view.save_as()

        def act_undo(self, action):
            self.service.single_view.undo()

        def act_redo(self, action):
            self.service.single_view.redo()

        def get_menu_definition(self):
            return """
              <menubar>
                <menu name="base_file" action="base_file_menu">
                  <separator />
                  <menuitem action="gazpach+document+save"/>
                  <menuitem action="gazpach+document+save_as"/>
                  <separator />
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                <menuitem action="gazpach+document+undo"/>
                <menuitem action="gazpach+document+redo"/>
                <separator />
                <menuitem action="gazpach+document+cut"/>
                <menuitem action="gazpach+document+copy"/>
                <menuitem action="gazpach+document+paste"/>
                <menuitem action="gazpach+document+delete"/>
                </menu>
                <menu action="base_project_menu">
                </menu>
                <menu action="base_help_menu">
                <menuitem action="About"/>
                </menu>
              </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
            </placeholder>
            <placeholder name="SaveFileToolbar">
                <separator />
               <toolitem action="gazpach+document+save"/>
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
        self.create_single_view()
        self.single_view.raise_page()

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

    def act_user_interface_designer(self, action):
        """Start the user interface designer Gazpacho."""
        self.call('start')
        
    def cb_single_view_closed(self, view):
        self.boss.call_command('buffermanager', 'file_closed',
                        filename=self.current_document.filename)

    def confirm_single_view_controlbar_clicked_close(self, view):
        return view.confirm_close()
        
    def get_current_document(self):
        return self.__current_document

    def set_current_document(self, value):
        self.__current_document = value
    
    current_document = property(get_current_document, set_current_document)
            

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

