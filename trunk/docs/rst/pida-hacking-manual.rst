===============
The PIDA's Hacking Manual
===============

:author: Tiago Cogumbreiro
:contact: cogumbreiro@users.sf.net

.. contents:: Table Of Contents


Creating gtk.Action's
=====================

First you need to know that there's a gtk.Action group associated with
each service. It's name is the 'classname'.
It can be accessed through 'self.action_group'.

The Hard Way
____________

In order to add actions to the service's action group you just need
to add them in the 'init()' method which is called to initialized the
service.

Example::

  import pida.core.service as service
  import gtk

  class MyService(service.service):
      def init(self):
          self.action_group.add_actions([
              ("GoForward",gtk.STOCK_GO_FORWARD, None,
               "This makes it go forward"),
          ])
          
          act = self.action_group.get_action("GoForward")
          act.connect("activate", self.on_go_forward)
      
      def on_go_forward(self, action):
          print "Go forward!"


The Fast Way
_____________


Another way of creating actions is the *implicit creation*. Pida has a nice
feature that turns every method you prefix with a 'act_' into a 'gtk.Action' and
then the action name.

The action name is generated with the 'module+servicename+action_name', where
'action_name' is the method name ignoring the 'act_' part. The tooltip text is
generated from the doc string of the method.

So, a simillar example would be::


  import pida.core.service as service

  class MyService(service.service):
      def act_go_forward(self, action):
          """This makes it go forward"""
          print "Go forward!"

As you can see the code is way smaller but it has the following limitations:
 
 * implicitly connects to the 'activate' signal
 * the stock icon is fetched from the first word (separated by '_'), so in the
   case of gtk.STOCK_GO_FORWARD there's a no go.
 * it can only create gtk.Action's, not gtk.ToggleAction's nor
   gtk.RadioAction's.


Integrating into menu and toolbar
=================================

In order to put your gtk.Action's in toolbar and menus you have to
have a concept of gtk.UIManager. You have 5 available placeholders to put your
actions for your toolbar:
 
 * 'OpenFileToolbar'
 * 'SaveFileToolbar'
 * 'EditToolbar'
 * 'ProjectToolbar'
 * 'VcToolbar' 
 * 'ToolsToolbar'

And 4 available placeholders for your menu entries:
 * 'OpenFileMenu'
 * 'SaveFileMenu'
 * 'ExtrasFileMenu'
 * 'GlobalFileMenu'

This is also the order of which they were created.

The next part is that you need to
return a UIManager definition with the following nature: implement a method
named 'get_menu_definition' in your service class::

  import pida.core.service as service

  class MyService(service.service):
  
      def get_menu_definition(self):
          return """
              <menubar>
                  <placeholder name="ExtrasFileMenu">
                      <menu name="my_menu_entry" action="MyAction">
                  </placeholder>
              </menubar>
              <toolbar>
                  <placeholder name="ToolsToolbar">
                      <toolitem name="my_tool_item" action="MyAction" />
                  </placeholder>
              </toolbar>
          """

In this example we've plugged our action 'MyAction' to the menu and the toolbar.

