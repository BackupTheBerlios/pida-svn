
from pida.utils.pgd import main, kiwiviews, mainwindow
import gtk
import gobject
from pida.core import service, actions
from pida.model import attrtypes as types
from pida.pidagtk import contentview

defs = service.definitions

class ParentDelegate(kiwiviews.PythonSlaveDelegate):

    def __init__(self, parent, *args, **kw):
        self._parent = parent
        #self._widget = widget
        super(ParentDelegate, self).__init__(*args, **kw)

    def create_toplevel_widget(self):
        self.f = gtk.Frame()
        mainwindow.pack_container(self.f, self)
        return self.f

class DebugView(contentview.content_view):

    ICON_NAME = 'gtk-debug'
    
    SHORT_TITLE = 'Debugger'

    HAS_CONTROL_BOX = True
    
    LONG_TITLE = 'Python Debugger'
    
    def init(self):
        pass

class Debugger(service.service):
    
    class DebugView(defs.View):
        view_type = DebugView
        book_name = 'view'
    
    def reset(self):
        self._document = None
        self._view = None
        _ga = lambda n: self.action_group.get_action('pythondebugger+%s' % n)
        self._docacts = {}
        for act in ['step', 'next', 'return', 'stop', 'break', 'go']:
            self._docacts[act] = _ga(act)
        print self._docacts
        for act in self._docacts.values():
            act.set_visible(False)
            act.set_sensitive(False)
    
    @actions.action(stock_id='gtk-debug')
    def act_debug(self, action):
        if self._document and not self._document.is_new:
            self.launch(self._document.filename)
    
    @actions.action(stock_id=gtk.STOCK_MEDIA_NEXT)
    def act_step(self, action):
        self._view.app.session_manager.request_step()
    
    @actions.action(stock_id=gtk.STOCK_MEDIA_PLAY)
    def act_go(self, action):
        self._view.app.session_manager.request_go()

    @actions.action(stock_id=gtk.STOCK_MEDIA_PREVIOUS)
    def act_return(self, action):
        self._view.app.session_manager.request_return()
    
    @actions.action(stock_id=gtk.STOCK_MEDIA_PAUSE)
    def act_break(self, action):
        self._view.app.self.session_manager.request_break()

    @actions.action(stock_id=gtk.STOCK_MEDIA_FORWARD)
    def act_next(self, action):
        self._view.app.session_manager.request_next()

    @actions.action(label='Debug file')
    def act_launch(self, action):
        dlg = gtk.FileChooserDialog(parent=self.main_window.window,
                                    title='Select script to launch',
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK,
                                             gtk.RESPONSE_ACCEPT,
                                             ))
        dlg.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        filename = None
        response = dlg.run()
        if response == gtk.RESPONSE_ACCEPT:
            filename = dlg.get_filename()
            self.session_manager.launch_filename(filename)
        dlg.destroy()
 
    def act_stop(self, action):
        def _s():
            self._view.app.session_manager.save_breakpoints()
            self._view.app.session_manager.stop_debuggee()
        gobject.idle_add(_s)
    
    def bnd_buffermanager_document_changed(self, document):
        self._document = document
        
    def launch(self, filename):
        if self._view is None:
            self._view = v = self.create_view('DebugView')
            ParentDelegate.window = self.boss.get_main_window()
            main.embed(v, ParentDelegate)
            f = v.app.main_window.f
            v.app.master = self
            v.widget.pack_start(f)
            v.app.source_goto = self.goto_source 
            f.show_all()
            self.show_view(view=v)
            for act in self._docacts.values():
                act.set_visible(True)
    
        else:
            self._view.raise_page()
        self._view.long_title = 'Debugging: %s' % filename
        self._view.app.launch(filename)
    
    def goto_source(self, filename, linenumber):
        def goto():
            self.boss.call_command('buffermanager', 'open_file_line',
                filename=filename, linenumber=linenumber)
        gobject.idle_add(goto)
    
    def view_closed(self, view):
        self.act_stop(None)
        def finish():
            self._view = None
            for act in self._docacts.values():
                act.set_visible(False)
        gobject.idle_add(finish)
    
    def get_menu_definition(self):
        return """
                <menubar>
                    <menu action="base_python_menu" name="base_python">
                        <menuitem action="pythondebugger+debug" />
                        <menuitem action="pythondebugger+launch" />
                    </menu>
                </menubar>
           <toolbar>
            <placeholder name="ToolsToolbar">
            <separator />
            <toolitem action="pythondebugger+debug"/>
            <separator />
            <toolitem action="pythondebugger+go"/>
            <toolitem action="pythondebugger+break"/>
            <separator />
            <toolitem action="pythondebugger+step"/>
            <toolitem action="pythondebugger+next"/>
            <toolitem action="pythondebugger+return"/>
            <toolitem action="pythondebugger+stop"/>
            <separator />
            </placeholder>
            </toolbar>
               """

    def update_state(self, state):
        smap = {
            'broken': ['step', 'next', 'return', 'go', 'stop'],
            'running': ['stop', 'break'],
            'detached': ['launch', 'reload'],
            'spawning': [],
            }
        for act in self._docacts:
            if state in smap:
                if (act in smap[state] or
                    act.endswith('Menu')):
                    self._docacts[act].set_sensitive(True)
                else:
                    self._docacts[act].set_sensitive(False)
        
    
Service = Debugger