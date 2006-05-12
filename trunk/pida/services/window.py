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

from rat import shiftpaned

import pida.core.actions as actions
import pida.core.service as service

from pida.pidagtk.contentview import ContentManager, create_pida_icon


from pida.model import attrtypes as types
defs = service.definitions


class WindowConfig:

    __order__ = ['layout', 'window_size', 'toolbar_and_menubar']
    class layout(defs.optiongroup):
        """The layout options."""
        __order__ = ['sidebar_on_right', 'vertical_sidebar_split',
                      'small_toolbar', 'sidebar_width']
        label = 'Window Layout'
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

    class window_size(defs.optiongroup):
        """The starting size of the pida window."""
        __order__ = ['width', 'height', 'save_on_shutdown']
        label = 'Window Size'
        class width(defs.option):
            """The starting width in pixels."""
            default = 800
            rtype = types.intrange(0, 2800, 25)
        class height(defs.option):
            """The starting height in pixels."""
            default = 600
            rtype = types.intrange(0, 2800, 25)
        class save_on_shutdown(defs.option):
            """Whether the size will be saved on shutdown."""
            default = True
            rtype = types.boolean

    class toolbar_and_menubar(defs.optiongroup):
        """Options relating to the toolbar and main menu bar."""
        __order__ = ['toolbar_visible', 'menubar_visible', 'sidebar_visible',
                     'viewpan_visible']
        class toolbar_visible(defs.option):
            """Whether the toolbar will start visible."""
            rtype = types.boolean
            default = True
        class menubar_visible(defs.option):
            """Whether the menubar will start visible."""
            rtype = types.boolean
            default = True
        class sidebar_visible(defs.option):
            """Whether the sidebar will start visible."""
            rtype = types.boolean
            default = True
        class viewpan_visible(defs.option):
            """Whether the view pan will be visible."""
            rtype = types.boolean
            default = True
            label = 'Show View Pane'

    def __markup__(self):
        return 'Window and view'

