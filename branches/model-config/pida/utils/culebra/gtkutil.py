__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

# Most of this code is redudant because it's also present on 'rat' module.
import weakref
import gobject
import gtk

def hide_on_delete(window):
    """
    Makes a window hide it self instead of getting destroyed.
    """
    
    def on_delete(wnd, *args):
        wnd.hide()
        return True
        
    return window.connect("delete-event", on_delete)


class _GetterMemoize:
    # XXX: must implement this per child
    def __init__(self, func):
        self.func = func
        self.vals = {}
        
    def __call__(self, obj):
        try:
            return self.val
        except AttributeError:
            self.val = self.func(obj)
            return self.val


def getter_memoize(func):
    name = func.__name__ + "_val"
    
    def wrapper(self):
        if not hasattr(self, name):
            setattr(self, name, func(self))

        return getattr(self, name, func(self))
    
    return wrapper
        

class _DestroyedListener:
    """
    This is a helper class that helps you not create a circular reference
    with the object you're listening too.
    """
    def __init__(self, holder):
        self.holder = weakref.ref(holder)
    
    def on_destroyed(self, gobj):
        # Remove the old reference
        self.holder().obj = lambda: None

class SignalHolder:
    """
    Simple usage::
    
        holder = SignalHolder(btn, "clicked", on_clicked)
        # while this reference lives the connection to the signal lives too
        holder = None
        # on_connect no longer recieves callbacks from 'btn'
        
        # You can also send user data, you need to use the 'userdata' keyword
        # argument
        holder = SignalHolder(btn, "clicked", on_clicked, userdata="bar")
        
    """
    def __init__(self, obj, signal, cb, use_weakref=True, destroy=True, *args, **kwargs):
        try:
            args = kwargs["userdata"],
        except KeyError:
            args = ()

        self.source = obj.connect(signal, cb, *args)

        if destroy and isinstance(obj, gtk.Object):
            self.listener = _DestroyedListener(self)
            self.destroy_source = obj.connect("destroy", self.listener.on_destroyed)

        if use_weakref:
            self.obj = weakref.ref(obj)
        else:
            self.obj = lambda: obj
    
    def __del__(self):
        obj = self.obj()
        if obj is None:
            return
            
        obj.disconnect(self.source)
        if hasattr(self, "destroy_source"):
            obj.disconnect(self.destroy_source)
        


def signal_holder(obj, signal, cb, use_weakref=True, **kwargs):
    if obj is None or cb is None:
        return
    return SignalHolder(obj, signal, cb, **kwargs)



class ProxySubscription:
    """This represents the `gtk.Action.connect_proxy`, 
    `gtk.Action.disconnect_proxy` subscription.
    
    When the object is created it will connect the widget as an action
    proxy.
    
    When no references to this object are left it will disconnect the widget
    from the action.
    """
    
    def __init__(self, action, widget, use_weakref=True):
        action.connect_proxy(widget)
        if use_weakref:
            self.action = weakref.ref(action)
            self.widget = weakref.ref(widget)
        else:
            self.action = lambda: action
            self.widget = lambda: widget
    
    def __del__(self):
        self.action().disconnect_proxy(self.widget())


def subscribe_proxy(action, widget, use_weakref=True):
    if action is None or widget is None:
        return

    return ProxySubscription(action, widget, use_weakref)
