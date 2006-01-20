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

# gtk import(s)
import gtk

# pida core import(s)
import base

import string

(
TYPE_RADIO,
TYPE_TOGGLE,
TYPE_NORMAL
) = range(3)

def decorate_action(meth, **kwargs):
    for key, val in kwargs.iteritems():
        setattr(meth, key, val)

def action(**kwargs):
    '''This is a python decorator to add metadata to your action methods.
    Its usage is very simple::
    
        class MyService(service.service):
            
            # A simple gtk.Action
            @action(stock_id=gtk.STOCK_GO_FORWARD, label="My Action")
            def act_my_action(self, action):
                """The tooltip text"""
                print "i'm on the activate callback"
            
            # A gtk.ToggleAction
            @action(stock_id=gtk.STOCK_GO_BACK, label="My Toggle Action",
                    type=TYPE_TOGGLE)
            def act_my_toggle_action(self, action):
                """Tooltip text for a toggle action"""
                print "i'm the activate callback"
            
            
            # A gtk.RadioAction. The 'group' argument is optional.
            @action(stock_id=gtk.STOCK_GO_DOWN, label="Second Radio Action",
                    value="bar", type="radio")
            def act_foo_bar(self, action):
                """This is the first element of the group"""
                print "I'm the activate callback" 

            # In this case the 'my_radio_action' is connected to 'foo_bar'
            # action.
            @action(stock_id=gtk.STOCK_GO_UP, label="My Radio Action",
                    value="foo", group="foo_bar", type=TYPE_RADIO)
            def act_my_radio_action(self, action):
                """Tooltip text for a radio action"""
                print "I'm the activate callback"
                
            # You can even change the action name
            @action(name="ACoolName", type=TYPE_RADIO, value=0)
            def act_this_name_is_ignored(self, action):
                pass
            
            # But when you refer to it you use the full name:
            @action(type=TYPE_RADIO, group="ACoolName", value=1)
            def act_something_cool(self, action):
                pass
    '''
    def wrapper(meth):
        for key, val in kwargs.iteritems():
            setattr(meth, key, val)
        return meth
    return wrapper

class action_handler(base.pidacomponent):

    type_name = 'action-handler'
    __actions = {
        TYPE_NORMAL: gtk.Action,
        TYPE_TOGGLE: gtk.ToggleAction,
        TYPE_RADIO: gtk.RadioAction
    }

    def __init__(self, service):
        self.__service = service
        self.__init_actiongroup()
        self.init()

    def init(self):
        pass

    def __init_actiongroup(self):
        agname = "%s+%s" % (self.__service.NAME, self.type_name)
        self.__action_group = gtk.ActionGroup(agname)
        radio_elements = {}
        
        for attr in dir(self):
            if not attr.startswith("act_"):
                continue
                
            meth = getattr(self, attr)
            
            name = attr[4:]
            actname = "%s+%s" % (agname, name)
            actname = getattr(meth, "name", actname)
            
            name = getattr(meth, "name", name)
            words = map(string.capitalize, name.split('_'))
            label = " ".join(words)
            label = getattr(meth, "label", label)
            stock_id = "gtk-%s%s" % (words[0][0].lower(), words[0][1:])
            stock_id = getattr(meth, "stock_id", stock_id)
            doc = meth.func_doc
            
            action_type = getattr(meth, "type", TYPE_NORMAL)
            action_factory = self.__actions[action_type]
            
            args = ()
            # gtk.RadioAction has one more argument in the constructor
            if action_type == TYPE_RADIO:
                args = [getattr(meth, "value")]
            
            action = action_factory(actname, label, doc, stock_id, *args)

            # gtk.RadioAction has an important property that needs to be set
            if action_type == TYPE_RADIO:
                radio_elements[name] = (action, getattr(meth, "group", None))
            
            action.set_property("is-important", getattr(meth, "is_important", False))
                
            action.connect("activate", meth)
            self.__action_group.add_action(action)
        
        # Now we create the radio groups
        for name, (action, group) in radio_elements.iteritems():
            if group is not None:
                group = radio_elements[group][0]
                
            action.set_group(group)
        

    def get_action_group(self):
        return self.__action_group
    action_group = property(get_action_group)

    def get_service(self):
        return self.__service
    service = property(get_service)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                """
