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

import gtk
import os

try:
    from gazpacho import application, gladegtk
    from gazpacho.path import pixmaps_dir
    from gazpacho import palette, editor, project, catalog
    from gazpacho.l10n import _
    from gazpacho.gaction import GActionsView, GAction, GActionGroup
except ImportError:
    print "User interface design needs the installation of Gazpacho"
    gazpacho = None

class Gazpacho(object):

    def __init__(self, cb):
        self.cb = cb
        self.app = None
        self.holder = None

    def launch(self, holder=None):
        if not self.app:
            if holder:
                self.app = GazpachoEmbedded(self.cb)
                self.app._pidawindow = self.cb.cw
                holder.pack_start(self.app._window)
                self.holder = holder
            else:
                self.app = GazpachoApplication()
            
            gladegtk.init_gladegtk(self.app)
            self.app.reactor = self
        self.app.show_all()
        self.app.new_project()


class GazpachoApplication(application.Application):

    def _quit_cb(self, action=None):
        projects = self._projects
        for project in projects:
            if project.changed:
                if not self._confirm_close_project(project):
                    return
                self._projects.remove(project)
        self._window.hide_all()

class GazpachoEmbedded(GazpachoApplication):
    
    def __init__(self, cb):
        self.cb = cb
        GazpachoApplication.__init__(self)
    
    def get_window(self): return self._pidawindow
    window = property(get_window)
    
    def _refresh_title(self):
        return
        if self._project:
            title = 'Gazpacho - %s' % self._project.name
        else:
            title = 'Gazpacho'
        self._window.set_title(title)

    def _application_window_create(self):
        
        application_window = gtk.VBox()
        #application_window.move(0, 0)
        #application_window.set_default_size(700, -1)
        #gtk.window_set_default_icon_from_file(join(pixmaps_dir,
        #                                           'gazpacho-icon.png'))
        #application_window.connect('delete-event', self._delete_event)

        # Create the different widgets
        menubar = self._construct_menu_and_toolbar(application_window)

        self._palette = MiniPalette(self._catalogs)
        self._palette.connect('toggled', self._palette_button_clicked)

        self._editor = editor.Editor(self)

        widget_view = self._widget_tree_view_create()

        self.gactions_view = self._gactions_view_create()
        
        self._statusbar = self._construct_statusbar()

        # Layout them on the window
        main_vbox = gtk.VBox()
        application_window.add(main_vbox)

        top_box = gtk.HBox()
        main_vbox.pack_start(top_box, expand=False)

        #top_box.pack_start(toolbar)
        #top_box.pack_start(menubar, False)
        self.menu = menubar

        hbox = gtk.VBox(spacing=6)

        
        self.selector_image = gtk.Image()
        self.selector_image.set_from_file(os.path.join(pixmaps_dir, 'selector.png'))

        self.expander_label = ExpanderLabel(self.cb, self.selector_image)
        hbox.pack_start(self.expander_label, expand=False)
        
        self._palette_expander = gtk.Expander('Widgets')
        self._palette_expander.add(self._palette)
        
        hbox.pack_start(self._palette_expander, False, False)

        vpaned = gtk.VPaned()
        hbox.pack_start(vpaned, True, True)

        notebook = gtk.Notebook()
        notebook.append_page(widget_view, gtk.Label(_('Widgets')))
        notebook.append_page(self.gactions_view, gtk.Label(_('Actions')))
        notebook.set_size_request(200, -1)

        #vpaned.set_position(200)

        vpaned.pack1(notebook, True, True)
        vpaned.pack2(self._editor, True, True)
        self._editor.set_size_request(200, -1)

        main_vbox.pack_start(hbox)
        
        #main_vbox.pack_end(self._statusbar, False)

        #self.refresh_undo_and_redo()

        return application_window
 
    def _palette_button_clicked(self, palette):
        klass = palette.current

        # klass may be None if the selector was pressed
        self._add_class = klass
        if klass and klass.is_toplevel():
            self._command_manager.create(klass, None, self._project)
            self._palette.unselect_widget()
            self._add_class = None
        
        self.expander_label.set_label(self._add_class)
            

    def _construct_menu_and_toolbar(self, application_window):
        actions =(
            ('Gazpacho', None, _('_Gaz')),
            ('FileMenu', None, _('_File')),
            ('New', gtk.STOCK_NEW, _('_New'), '<control>N',
             _('New Project'), self._new_cb),
            ('Open', gtk.STOCK_OPEN, _('_Open'), '<control>O',
             _('Open Project'), self._open_cb),
            ('Save', gtk.STOCK_SAVE, _('_Save'), '<control>S',
             _('Save Project'), self._save_cb),
            ('SaveAs', gtk.STOCK_SAVE_AS, _('_Save As...'),
             '<shift><control>S', _('Save project with different name'),
             self._save_as_cb),
            ('Close', gtk.STOCK_CLOSE, _('_Close'), '<control>W',
             _('Close Project'), self._close_cb),
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), '<control>Q', _('Quit'),
             self._quit_cb),
            ('EditMenu', None, _('_Edit')),
            ('Cut', gtk.STOCK_CUT, _('C_ut'), '<control>X', _('Cut'),
             self._cut_cb),
            ('Copy', gtk.STOCK_COPY, _('_Copy'), '<control>C', _('Copy'),
             self._copy_cb),
            ('Paste', gtk.STOCK_PASTE, _('_Paste'), '<control>V', _('Paste'),
             self._paste_cb),
            ('Delete', gtk.STOCK_DELETE, _('_Delete'), '<control>D',
             _('Delete'), self._delete_cb),
            ('ActionMenu', None, _('_Actions')),
            ('AddAction', gtk.STOCK_ADD, _('_Add action'), '<control>A',
             _('Add an action'), self._add_action_cb),
            ('RemoveAction', gtk.STOCK_REMOVE, _('_Remove action'), None,
             _('Remove action'), self._remove_action_cb),
            ('EditAction', None, _('_Edit action'), None, _('Edit Action'),
             self._edit_action_cb),
            ('ProjectMenu', None, _('_Project')),
            ('DebugMenu', None, _('_Debug')),
            ('HelpMenu', None, _('_Help')),
            ('About', None, _('_About'), None, _('About'), self._about_cb)
            )

        toggle_actions = (
            ('ShowCommandStack', None, _('Show _command stack'), 'F3',
             _('Show the command stack'), self._show_command_stack_cb, False),
            ('ShowClipboard', None, _('Show _clipboard'), 'F4',
             _('Show the clipboard'), self._show_clipboard_cb, False),
            )
        
        undo_action = (
            ('Undo', gtk.STOCK_UNDO, _('_Undo'), '<control>Z',
             _('Undo last action'), self._undo_cb),
            )

        redo_action = (
            ('Redo', gtk.STOCK_REDO, _('_Redo'), '<control>R',
             _('Redo last action'), self._redo_cb),
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

        menu = self._ui_manager.get_widget('/MainMenu')


        #toolbarbox = gtk.VBox()
        #mtoolbar = self._ui_manager.get_widget('/MainToolbar')
        #toolbarbox.pack_start(mtoolbar, expand=False)
        #etoolbar = self._ui_manager.get_widget('/EditBar')
        #toolbarbox.pack_start(etoolbar, expand=False)

        #mtoolbar.set_style(gtk.TOOLBAR_ICONS)
        #mtoolbar.set_icon_size(gtk.ICON_SIZE_BUTTON)

        #etoolbar.set_style(gtk.TOOLBAR_ICONS)
        #etoolbar.set_icon_size(gtk.ICON_SIZE_BUTTON)
        
        #print menu, type(menu)
        #bar = gtk.MenuBar()
        
        #parentmenu = gtk.MenuItem(label='Gazpacho')
        #submenu = gtk.Menu()
        #for child in menu.get_children():
        #    menu.remove(child)
        #    print child
        #    submenu.append(child)
        #parentmenu.set_submenu(submenu)
        #bar.append(parentmenu)

        return menu

    def refresh_undo_and_redo(self):
        #return
        undo_item = redo_item = None
        if self._project is not None:
            pri = self._project.prev_redo_item
            if pri != -1:
                undo_item = self._project.undo_stack[pri]
            if pri + 1 < len(self._project.undo_stack):
                redo_item = self._project.undo_stack[pri + 1]

        #undo_action = self._ui_manager.get_action('/MainToolbar/Undo')
        #undo_group = undo_action.get_property('action-group')
        #undo_group.set_sensitive(undo_item is not None)
        self.undo_button.set_sensitive(undo_item is not None)
        undo_widget = self._ui_manager.get_widget('/MainMenu/Gazpacho/EditMenu/Undo')
        label = undo_widget.get_child()
        if undo_item is not None:
            label.set_text_with_mnemonic(_('_Undo: %s') % \
                                         undo_item.description)
        else:
            label.set_text_with_mnemonic(_('_Undo: Nothing'))
            
        #redo_action = self._ui_manager.get_action('/MainToolbar/Redo')
        #redo_group = redo_action.get_property('action-group')
        #redo_group.set_sensitive(redo_item is not None)
        self.redo_button.set_sensitive(redo_item is not None)
        redo_widget = self._ui_manager.get_widget('/MainMenu/Gazpacho/EditMenu/Redo')
        label = redo_widget.get_child()
        if redo_item is not None:
            label.set_text_with_mnemonic(_('_Redo: %s') % \
                                         redo_item.description)
        else:
            label.set_text_with_mnemonic(_('_Redo: Nothing'))

        if self._command_stack_window is not None:
            command_stack_view = self._command_stack_window.get_child()
            command_stack_view.update()
 
    def _add_project(self, project):
        # if the project was previously added, don't reload
        for prj in self._projects:
            if prj.path and prj.path == project.path:
                self._set_project(prj)
                return

        self._projects.insert(0, project)

        # add the project in the /Project menu
        project_action= gtk.Action(project.name, project.name, project.name,
                                   '')

        project_action.connect('activate', self._set_project, project)
        project_ui = """
        <ui>
          <menubar name="MainMenu">
            <menu action="Gazpacho">
            <menu action="ProjectMenu">
              <menuitem action="%s"/>
            </menu>
            </menu>
          </menubar>
        </ui>
        """ % project.name
        action_group = self._ui_manager.get_action_groups()[0]
        action_group.add_action(project_action)
        
        project.uim_id = self._ui_manager.add_ui_from_string(project_ui)

        # connect to the project signals so that the editor can be updated
        project.connect('widget_name_changed', self._widget_name_changed_cb)
        project.connect('selection_changed',
                         self._project_selection_changed_cb)

        # make sure the palette is sensitive
        self._palette.set_sensitive(True)

        self._set_project(project)

    def _widget_tree_view_create(self):
        from gazpacho.widgettreeview import WidgetTreeView
        view = WidgetTreeView(self)
        self._project_views.insert(0, view)
        view.set_project(self._project)
        #view.set_size_request(150, 200)
        view.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        return view

    def _gactions_view_create(self):
        view = GActionsView()
        view.set_project(self._project)
        self._project_views.insert(0, view)
        #view.set_size_request(150, -1)
        view.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        return view


    def _command_stack_view_create(self):
        view = CommandStackView()
        self._project_views.insert(0, view)
        view.set_project(self._project)
        #view.set_size_request(300, 200)
        view.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        return view

    def _clipboard_view_create(self):
        view = ClipboardView(self._clipboard)
        view.set_size_request(300, 200)
        view.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        return view


class ExpanderLabel(gtk.HBox):

    def __init__(self, cb, selectorimage):
   
        self.cb = cb
        self.selectorimage = selectorimage
        gtk.HBox.__init__(self)
        
        self.image_holder = gtk.EventBox()
        self.pack_start(self.image_holder, expand=False)
        
        self.label = gtk.Label()
        self.pack_start(self.label)

        self.selector = gtk.RadioButton(None)
        self.selector.set_mode(False)
        self.selector.set_relief(gtk.RELIEF_NONE)
        self.selector.add(get_resized_image_copy(self.selectorimage, 14))
        self.pack_start(self.selector, expand=False)
        self.set_label(None)
        #self.selector.connect('toggled', self._on_button_toggled)
        

    def _selector_toggled(self, *args):
        pass

    def set_label(self, klass):
        image = self.selectorimage
        text = 'Selector'
        if klass:
            image = klass.icon
            text = klass.name
            self.selector.set_active(True)
        else:
            self.selector.set_active(True)
        
        for child in self.image_holder.get_children():
            self.image_holder.remove(child)

        new_image = get_resized_image_copy(image, 14)
        self.image_holder.add(new_image)
        self.label.set_label(text)
        self.show_all()


def get_resized_image_copy(image, size):
    pb = image.get_pixbuf().scale_simple(size, size, gtk.gdk.INTERP_HYPER)
    new_image = gtk.Image()
    new_image.set_from_pixbuf(pb)
    return new_image
    

class MiniPalette(palette.Palette):
    
    def __init__(self, catalogs):
        gtk.VBox.__init__(self)

        # The GladeWidgetClass corrisponding to the selected button. NULL if
        # the selector button is pressed.
        self._current = None

        self.pack_start(self._selector_new(), False)
        self.pack_start(gtk.HSeparator(), False, padding=3)

        #The vbox that contains the titles of the sections
        self._groups_vbox = gtk.HBox()
        self.pack_start(self._groups_vbox, False)
        self.pack_start(gtk.HSeparator(), False, padding=3)

        #  Where we store the different catalogs
        self._notebook = gtk.Notebook()
        self._notebook.set_show_tabs(False)
        self._notebook.set_show_border(False)
        self.pack_end(self._notebook)

        # The number of sections in this palette
        self._nb_sections = 0

        # Each section of the palette has a button. This is the
        # sections_button_group list
        self._sections_button_group = []

        for catalog in catalogs:
            for group in catalog.widget_groups:
                self.append_widget_group(group)

