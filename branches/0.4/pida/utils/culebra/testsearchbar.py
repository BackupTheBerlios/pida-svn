import unittest
from guitest import gtktest
from searchbar import SearchBar
from common import ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD, ACTION_FIND_TOGGLE
from rat import util
#from buffers import CulebraBuffer
import edit
import gtk
from bar import VisibilitySync
import weakref
import interfaces
import core
## XXX: there must be a generic test with mock services

class MockTextView:
    forward = None
    buffer = None
    
    def find(self, forward=True):
        self.forward = forward
    
    def get_buffer(self):
        return self.buffer
    
    
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


def get_selected_text(entry):
    start = entry.get_property("selection-bound")
    end = entry.get_property("cursor-position")
    return entry.get_text()[start:end]


class GtkTestCase(gtktest.GtkTestCase):
    def tearDown(self):
        pass

class TestSearchBar(GtkTestCase):
    
    def createAg(self):
        ag = gtk.ActionGroup("a")
        for name in (ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD):
            ag.add_action(gtk.Action(name, None, None, "gtk-open"))
        ag.add_action(gtk.ToggleAction(ACTION_FIND_TOGGLE, None, None, "gtk-open"))
        return ag
        
    
    def setUp(self):
        self.ag = self.createAg()
        self.act_fw = self.ag.get_action(ACTION_FIND_FORWARD)
        self.act_bw = self.ag.get_action(ACTION_FIND_BACKWARD)

        self.provider = provider = core.ServiceProvider()
        edit.register_services(provider)
        
        self.highlight = provider.get_service(interfaces.IHighlightSearch)
        self.search = provider.get_service(interfaces.ISearch)
#        self.view = MockTextView()
#        self.view.buffer = self.buff
        provider.register_factory(interfaces.ISearchBar, SearchBar)
        self.bar = provider.get_service(interfaces.ISearchBar)
        self.bar.set_action_group(self.ag)
        
        self.w = self.bar.widget
        self.entry = self.bar.entry#util.find_child_widget(self.w, "entry")
        self.bw = util.find_child_widget(self.w, "backward")
        self.fw = util.find_child_widget(self.w, "forward")
        assert self.entry is not None

    def test_widgets(self):
        
        bar = self.bar
        w = bar.widget
        lbl = util.find_child_widget(w, "label")
        assert lbl is not None
        assert lbl.get_property("visible")
        
        assert self.entry is not None
        assert self.entry.get_property("visible")

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
        self.assertEquals("", self.search.get_text())
        
        entry.set_text("foo")
        self.assertEquals("foo", self.search.get_text())
    
        self.search.set_text("bar")
        self.assertEquals("bar", entry.get_text())
        
        # Check if the event listeners' decrease
        # TODO: test the events
        '''
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
        '''
    
    def test_buttons_clicked(self):
        """Clicking buttons"""
        entry = self.entry
        fw = self.fw
        bw = self.bw
        act_fw = self.act_fw
        act_bw = self.act_bw
        
        
        self.search.set_text("bar")
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
    
    def assertAreSensitive(self):
        assert self.fw.get_property("sensitive")
        assert self.bw.get_property("sensitive")

    def assertAreNotSensitive(self):
        assert not self.fw.get_property("sensitive")
        assert not self.bw.get_property("sensitive")
        
    def test_sensitivity(self):
        """Button sensitivity"""
        # Check if the text entry test changing affects the buffer
        
        # Test 1: default action group
        self.entry.set_text("")
        self.assertAreNotSensitive()
        self.entry.set_text("foo")
        self.assertAreSensitive()
        
        # Test 2: Removing the action group makes no difference
        self.bar.set_action_group(None)
        
        self.entry.set_text("")
        self.assertAreNotSensitive()
        self.entry.set_text("foo")
        self.assertAreSensitive()
        
        # Test 3: Using a new action group makes no difference
        self.bar.set_action_group(self.createAg())

        self.entry.set_text("")
        self.assertAreNotSensitive()
        self.entry.set_text("foo")
        self.assertAreSensitive()


