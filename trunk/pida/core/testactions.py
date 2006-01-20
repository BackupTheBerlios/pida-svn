import actions
import unittest
import gtk

class Something:
    NAME="foo"

class MyHandler(actions.action_handler):
    def act_normal_action_1(self, action):
        pass
    
    def act_normal_action_2(self, action):
        """I have a tooltip"""

    def act_find_something(self, action):
        """Tooltip and gtk.STOCK_FIND"""
    
    @actions.action(name="another_name")
    def act_some_name(self, action):
        pass

    @actions.action(type=actions.TYPE_NORMAL)
    def act_normal_action_3(self, action):
        pass

    @actions.action(label="Label", is_important=True, type=actions.TYPE_TOGGLE)
    def act_normal_action_4(self, action):
        pass

    @actions.action(type=actions.TYPE_RADIO, value=0)
    def act_radio1(self, action):
        pass

    @actions.action(type=actions.TYPE_RADIO, value=1, group="radio1")
    def act_radio2(self, action):
        pass

    @actions.action(type=actions.TYPE_RADIO, value=0, name="Something")
    def act_radio3(self, action):
        pass

    @actions.action(type=actions.TYPE_RADIO, value=1, group="Something")
    def act_radio4(self, action):
        pass


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MyHandler(Something())
        self.actions = self.handler.action_group

    def get_action(self, name):
        return self.actions.get_action("foo+action-handler+%s" % name)

    def checkAction(self, name="", tooltip=None, stock_id="", action_type=gtk.Action, action=None, is_important=False, label=""):
        if action is None:
            action = self.get_action(name)
        assert action is not None
        self.assertEquals(type(action), action_type)
        self.assertEquals(tooltip, action.get_property("tooltip"))
        self.assertEquals(stock_id, action.get_property("stock-id"))
        self.assertEquals(is_important, action.get_property("is-important"))
        self.assertEquals(label, action.get_property("label"))

    def test_actions(self):
        self.assertEquals(10, len(self.actions.list_actions()))

    def test_action1(self):
        self.checkAction(
            name = "normal_action_1",
            tooltip = None,
            stock_id = "gtk-normal",
            label = "Normal Action 1",
        )
    
    def test_action2(self):
        self.checkAction(
            name = "normal_action_2",
            tooltip = "I have a tooltip",
            stock_id = "gtk-normal",
            label = "Normal Action 2",
        )

    def test_action3(self):
        self.checkAction(
            name = "find_something",
            tooltip = "Tooltip and gtk.STOCK_FIND",
            stock_id = gtk.STOCK_FIND,
            label = "Find Something",
        )

    def test_action4(self):
        self.checkAction(
            action = self.actions.get_action("another_name"),
            tooltip = None,
            stock_id = "gtk-another",
            label = "Another Name",
        )

    def test_action5(self):
        self.checkAction(
            name = "normal_action_3",
            tooltip = None,
            stock_id = "gtk-normal",
            label = "Normal Action 3",
        )

    def test_action6(self):
        self.checkAction(
            name = "normal_action_4",
            tooltip = None,
            stock_id = "gtk-normal",
            label = "Label",
            is_important = True,
            action_type = gtk.ToggleAction,
        )



if __name__ == '__main__':
    unittest.main()
