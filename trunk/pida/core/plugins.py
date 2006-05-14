"""A flexible plugin framework.

Clear your mind of any previously defined concept of a plugin.

Key components:

    * Registry: stores a set of plugins
    * Plugin: defines a set of behaviours
    * Registry key: unique behavioural identifier

Types of definable behaviour:

    1. Singleton
    2. Feature
    3. Extension Point/Extender

A plugin can register any number of the above behaviour
types.

1. Singleton

When a plugin registers as a singleton for a key, it is saying "I provide the
behaviour", so when the registry is looked up for that key, the object is
returned. At this point, please consider that an ideal registry key may be an
Interface definition (formal or otherwise), so when you ask for the behaviour
by interface you are actually returned an object implementing that interface.

2. Feature

When a plugin defines a Feature, it is again saying "I provide the behaviour",
the difference with singleton is that many plugins can define a feature, and
these plugins are aggregated and can be looked up by registry key. The look up
returns a list of objects that claim to provide the key.

3. Extension point

An extension point is identical to a feature except that the keys for it must
be predefined and are fixed. While a plugin may invent a feature and others
can join it, it is expected that whatever creates the registry formally
defines the extension points and they are then fixed. This can be used to
simulate the behaviour of traditional (Eclipse or Trac) extension points. The
plugin itself supplies the Extender (that which extends), while the registry
contains the Extension point itself (that which is to be extended).

Defining Plugins:

1. Singletons

a. First you will need a registry item:

    reg = Registry()

b. now define a behavioural interface:

    class IAmYellow(Interface):
        def get_shade():
            "get the shade of yellow"

c. now write a class that implements this behaviour:

    class Banana(object):
        def get_shade(self):
            return 'light and greeny'

d. create an instance of the plugin

    plugin = Banana()

e. register it with the registry:

    reg.register_plugin(
            instance=plugin,
            singletons=(IAmYellow,)
        )

f. get the item from the registry at a later time:

    plugin = reg.get_singleton(IAmYellow)
    print plugin.get_shade()

Things to note:

    * Attempting to register another plugin with a singleton of IAmYellow will
      fail.

    * Looking up a non-existent singleton will raise a SingletonError.


"""

import weakref

##############################################################################
## Core data types

