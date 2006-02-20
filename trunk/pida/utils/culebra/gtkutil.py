__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

# Most of this code is redudant because it's also present on 'rat' module.
import weakref

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
        


class SignalHolder:
    def __init__(self, obj, signal, cb, use_weakref=True, *args, **kwargs):
        try:
            args = kwargs["userdata"],
        except KeyError:
            args = ()

        self.source = obj.connect(signal, cb, *args)

        if use_weakref:
            self.obj = weakref.ref(obj)
        else:
            self.obj = lambda: obj
    
    def __del__(self):
        self.obj().disconnect(self.source)


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
