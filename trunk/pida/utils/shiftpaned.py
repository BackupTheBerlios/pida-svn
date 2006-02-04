__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__copyright__ = "Copyright 2006, Tiago Cogumbreiro"

import gtk

(
SHOW_LEFT,
SHOW_RIGHT,
SHOW_BOTH,
) = range(3)

def _remove_all(widget):
    map(widget.remove, widget.get_children())

# TODO: implement remove_{right,left}_widget
class ShiftPaned(gtk.VBox):
    """
    A ShiftPaned is a gtk.Paned that can hide one of its child widgets,
    therefore hiding the pane division.
    
    """
    _state = SHOW_BOTH
    _left_args = ()
    _left_kwargs = {}
    _right_args = ()
    _right_kwargs = {}
    left_widget = None
    right_widget = None
    
    def has_both_widgets(self):
        return self.right_widget is not None and self.left_widget is not None
    
    def __init__(self, paned_factory=gtk.HPaned):
        self.paned = paned_factory()
        self.paned.show()
        super(ShiftPaned, self).__init__()
    
    def update_children(self):
        if self.has_both_widgets():
            _remove_all(self)
            _remove_all(self.paned)
            if self._state == SHOW_BOTH:
                self.add(self.paned)
                self.paned.pack1(
                    self.left_widget,
                    *self._left_args,
                    **self._left_kwargs
                )
                
                self.paned.pack2(
                    self.right_widget,
                    *self._right_args,
                    **self._right_kwargs
                )
            elif self._state == SHOW_LEFT:
                self.add(self.left_widget)
            elif self._state == SHOW_RIGHT:
                self.add(self.right_widget)
                
        elif len(self.get_children()) >= 1:
            self.remove(self.get_children()[0])
    
    def pack1(self, widget, *args, **kwargs):
        assert widget is not None
        self._left_args = args
        self._left_kwargs = kwargs
        self.left_widget = widget
        self.update_children()
    
    def pack2(self, widget, *args, **kwargs):
        assert widget is not None
        self._right_args = args
        self._right_kwargs = kwargs
        self.right_widget = widget
        self.update_children()
        
    def set_state(self, state):
        if state == self._state:
            return
        self._state = state
        self.update_children()

    def get_state(self):
        return self._state

    def set_position(self, position):
        self.paned.set_position(position)
    
    def get_position(self):
        return self.paned.get_position()



if __name__ == '__main__':
    #p = ShiftPaned(gtk.VPaned)
    p = ShiftPaned(gtk.HPaned)
    btn1 = gtk.Button("Show right only")
    btn2 = gtk.Button("Show left only")
    p.pack1(btn1)
    p.pack2(btn2)
    def on_click(btn):
        p.set_state(SHOW_RIGHT)
    btn1.connect("clicked", on_click)
    def on_click(btn):
        p.set_state(SHOW_LEFT)
    btn2.connect("clicked", on_click)
    btn1.show()
    btn2.show()
    w = gtk.Window()
    w.add(p)
    w.show_all()
    w.connect("delete-event", gtk.main_quit)
    gtk.main()