class WindowManager(service.service):
    """Class to control the main window."""

    display_name = 'View'

    config_definition = WindowConfig
    
    def init(self, *args, **kw):
        self.__acels = gtk.AccelGroup()
        self._create_uim()

    def bind(self):
        self._bind_views()
        self._bind_pluginviews()
        self._pack()
        self.__uim.ensure_update()

    def reset(self):
        """Display the window."""
        self._create_window()
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.opts.__model_notify__()

    toolbar = None
    menubar = None

    def cb_layout__small_toolbar(self, val):
        if self.toolbar is None: return
        if val:
            size = gtk.ICON_SIZE_SMALL_TOOLBAR
        else:
            size = gtk.ICON_SIZE_LARGE_TOOLBAR
        self.toolbar.set_icon_size(size)

    def cb_toolbar_and_menubar__toolbar_visible(self, val):
        if self.toolbar is None: return
        if val:
            self.toolbar.show_all()
        else:
            self.toolbar.hide_all()
        act = self.action_group.get_action('window+toggle_toolbar')
        if act.get_active() != val:
            act.set_active(val)

    def cb_toolbar_and_menubar__menubar_visible(self, val):
        if self.menubar is None: return
        if val:
            self.menubar.show_all()
        else:
            self.menubar.hide_all()
        act = self.action_group.get_action('window+toggle_menubar')
        if act.get_active() != val:
            act.set_active(val)

    def cb_toolbar_and_menubar__sidebar_visible(self, val):
        if self.menubar is None: return
        if val:
            self.show_sidebar()
        else:
            self.hide_sidebar()
        act = self.action_group.get_action('window+toggle_sidebar')
        if act.get_active() != val:
            act.set_active(val)

    def cb_toolbar_and_menubar__viewpan_visible(self, val):
        if self.menubar is None: return
        if val:
            self.show_viewpan()
        else:
            self.hide_viewpan()
        act = self.action_group.get_action('window+toggle_viewpan')
        if act.get_active() != val:
            act.set_active(val)

    def stop(self):
        if self.opts.window_size__save_on_shutdown:
            w, h = self.__window.get_size()
            self.opts.window_size__width = w
            self.opts.window_size__height = h

    def cmd_show_window(self):
        # TODO: try to optimize this, maybe show_all is not optimized
        # TODO: and explicit show()s make it faster
        self.__window.show_all()

    def cmd_update_action_groups(self):
        self.__uim.ensure_update()
        ht = self.toolbar.get_parent()
        if ht:
            ht.remove(self.toolbar)
        self.toolbar = self.__uim.get_widget('/toolbar')
        ht.add(self.toolbar)

    def cmd_append_page(self, bookname, view):
        self._cm.add(bookname, view)

    def cmd_remove_page(self, view):
        self._cm.remove(view)

    def cmd_raise_page(self, view):
        self._cm.raise_view(view)

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

    def cmd_next_view(self):
        """Jump to the next view in the viewbook."""
        self.bookview.next_page()

    def cmd_previous_view(self):
        """Jump to the previos view in the viewbook."""
        self.bookview.prev_page()

    def bnd_buffermanager_document_changed(self, document):
        if document.is_new:
            title = 'New File %s' % document.newfile_index
        else:
            title = document.filename
        self.cmd_set_title(title)

    def bnd_editormanager_started(self):
        self.cmd_show_window()

    @actions.action(label='Next View',
                    default_accel='<Alt>Up')
    def act_next_view(self, action):
        """Jump to the next pane in the content book."""
        self.call('next_view')

    @actions.action(label='Previous View',
                    default_accel='<Alt>Down')
    def act_previous_view(self, action):
        """Jump to the next pane in the content book."""
        self.call('previous_view')

    @actions.action(
        default_accel='<Control><Shift>l',
        type=actions.TYPE_TOGGLE,
        label='Too_lbar'
        )
    def act_toggle_toolbar(self, action):
        self.opts.toolbar_and_menubar__toolbar_visible = action.get_active()

    @actions.action(
        type=actions.TYPE_TOGGLE,
        default_accel='<Control><Shift>m',
        label='Menubar'
        )
    def act_toggle_menubar(self, action):
        self.opts.toolbar_and_menubar__menubar_visible = action.get_active()

    @actions.action(
        type=actions.TYPE_TOGGLE,
        default_accel='<Control><Shift>s',
        label='Sidebar'
    )
    def act_toggle_sidebar(self, action):
        self.opts.toolbar_and_menubar__sidebar_visible = action.get_active()

    @actions.action(
        type=actions.TYPE_TOGGLE,
        default_accel='<Control><Shift>v',
        label='Pane Viewer'
    )
    def act_toggle_viewpan(self, action):
        self.opts.toolbar_and_menubar__viewpan_visible = action.get_active()


    def _bind_views(self):
        self._cm = ContentManager()
        self.contentview = self._cm.create_book('content')
        self.contentview.set_tab_pos(gtk.POS_RIGHT)
        self.bookview = self._cm.create_book('view')
        self.editorview = self._cm.create_book('edit')
        self.editorview.set_show_tabs(False)
        self.pluginview = self._cm.create_book('plugin')
        def _s():
            self.contentview.set_current_page(0)
        gtk.idle_add(_s)

    def _bind_pluginviews(self):
        for service in ['buffermanager', 'filemanager', 'projectmanager']:
            svc = self.boss.get_service(service)
            svc.show_view(view=svc.plugin_view)

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
        sidebar_on_right = self.opts.layout__sidebar_on_right
        self.__sidebar = p0 = shiftpaned.SidebarPaned(gtk.HPaned,
                                                    sidebar_on_right)
        self.__mainbox.pack_start(p0)
        sidebar_width = self.opts.layout__sidebar_width
        sidebar = self._pack_sidebar()
        if sidebar_on_right:
            main_pos = 800 - sidebar_width
            self.contentview.set_tab_pos(gtk.POS_LEFT)
            self.pluginview.set_tab_pos(gtk.POS_LEFT)
        else:
            main_pos = sidebar_width
            self.contentview.set_tab_pos(gtk.POS_RIGHT)
            self.pluginview.set_tab_pos(gtk.POS_RIGHT)
        self.__viewpan = p1 = shiftpaned.SidebarPaned(gtk.VPaned, True)
        p0.pack_sub(sidebar, resize=False)
        p0.pack_main(p1, resize=True)
        p0.set_position(main_pos)
        p1.pack_main(self.editorview, resize=True)
        p1.pack_sub(self.bookview, resize=False)
        h = self.opts.window_size__height
        p1.set_position(h - 200)

    def _pack_sidebar(self):
        sidebar_horiz = self.opts.layout__vertical_sidebar_split
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
            self.__window.set_title('PIDA Loves You')
            self.__window.connect('delete-event', self.cb_destroy)
            self.__window.add_accel_group(self.__acels)
            self._connect_drag_events()
            self.__window.add(self.__mainbox)
            w = self.opts.window_size__width
            h = self.opts.window_size__height
            self.__window.resize(w, h)
            self.__window.set_icon(create_pida_icon())


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
                    <menu name="base_project" action="base_project_menu">
                        <placeholder name="ProjectMain" />
                        <placeholder name="ProjectExtras" />
                    </menu> 
                    <menu name="base_python" action="base_python_menu" />
                    <menu name="base_tools" action="base_tools_menu">
                        <placeholder name="ToolsMenu" />
                        <separator />
                        <placeholder name="ExtraToolsMenu" />
                        <separator />
                        <menu name="service_conf" action="base_service_conf_menu" />
                        <separator />
                    </menu>
                    <menu name="base_view" action="base_view_menu">
                        <placeholder name="TopViewMenu" />
                        <separator />
                        <placeholder name="ViewMenu" />
                        <separator />
                    </menu>
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
        self.menubar = self.__uim.get_toplevels(gtk.UI_MANAGER_MENUBAR)[0]
        self.toolbar = self.__uim.get_toplevels(gtk.UI_MANAGER_TOOLBAR)[0]
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
                        <placeholder name="ViewMenu">
                            <separator />
                            <menuitem name="togglesidebar" action="window+toggle_sidebar" />
                            <menuitem action="window+toggle_viewpan" />
                            <menuitem name="toggletoolbar" action="window+toggle_toolbar" />
                            <menuitem name="togglemenubar" action="window+toggle_menubar" />
                            <separator />
                            <menuitem action="window+next_view" />
                            <menuitem action="window+previous_view" />
                        </placeholder>
                    </menu>
                </menubar>
               """

    def get_sidebar_on_right(self):
        return self.opts.layout__sidebar_on_right
    
    def show_sidebar(self):
        self.__sidebar.show_sub()
    
    def hide_sidebar(self):
        self.__sidebar.hide_sub()

    def show_viewpan(self):
        self.__viewpan.show_sub()

    def hide_viewpan(self):
        self.__viewpan.hide_sub()

Service = WindowManager
