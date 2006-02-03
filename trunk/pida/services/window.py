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

import os

import gtk

import pida.core.actions as actions
import pida.core.service as service
import pida.pidagtk.window as window
import pida.pidagtk.expander as expander
import pida.pidagtk.contentbook as contentbook


types = service.types
defs = service.definitions

from pkg_resources import Requirement, resource_filename
icon_file = resource_filename(Requirement.parse('pida'),
                              'pida-icon.png')
im = gtk.Image()
im.set_from_file(icon_file)
im2 = gtk.Image()
im2.set_from_file(icon_file)

class SplashWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER)
        hb = gtk.HBox()
        hb.set_property('border-width', 36)
        self.add(hb)
        hb.pack_start(im2, padding=12)
        self._msg = gtk.Label()
        self._msg.set_alignment(0.8, 0.8)
        hb.pack_start(self._msg)
        
    def message(self, msg):
        self._msg.set_markup(msg)

splash = SplashWindow()
#splash.show_all()

class WindowManager(service.service):
    """Class to control the main window."""

    display_name = 'View'

    class layout(defs.optiongroup):
        """The layout options."""
        class sidebar_on_right(defs.option):
            """Whether the sidebar will appear on the right."""
            default = False
            rtype = types.boolean
        class vertical_sidebar_split(defs.option):
            """Whether the main sidebar componens will be split by a vertical separator"""
            rtype = types.boolean
            default = False
        class small_toolbar(defs.option):
            """Whether the toolbar will be displayed with small buttons."""
            rtype = types.boolean
            default = False
        class sidebar_width(defs.option):
            """The width of the sidebar."""
            default = 200
            rtype = types.intrange(75, 1800, 25)

    class toolbar_and_menubar(defs.optiongroup):
        """Options relating to the toolbar and main menu bar."""
        class toolbar_hidden(defs.option):
            """Whether the toolbar will start visible."""
            rtype = types.boolean
            default = False
        class menubar_hidden(defs.option):
            """Whether the menubar will start visible."""
            rtype = types.boolean
            default = False

    def init(self):
        self.__splash = splash
        self.__splash.message('<b>Starting PIDA</b>')
        self.__acels = gtk.AccelGroup()
        self._create_uim()

    def bind(self):
        self._bind_views()
        self._bind_pluginviews()
        self._pack()
        self.__uim.ensure_update()

    def reset(self):
        """Display the window."""
        if self.opt('layout', 'small_toolbar'):
            size = gtk.ICON_SIZE_SMALL_TOOLBAR
        else:
            size = gtk.ICON_SIZE_LARGE_TOOLBAR
        tbact = self.action_group.get_action('window+toggle_toolbar')
        tbact.set_active(self.opt('toolbar_and_menubar',
                                      'toolbar_hidden'))
        menact = self.action_group.get_action('window+toggle_menubar')
        menact.set_active(self.opt('toolbar_and_menubar',
                                       'menubar_hidden'))
        self._show_menubar()
        self._show_toolbar()
        self._create_window()
        self.toolbar.set_icon_size(size)

    def cmd_show_window(self):
        self.__window.show_all()
        self._show_menubar()
        self._show_toolbar()

    def cmd_update_action_groups(self):
        self.__uim.ensure_update()
        ht = self.toolbar.get_parent()
        if ht:
            ht.remove(self.toolbar)
        self.toolbar = self.__uim.get_widget('/toolbar')
        ht.add(self.toolbar)

    def cmd_append_page(self, bookname, view):
        self._append_page(bookname, view)

    def cmd_remove_pages(self, bookname):
        if bookname in self.__viewbooks:
            book = self.__viewbooks[bookname]
            book.detach_pages()

    def cmd_register_action_group(self, actiongroup, uidefinition):
        self.__uim.insert_action_group(actiongroup, 0)
        self.__uim.add_ui_from_string(uidefinition)
        for action in actiongroup.list_actions():
            if hasattr(action, 'bind_accel'):
                action.bind_accel(self.__acels)
        self.__uim.ensure_update()

    def cmd_unregister_action_group(self, actiongroup):
        self.__uim.remove_action_group(actiongroup)
        actiongroup.set_visible(False)
        self.__uim.ensure_update()

    def cmd_get_action_groups(self):
        return self.__uim.get_action_groups()

    def cmd_get_ui_widget(self, path):
        return self.__uim.get_widget(path)

    def cmd_input(self, callback_function, prompt='?', prefill=''):
        dialog = gtk.Dialog(title=prompt,
            parent=self.boss.get_main_window(),
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                     gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
                     
        hb = gtk.HBox(spacing=6)
        dialog.vbox.pack_start(hb)
        hb.set_border_width(6)
        hb.pack_start(gtk.Label(prompt), expand=False)
        name_entry = gtk.Entry()
        hb.pack_start(name_entry)
        name_entry.set_text(prefill)
        hb.show_all()
        def response(dialog, response):
            if response == gtk.RESPONSE_ACCEPT:
                text = name_entry.get_text()
                callback_function(text)
            dialog.destroy()
        dialog.connect('response', response)
        dialog.run()

    def cmd_set_title(self, title):
        """Set the window title.
        
        title: a string representation of the new title."""
        self.__window.set_title(title)

    def bnd_buffermanager_document_changed(self, document):
        self.call('set_title', title=document.filename)

    def bnd_editormanager_started(self):
        self.__splash.destroy()
        self.call('show_window')

    @actions.action(
        default_accel='<Control><Shift>l',
        type=actions.TYPE_TOGGLE,
        label='Hide toolbar'
        )
    def act_toggle_toolbar(self, action):
        self.set_option('toolbar_and_menubar', 'toolbar_hidden',
                        action.get_active())
        self._show_toolbar()

    @actions.action(
        type=actions.TYPE_TOGGLE,
        default_accel='<Control><Shift>m',
        label='Hide menu bar'
        )
    def act_toggle_menubar(self, action):
        self.set_option('toolbar_and_menubar', 'menubar_hidden',
                        action.get_active())
        self._show_menubar()

    def _show_menubar(self):
        if self.opt('toolbar_and_menubar', 'menubar_hidden'):
            self.menubar.hide_all()
        else:
            self.menubar.show_all()

    def _show_toolbar(self):
        if self.opt('toolbar_and_menubar', 'toolbar_hidden'):
            self.toolbar.hide_all()
        else:
            self.toolbar.show_all()

    def _bind_views(self):
        self.contentview = contentbook.ContentBook()
        self.editorview = contentbook.ContentBook(show_tabs=False)
        self.bookview = contentbook.ContentBook()
        self.bookview.notebook.set_tab_pos(gtk.POS_TOP)
        self.externalview = window.external_book()
        self.pluginview = contentbook.ContentBook()
        self.__viewbooks = {'content': self.contentview,
                            'view': self.bookview,
                            'plugin': self.pluginview,
                            'edit': self.editorview,
                            'ext': self.externalview}
        self.menubar = self.__uim.get_toplevels(gtk.UI_MANAGER_MENUBAR)[0]
        self.toolbar = self.__uim.get_toplevels(gtk.UI_MANAGER_TOOLBAR)[0]

    def _bind_pluginviews(self):
        for service in self.boss.services:
            if service.plugin_view_type is not None:
                if service.NAME in ['buffermanager', 'projectmanager',
                                    'filemanager']:
                    self.contentview.append_page(service.plugin_view)
                else:
                    self.pluginview.append_page(service.plugin_view)
        #for service in self.boss.services:
        #    if service.lang_view_type is not None:
        #        self.pluginview.append_page(service.lang_view)

    def _pack(self):
        self.__mainbox = gtk.VBox()
        self._pack_toolbox()
        self._pack_panes()

    def _pack_toolbox(self):
        self.__toolbox = gtk.VBox()
        self.__toolbox.pack_start(self.menubar, expand=False)
        self.__toolbox.pack_start(self.toolbar, expand=False)
        self.__mainbox.pack_start(self.__toolbox, expand=False)

    def _pack_panes(self):
        p0 = gtk.HPaned()
        self.__mainbox.pack_start(p0)
        sidebar_width = self.opt('layout', 'sidebar_width')
        sidebar_on_right = self.opt('layout', 'sidebar_on_right')
        sidebar = self._pack_sidebar()
        sidebar.show()
        if sidebar_on_right:
            side_func = p0.pack2
            main_func = p0.pack1
            main_pos = 800 - sidebar_width
            self.contentview.notebook.set_tab_pos(gtk.POS_LEFT)
            self.pluginview.notebook.set_tab_pos(gtk.POS_LEFT)
        else:
            side_func = p0.pack1
            main_func = p0.pack2
            main_pos = sidebar_width
            self.contentview.notebook.set_tab_pos(gtk.POS_RIGHT)
            self.pluginview.notebook.set_tab_pos(gtk.POS_RIGHT)
        p1 = gtk.VPaned()
        p1.show()
        side_func(sidebar, resize=False)
        main_func(p1, resize=True)
        p0.set_position(main_pos)
        p1.pack1(self.editorview, resize=True)
        p1.pack2(self.bookview, resize=False)
        p1.set_position(430)

    def _pack_sidebar(self):
        sidebar_horiz = self.opt('layout', 'vertical_sidebar_split')
        if sidebar_horiz:
            box = gtk.HPaned()
        else:
            box = gtk.VPaned()
        box.pack1(self.contentview, resize=True)
        box.pack2(self.pluginview, resize=True)
        return box

    def _create_window(self):
        if not self.__started:
            self.__started = True
            self.__window = gtk.Window()
            self.__window.connect('delete-event', self.cb_destroy)
            self.__window.add_accel_group(self.__acels)
            self._connect_drag_events()
            self.__window.add(self.__mainbox)
            self.__window.resize(800, 600)
            self.__window.set_icon(im.get_pixbuf())

    def _append_page(self, bookname, page):
        self.__viewbooks[bookname].append_page(page)
        self.__viewbooks[bookname].show_all()

    def _create_uim(self):
        self.__uim = gtk.UIManager()
        ag = gtk.ActionGroup('baseactions')
        ag.add_actions([
            ('base_file_menu', None, '_File'),
            ('base_edit_menu', None, '_Edit'),
            ('base_project_menu', None, '_Project'),
            ('base_python_menu', None, '_Python'),
            ('base_tools_menu', None, '_Tools'),
            ('base_view_menu', None, '_View'),
            ('base_pida_menu', None, '_Debugging Pida'),
            ('base_help_menu', None, '_Help'),
            ('base_service_conf_menu', None, '_Service configuration')
            ])
        menudef = """
                <menubar>
                    <menu name="base_file" action="base_file_menu">
                        <separator />
                        <placeholder name="OpenFileMenu" />
                        <separator />
                        <placeholder name="SaveFileMenu" />
                        <placeholder name="SubSaveFileMenu" />
                        <separator />
                        <placeholder name="ExtrasFileMenu" />
                        <separator />
                        <placeholder name="GlobalFileMenu" />
                    </menu>
                    <menu name="base_edit" action="base_edit_menu">
                        <placeholder name="EditMenu" />
                        <placeholder name="EditSearchMenu" />
                        <placeholder name="SubEditSearchMenu" />
                        <placeholder name="SubPreferencesMenu" />
                        <placeholder name="PreferencesMenu" />
                    </menu>
                    <menu name="base_project" action="base_project_menu" />
                    <menu name="base_python" action="base_python_menu" />
                    <menu name="base_tools" action="base_tools_menu">
                        <placeholder name="ToolsMenu" />
                        <separator />
                        <placeholder name="ExtraToolsMenu" />
                        <separator />
                        <menu name="service_conf" action="base_service_conf_menu" />
                        <separator />
                    </menu>
                    <menu name="base_view" action="base_view_menu" />
                    <menu name="base_pida" action="base_pida_menu" />
                    <menu name="base_help" action="base_help_menu" />
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
                </placeholder>
                </toolbar>
                """
        self.call('register_action_group',
                    actiongroup=ag,
                    uidefinition=menudef)
        self.__started = False

    def _debug_uim(self):
        print self.__uim.get_ui()
        ag = self.__uim.get_action_groups()
        for a in ag:
            print a.get_name(), a.get_visible()
            acts = a.list_actions()
            for act in acts:
                print '\t', act, act.get_name(), act.get_visible()

    def _connect_drag_events(self):
        def drag_motion(win, drag, x, y, timestamp):
            self.buffermanager.drag_highlight()

        def drag_leave(win, drag, timestamp):
            self.buffermanager.drag_unhighlight()

        def drag_drop(win, drag, x, y, selection, info, timestamp):
            path = selection.data.strip()[7:]
            if os.path.isdir(path):
                self.boss.call_command('filemanager', 'browse',
                                       directory=path)
            elif os.path.exists(path):
                self.boss.call_command('buffermanager', 'open_file',
                                       filename=path)
            return True

        self.__window.connect('drag-motion', drag_motion)
        self.__window.connect('drag-leave', drag_leave)
        self.__window.connect('drag-data-received', drag_drop)

    def get_view(self):
        """Return the main window."""
        return self.__window

    view = property(get_view)

    def cb_destroy(self, window, *args):
        can_close = self.boss.call_command("editormanager", "can_close")
        if can_close:
            self.boss.stop()
        return not can_close

    def get_menu_definition(self):
        return """ 
                <menubar>
                <menu name="base_view" action="base_view_menu" >
                <menuitem name="toggletoolbar" action="window+toggle_toolbar" />
                <menuitem name="togglemenubar" action="window+toggle_menubar" />
                </menu>
                </menubar>
               """

Service = WindowManager