class SetsDict:
    """
    The theory of the plugin architecture has its foundations
    on this simple structure which is a simple dictionary of sets.
    Each key contains a set associated with it and instead of setting
    the items you add them to a certain key.
    """
    def __getitem__(self, key):
        raise NotImplementedError
    
    def add(self, key, value):
        raise NotImplementedError
    
    def remove(self, key, value):
        raise NotImplementedError
        
    def keys(self):
        return self.data.keys()
    
    def __delitem__(self, key):
        del self.data[key]

    def __repr__(self):
        return repr(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

class StrictSetsDict(SetsDict):
    """
    A sets dictionary, where every value is a set of values.
    It is strict because in order to access a key you have to call
    `init_key` first otherwise `add`ing an item will result in
    a `KeyError`.
    """

    def __init__(self, keys=()):
        self.data = {}
        [self.init_key(key) for key in keys]
        

    def init_key(self, key):
        """pre-condition: key not in self.data"""
        val = self.data[key] = set()
        return val

    def __getitem__(self, key):
        return iter(self.data[key])

    def add(self, key, value):
        self.data[key].add(value)

    def remove(self, key, value):
        return self.data[key].remove(value)


class DynSetsDict(SetsDict):
    """
    A sets of dictionary that is dynamic. The difference between a strict
    one is that when there isn't a sets associated with a certain key
    it will be created.
    
    When you remove a value if the key associated with it does not
    exist you won't have a problem either.
    """
    
    default = ()
    
    def __init__(self):
        self.data = {}
        
    def __getitem__(self, key):
        return iter(self.data.get(key, self.default))
    
    def remove(self, key, value):
        try:
            return self.data[key].remove(value)
        except KeyError:
            pass
    
    def add(self, key, value):
        try:
            vals = self.data[key]
        except KeyError:
            vals = self.data[key] = set()
            
        vals.add(value)

    def __delitem__(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

##############################################################################
## Base classes

class PluginIterator:
    def __init__(self, registry, real_iter, *args, **kwargs):
        self.registry = registry
        self.real_iter = real_iter
        self.args = args
        self.kwargs = kwargs
    
    def next(self):
        plugin = self.real_iter.next()
        return plugin.get_instance(self.registry, *self.args, **self.kwargs)
    
    def __iter__(self):
        return self
    
    def __repr__(self):
        return repr(self.real_iter)

class Plugin:
    def __init__(self, instance=None, factory=None):
        if factory is not None and not callable(factory):
            raise TypeError("If you specify a factory it must be a callable object.", factory)
            
        if factory is None:
            self.instance = instance
        else:
            self.factory = factory
            
    def get_instance(self, registry):
        try:
            return self.instance
        except AttributeError:
            self.instance = self.factory(registry)
            return self.instance

    def reset(self):
        del self.service

    def unplug(self, registry):
        """This method is called when the service is removed from the registry"""

##############################################################################
## Implementations
class ExtensionPointError(StandardError):
    """Raised when there's an error of some sort"""
    
class ExtensionPoint:
    
    def __init__(self):
        self.lazy = DynSetsDict()
    
    def get_extender(self, extender):
        return extender
    
    def init(self, extension_points):
        self.data = StrictSetsDict(extension_points)
        
        for ext_pnt in self.lazy:
            try:
                for extender in self.lazy[ext_pnt]:
                    self.data.add(ext_pnt, self.get_extender(extender))
                
            except KeyError:
                pass
        del self.lazy
        
    def add(self, key, value):
        try:
            self.data.add(key, value)
        except AttributeError:
            self.lazy.add(key, value)

    def __getitem__(self, key):
        try:
            return self.data[key]
        except AttributeError:
            raise ExtensionPointError("Not initialized, run init() first")

    get_extension_point = __getitem__
    
    def has_init(self):
        return hasattr(self, "data")

    def keys(self):
        """
        Returns the available extension points. When it was not initialized
        a ExtensionPointError exception is raised.
        """
        
        try:
            return self.data.keys()
        except:
            raise ExtensionPointError("Not initialized, run init() first")
        

class PluginExtensionPoint(ExtensionPoint):
    def __init__(self, registry):
        self._registry = weakref.ref(registry)
        ExtensionPoint.__init__(self)
    
    def get_extender(self, extender):
        return extender.get_instance(self._registry())

class ExtensionPointManager:
    """
    An extension point manager is a DynSetsDict that can be transformed 
    into a StrictSetsDict. This means that before transforming it you
    can add elements at any key that they will be happily insterted
    however when the transformation takes turn all the elements will be
    added on the valid keys, the others will be silently discarded.
    
    This is usefull because the definition of the set (its keys) may
    only be known long after the object is needed - to aid the usage
    of lazy objects - and therefore the need for the transformation.
    
    To extended you can use a callable object 
    """

    def __init__(self, factory=ExtensionPoint):
        self.data = {}
        self.factory = factory

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            val = self.data[key] = self.factory()
            return val
    
    
    def __delitem__(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass
    
    def __repr__(self):
        return repr(self.data)

##############################################################################
## Use case of the classes defined above

class SingletonError(StandardError):
    """Raised when you there's a problem related to Singletons."""

class PluginEntry:
    def __init__(self, plugin, features, singletons, extension_points, extends):
        self.plugin = plugin
        self.features = list(features)
        self.singletons = list(singletons)
        self.extends = dict(extends)
        self.extension_points = list(extension_points)
    
    def get_instance(self, *args, **kwargs):
        return self.plugin.get_instance(*args, **kwargs)


class PluginFactoryCreator:
    """
    This is basically a factory of plugin factories.
    Instances of this class are the factories needed on `Registry.register`,
    where the only thing you change is the actual `Plugin` factory.
    
    This class is needed when you need to specify a class that extends from
    `Plugin`.
    """
    def __init__(self, plugin_factory):
        self.plugin_factory = plugin_factory

    def __call__(self, **kwargs):
        singletons = kwargs.pop("singletons", ())
        features = kwargs.pop("features", ())
        extends = kwargs.pop("extends", ())
        extension_points = kwargs.pop("extension_points", ())
            
        if len(singletons) == len(features) == 0:
            raise TypeError("You must specify at least one feature or one singleton key")
        plugin = self.plugin_factory(**kwargs)
        return plugin, features, singletons, extension_points, extends


# This is the default factory that uses the class Plugin
PluginFactory = PluginFactoryCreator(Plugin)


class Registry:
    def __init__(self, plugin_factory=PluginFactory):
        self.singletons = {}
        self.plugins = {}
        
        self.plugin_factory = plugin_factory
        factory = lambda: PluginExtensionPoint(self)
        
        self.ext_points = ExtensionPointManager(factory)
        self.features = DynSetsDict()
        
    
    def register(self, plugin, features, singletons, extension_points, extends):
        
        # Check for singletons conflicts
        # In this case we do not allow overriding an existing Singleton
        for key in singletons:
            try:
                val = self.singletons[key]
                raise SingletonError(key)
            except KeyError:
                pass
    
        for key in singletons:
            self.singletons[key] = plugin
        
        for feat in features:
            self.features.add(feat, plugin)
        
        for holder_id, points in extension_points:
            self.ext_points[holder_id].init(points)
        
        extension_points = [row[0] for row in extension_points]
        
        for holder_id, extension_point in extends:
            self.ext_points[holder_id].add(extension_point, plugin)
        
        
        self.plugins[plugin] = PluginEntry(plugin, features, singletons,
                                           extension_points, extends)
        
        return plugin
    
    def get_plugin_from_singleton(self, singleton):
        try:
            return self.singletons[singleton]
        except KeyError:
            raise SingletonError(singleton)
    
    def unregister(self, plugin):
        entry = self.plugins[plugin]
        
        for key in entry.singletons:
            del self.singletons[key]
            
        for feat in entry.features:
            self.features.remove(feat, plugin)
            
        for holder_id in entry.extension_points:
            del self.ext_points[holder_id]
        
        for holder_id, ext_pnt in entry.extends.iteritems():
            self.ext_points[holder_id].remove(ext_pnt, plugin)

        del self.plugins[plugin]
        
        plugin.unplug(self)
    
    def register_plugin(self, *args, **kwargs):
        return self.register(*self.plugin_factory(*args, **kwargs))

    def get_features(self, feature, *args, **kwargs):
        return PluginIterator(self, iter(self.features[feature]), *args, **kwargs)
    
    def get_singleton(self, singleton, *args, **kwargs):
        return self.get_plugin_from_singleton(singleton).get_instance(self, *args, **kwargs)
    
    def get_extension_point(self, holder_id, extension_point):
        return self.ext_points[holder_id].get_extension_point(extension_point)
    
    def get_extension_point_def(self, holder_id):
        return self.ext_points[holder_id].keys()
    
    def _check_plugin(self, plugin):
        entry = self.plugins[plugin]
        if len(entry.features) == 0 and len(entry.singletons) == 0:
            self.unregister(plugin)
    
    def unregister_singleton(self, singleton):
        try:
            plugin = self.singletons.pop(singleton)
            entry = self.plugins[plugin]
            entry.singletons.remove(singleton)
            self._check_plugin(plugin)

        except KeyError:
            raise SingletonError(singleton)
    
    def unregister_feature(self, feature, plugin):
        """
        In order to remove a feature u must have the associated plugin.
        """
        self.features.remove(feature, plugin)
        
        entry = self.plugins[plugin]
        entry.features.remove(feature)
        self._check_plugin(plugin)

    def __iter__(self):
        return iter(self.plugins)

    def clear(self):
        self.services = {}
        self.features.clear()
        for plugin in self.plugins:
            plugin.singeltons = []
            plugin.features = []
            plugin.unplug()
        self.plugins.clear()

