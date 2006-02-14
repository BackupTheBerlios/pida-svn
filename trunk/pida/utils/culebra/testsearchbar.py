import unittest
#from guitest import gtktest
from searchbar import SearchBar
from common import ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD, ACTION_FIND_TOGGLE
from rat import util
from buffers import CulebraBuffer
import gtk
from bar import VisibilitySync

class MockTextView:
    forward = None
    def find(self, forward=True):
        self.forward = forward
    
    
class TestVisibilitySync(unittest.TestCase):
    def setUp(self):
        self.w = gtk.Label()
        self.t = gtk.ToggleAction("Foo", None, None, "gtk-open")
        
    def assertVisible(self):
        assert self.w.get_property("visible")
    
    def assertNotVisible(self):
        assert not self.w.get_property("visible")
    
    def assertActive(self):
        assert self.t.get_active()
    
    def assertNotActive(self):
        assert not self.t.get_active()
        
    def test_link(self):
        self.assertNotVisible()
        self.assertNotActive()
        self.t.set_active(True)
        self.assertActive()
        
        v = VisibilitySync(self.w, self.t)
        self.assertNotActive()
        
        self.w.show()
        self.assertVisible()
        self.assertActive()
        
        self.w.hide()
        self.assertNotVisible()
        self.assertNotActive()

        self.t.set_active(True)
        self.assertVisible()
        self.assertActive()
        
        self.t.set_active(False)
        self.assertNotVisible()
        self.assertNotActive()
        
        # Remove the link, now they are independet
        v = None
        
        self.w.show()
        self.assertVisible()
        self.assertNotActive()

        self.w.hide()
        self.assertNotVisible()
        self.assertNotActive()

        self.t.set_active(True)
        self.assertNotVisible()
        self.assertActive()
        
        self.t.set_active(False)
        self.assertNotVisible()
        self.assertNotActive()
        
class TestSearchBar(unittest.TestCase):
    def setUp(self):
        self.ag = gtk.ActionGroup("a")
        for name in (ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD):
            self.ag.add_action(gtk.Action(name, None, None, "gtk-open"))
        self.ag.add_action(gtk.ToggleAction(ACTION_FIND_TOGGLE, None, None, "gtk-open"))
        self.buff = CulebraBuffer()
        self.view = MockTextView()
        self.bar = SearchBar(self.view, self.ag)
        self.bar.set_buffer(self.buff)
        
    def test_widgets(self):
        view = self.view
        
        bar = self.bar
        w = bar.widget
        assert util.find_child_widget(w, "label") is not None
        entry = util.find_child_widget(w, "entry")
        assert entry is not None
        fw = util.find_child_widget(w, "forward")
        assert fw is not None
        bw = util.find_child_widget(w, "backward")
        assert bw is not None
    
    def test_sync(self):
        bar = self.bar
        w = bar.widget
        entry = util.find_child_widget(w, "entry")
        fw = util.find_child_widget(w, "forward")

        self.assertEquals("", entry.get_text())
        self.assertEquals("", self.buff.search_text)
        
        entry.set_text("foo")
        self.assertEquals("foo", self.buff.search_text)
    
        self.buff.search_text = "bar"
        self.assertEquals("bar", entry.get_text())
        
        # Check if the event listeners' decrease
        evts = self.buff.search_component.events
        changed = len(evts._events["changed"])
        no_more = len(evts._events["no-more-entries"])
        b = CulebraBuffer()
        self.bar.set_buffer(b)
        self.assertEquals(changed - 1, len(evts._events["changed"]))
        self.assertEquals(no_more - 1, len(evts._events["no-more-entries"]))
        
        self.buff.search_text = "foo"
        self.assertEquals("bar", entry.get_text())

        self.bar.set_buffer(None)
        # The number of event listeners should not be affected
        self.assertEquals(changed - 1, len(evts._events["changed"]))
        self.assertEquals(no_more - 1, len(evts._events["no-more-entries"]))
        self.buff.search_text = "foo1a"
        self.assertEquals("bar", entry.get_text())
        
    
    def test_buttons_sensitivity(self):
        bar = self.bar
        w = bar.widget
        bw = util.find_child_widget(w, "backward")
        entry = util.find_child_widget(w, "entry")
        fw = util.find_child_widget(w, "forward")
        # Check if the text entry test changing affects the buffer
        self.assertEquals("", entry.get_text())
        assert not fw.get_property("sensitive")
        assert not bw.get_property("sensitive")

        entry.set_text("foo")
        assert fw.get_property("sensitive")
        
        self.buff.search_text = "bar"
        self.assertEquals("bar", entry.get_text())
        assert self.view.forward is None
        self.buff.set_text(" a b a")
        fw.clicked()
        assert self.view.forward
        self.assertEquals(0, len(self.buff.get_selection_bounds()))
        self.view.forward = None
        
        entry.set_text("a")
        self.assertEquals("a", self.buff.search_text)
        assert self.view.forward is None
        bw.clicked()
        assert not self.view.forward
        self.view.forward = None
        fw.clicked()
        assert self.view.forward

    def test_visibility(self):
        view = MockTextView()
        bar = SearchBar(view, self.ag)
        buff = CulebraBuffer()
        bar.set_buffer(buff)
        w = bar.widget
        
        ft = self.ag.get_action(ACTION_FIND_TOGGLE)
        assert not ft.get_active()
        assert not w.get_property("visible")
        
        ft.set_active(True)

        assert ft.get_active()
        assert w.get_property("visible")

        w.hide()
        assert not w.get_property("visible")
        assert not ft.get_active()


    def test_show_selected_text(self):
        """When the search bar is shown and some text is selected it should
        show it on the entry and reflect it on the buffer.search_text"""
    
    def test_activate_entry(self):
        """When the text entry is activated the find next action should be
        activated."""
    
    def test_highlight_off(self):
        """When the action is unactive (or the widget is hidden) then the
        highlight should be turned off."""
    
    def test_focus(self):
        """When the text entry is selected its text should be selected."""
    
    def test_action_group_change(self):
        """When the action group is changed activating the old ones should not
        affect this search bar (and the other way around)."""
    
    def test_no_more_entries(self):
        """When there are no more entries the carret should be moved to the top
        and select the next entry, only if there is one next entry to select.
        Searching forward should move the carret to the top, and vice-versa."""
    
    def test_no_more_entries_sensitive(self):
        """When there are no search matches the search next/back buttons should
        be insensitive whilst the searchbar is focused."""
    
    def test_cycle(self):
        """When the carret is after the last selected item the carret should go
        to the first element on the buffer, instead of not doing it.
        When it's not cycling it should select the last element."""
        
# XXX: there should be a way of automating the tasks, like pushing/poping
# XXX: actions. For example: push 'move carret to top', if not 'find next', pop,
# XXX: else leave it there.

if __name__ == '__main__':
    unittest.main()