# TODO: need to test visibility
    '''
    def test_visibility(self):
        view = MockTextView()
        provider = core.ServiceProvider()
        provider.register_service(interfaces.ISearch, None)
        bar = SearchBar(view, self.ag, provider)
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
'''

    def test_show_selected_text(self):
        """When the search bar is shown and some text is selected it should
        show it on the entry and reflect it on the buffer.search_text"""
        buff = self.provider.get_service(interfaces.IBuffer)
        buff.set_text("123")
        buff.select_all()
        
        bar = self.bar
        w = bar.widget
        
        # Select all
        self.assertEquals(self.entry.get_text(), "")
        w.show()
        self.assertEquals(self.entry.get_text(), "123")

        # Select a few chars
        iter = self.buff.get_start_iter().copy()
        iter.forward_chars(1)
        self.buff.select_range(self.buff.get_start_iter(), iter)
        txt = self.buff.get_text(*self.buff.get_selection_bounds())
        self.assertEquals("1", txt)
        self.entry.set_text("")
        
        w.hide()
        w.show()
        self.assertEquals(self.entry.get_text(), "1")
        w.hide()
        
        # Now we select nothing and the search text should be maintained
        self.buff.place_cursor(self.buff.get_start_iter())
        self.assertEquals(self.entry.get_text(), "1")
        
    
    def test_activate_entry(self):
        """When the text entry is activated the find next action should be
        activated."""
        self.view.forward = None
        self.entry.emit("activate")
        assert self.view.forward is None
        
        self.entry.set_text("foo")
        self.entry.emit("activate")
        assert self.view.forward
    

    def assertHighlight(self):
        assert self.highlight.get_highlight()
    
    def notAssertHighlight(self):
        assert not self.highlight.get_highlight()
        
    def test_highlight_off(self):
        """Highlight"""
        # When the action is unactive (or the widget is hidden) then the
        # highlight should be turned off.
        self.notAssertHighlight()
        self.w.show()
        self.assertHighlight()
        self.w.hide()
        self.notAssertHighlight()
        self.highlight.set_highlight(True)
        self.w.show()
        self.assertHighlight()
        
        self.highlight.set_highlight(False)
        self.notAssertHighlight()
        self.w.hide()
        self.notAssertHighlight()
    
    def test_focus(self):
        """When the text entry is selected its text should be selected."""
        # XXX: calling grab_focus does not give *real* focus to the widget
        return
        
        entry = self.entry
        entry.set_text("12345")
        entry.select_region(1,-1)
        self.assertEquals("2345", get_selected_text(entry))
        
        # When we show the object it should focus the entry
        self.w.show()

        entry = self.entry
        self.assertEquals("12345", get_selected_text(entry))
        assert entry.props.is_focus
        gtk.main_quit()

        lbl = util.find_child_widget(self.w, "label")
        lbl.grab_focus()
        assert lbl.props.is_focus
        assert not entry.props.is_focus
        
        # Deselect the text
        self.w.hide()
        entry.select_region(0, 0)
        self.assertEquals("", get_selected_text(entry))
        
        # Now show it again, the text should be selected again
        self.w.show()
        assert entry.props.is_focus
        self.assertEquals("12345", get_selected_text(entry))
        
    
    def test_action_group(self):
        """Buttons from the search bar should be connected to the action
        group elements"""

        
        act_fw = self.ag.get_action(ACTION_FIND_FORWARD)
        act_bw = self.ag.get_action(ACTION_FIND_BACKWARD)
        
        assert self.fw in act_fw.get_proxies()
        assert self.bw in act_bw.get_proxies()
        
    
    def test_action_group_change(self):
        """When the action group is changed activating the old ones should not
        affect this search bar (and the other way around)."""

        fw = util.find_child_widget(self.w, "forward")
        bw = util.find_child_widget(self.w, "backward")
        
        act_fw = self.ag.get_action(ACTION_FIND_FORWARD)
        act_bw = self.ag.get_action(ACTION_FIND_BACKWARD)
        
        assert self.bar.find_forward is act_fw
        assert self.bar.find_backward is act_bw
        assert fw in act_fw.get_proxies()
        assert bw in act_bw.get_proxies()
        
        self.bar.set_action_group(None)
        
        assert fw not in act_fw.get_proxies()
        assert bw not in act_bw.get_proxies()
        
        assert self.bar.find_forward is None
        assert self.bar.find_backward is None
        assert self.bar.find_forward_source is None
        assert self.bar.find_backward_source is None
        
        ag = self.createAg()
        self.bar.set_action_group(ag)
        act_fw = ag.get_action(ACTION_FIND_FORWARD)
        act_bw = ag.get_action(ACTION_FIND_BACKWARD)
        assert fw in act_fw.get_proxies()
        assert bw in act_bw.get_proxies()
        
        # TODO: test more stuff here
    
    ## TODO: test life cycle
    '''
    def test_life_cycle(self):
        view = MockTextView()
        provider = core.ServiceProvider()
        sb = SearchBar(view, None, provider)
        ref = weakref.ref(sb)
        sb.destroy()
        sb = None
        assert ref() is None
    '''
    
    def test_no_more_entries(self):
        """When there are no more entries the carret should be moved to the top
        and select the next entry, only if there is one next entry to select.
        Searching forward should move the carret to the top, and vice-versa."""
        # XXX: how to test this?
    
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