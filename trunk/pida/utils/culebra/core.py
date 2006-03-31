__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2006, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import weakref

class IService:
    def bind(self, service_provider):
        pass


class ServiceFactory:
    """Should return a service provider"""


class ServiceError(StandardError):
    pass

class DependencyError(StandardError):
    pass

class FactoryError(StandardError):
    pass

class Depends(object):
    """
    Besides 'Depends' acting like an object that holds the interface
    needed to lookup the object it also works as a descriptor
    and uses a weak reference in order to avoid circular references
    transparentely.
    """
    def __init__(self, key, optional=False):
        self.key = key
        self.optional = optional
        self.objs = weakref.WeakKeyDictionary()
    
    def __get__(self, obj, obj_type=None):
        try:
            # If the object does exist return the value in the callable
            # associated with the name
            attr_name = self.objs[obj]
            return getattr(obj, attr_name)()
        except KeyError:
            # If the object does not exist then return myself
            return self
            
    def set_name(self, obj, attr_name):
        """Associates a certain object with the attribute that holds the
        weakref.ref object."""
        self.objs[obj] = attr_name


class BaseService(object):

    def bind(self, service_provider):
        for key in dir(self):
            val = getattr(self, key)
            if isinstance(val, Depends):
                try:
                    service = service_provider.get_service(val.key)
                    func = weakref.ref(service)
                    
                except ServiceError:
                    if not val.optional:
                        raise DependencyError(val.key)
                    func = lambda: None
                    
                attr_name = "_w_%s" % key
                val.set_name(self, attr_name)
                setattr(self, attr_name, func)
                
        self._bind(service_provider)
        
    def _bind(self, service_provider):
        """This method is called after the bind() method is, it's a good
        constructor method."""

class BaseServiceFactory:
    def __init__(self, factory):
        self.factory = factory
        
    def __call__(self, service_provider):
        service = self.factory()
        service.bind(service_provider)
        return service
    
    def __repr__(self):
        return repr(self.factory)

class MultiFactory:
    def __init__(self, factory, keys):
        self.factory = factory
        self.keys = keys
    
    def __call__(self, service_provider):
        service = self.factory(service_provider)
        for key in self.keys:
            service_provider.services[key] = service
        return service

class ServiceProvider:
    """A service provider makes it possible for factory generated objects,
    which we'll address as 'services', can be associated through keys.
    When you request a service from a certain key it will call a factory to
    create it.
    
    You can unregister services at any time and the factories will create them
    again when they are requested.
    
    You can also register services directly, overriding the ones generated
    from a factory. If that service overrides a key that has a service factory
    associated with it and that factory is registred on more factories then
    the service will override those keys too. The same thing happens when you
    unregister a service that is controlled by a service that has more then
    one key associated with it.
    
    You have two ways of registring factories, through `register_factory` and
    through `simple_factory`, the first is used to register classes based on
    `BaseService` whilst the second is used to register more generic factories
    . Generic factories are callable objects which accept one argument, the
    service provider, they *must* return the object they are supposed to
    create.
    
    You can access the services alive through the `services` variable.
    
    You can access the factories alive through the `factories` variable.
    """
    
    def __init__(self):
        self.factories = {}
        self.services = {}
        
        self.features = FeaturePool()
        # now we need something like a pool of registred object
        
        
    ## TODO: factories that are called with one argument and return the service in question
    
    def _register_factory(self, factory, keys):
        """Registers a certain key with a factory"""
        # First check for validation
        for key in keys:
            try:
                dummy = self.factories[key]
                raise FactoryError(key)
            except KeyError:
                pass

        if len(keys) > 1:
            factory = MultiFactory(factory, list(keys))
        
        for key in keys:
            self.factories[key] = factory

    # TODO: remove this methods
    def register_factory(self, factory, *keys):
        self._register_factory(BaseServiceFactory(factory), keys)
    
    def register_simple_factory(self, factory, *keys):
        self._register_factory(factory, keys)

    
    def unregister_factory(self, key):
        """Unregisters the factory"""
        try:
            factory = self.factories[key]
            keys = getattr(factory, "keys", [key])
            keys.remove(key)
            del self.factories[key]

        except KeyError:
            raise FactoryError(key)

    def register_service(self, service, *keys):
        """Register this service with the given keys."""
        # Get all keys that are present in factories as well
        all_keys = list(keys)
        for key in keys:
            try:
                all_keys.extend(getattr(self.factories[key], "keys", ()))
            except KeyError:
                pass
        
        for key in all_keys:
            self.services[key] = service
        
    def unregister_service(self, key):
        """Removes a service. If the service has a factory associated with
        it then it will be created again when needed."""
        
        # First get all the related keys
        try:
            factory = self.factories[key]
            keys = getattr(factory, "keys", (key,))
        except KeyError:
            keys = (key,)
        
        # Now try to delete the services
        try:
            for key in keys:
                del self.services[key]
            
        except KeyError:
            raise ServiceError(key)

    def get_service(self, interface):
        """Returns the service associated with a certain interface"""
        try:
            service = self.services[interface]
            
        except KeyError:
            try:
                factory = self.factories[interface]
                service = factory(self)
                self.services[interface] = service
                        
            except KeyError:
                raise ServiceError(interface)
                
        return service
    
    def destroy_services(self):
        """
        Removes all the services associated created thus far.
        Since we still hold the factories we can create them aftwerwards
        when the user calls `get_service()`.
        """
        
        self.services.clear()

######################################################################        

class FeaturePool:

    def __init__(self):
        self.features = {}
    
    def __getitem__(self, key):
        return self.features.get(key, ())
    
    def register_feature(self, feature, plugin):
        try:
            feats = self.features[feature]
        except KeyError:
            feats = set()
            self.features[feature] = feats
            
        return feats.add(plugin)
    
    def remove(self, feature, plugin):
        try:
            return self.features[feature].remove(plugin)
        except KeyError:
            pass

class PluginIterator:
    def __init__(self, registry, real_iter):
        self.registry = registry
        self.real_iter = real_iter
    
    def next(self):
        return self.real_iter.next().get_service(self.registry)
    
    def __iter__(self):
        return self
    
    def __repr__(self):
        return repr(self.real_iter)
        
class Plugin:
    def __init__(self, **kwargs):
        try:
            self.keys = list(kwargs.get("keys", ()))
            self.features = list(kwargs.get("features", ()))
            try:
                self.factory = kwargs["factory"]
            except KeyError:
                self.service = kwargs["service"]
                
        except KeyError:
            raise TypeError("__init__() accepts one obligatory argument, either 'factory' or 'service'")
            
    def get_service(self, registry):
        try:
            return self.service
        except AttributeError:
            self.service = self.factory(registry)
            return self.service

    def reset(self):
        del self.service

    def __repr__(self):
        return "<Plugin %r %r>" % (self.keys, self.features)

    def unplug(self):
        """This method is called when the service is removed from the registry"""

class PluginRegistry:
    def __init__(self, plugin_factory=Plugin):
        self.services = {}
        self.features = FeaturePool()
        self.plugins = set()
        self.plugin_factory = plugin_factory
    
    def register(self, plugin):
        for key in plugin.keys:
            try:
                val = self.services[key]
                raise ServiceError(key)
            except KeyError:
                pass
    
        self.plugins.add(plugin)
        
        for key in plugin.keys:
            self.services[key] = plugin
            
        for feat in plugin.features:
            self.features.register_feature(feat, plugin)
        return plugin
    
    def unregister(self, plugin):
        for key in plugin.keys:
            del self.services[key]
            
        for feat in plugin.features:
            self.features[feat].remove(plugin)
            
        self.plugins.remove(plugin)
        plugin.unplug()
    
    def register_plugin(self, *args, **kwargs):
        return self.register(self.plugin_factory(*args, **kwargs))

    def get_features(self, feature):
        return PluginIterator(self, iter(self.features[feature]))
    
    def get_service(self, key):
        try:
            return self.services[key].get_service(self)
        except KeyError:
            raise ServiceError(key)
    
    def _check_plugin(self, plugin):
        if len(plugin.features) == 0 and len(plugin.keys) == 0:
            self.unregister(plugin)
    
    def unregister_service(self, key):
        try:
            plugin = self.services.pop(key)
            plugin.keys.remove(key)
            self._check_plugin(plugin)

        except KeyError:
            raise ServiceError(key)
    
    def unregister_feature(self, feature, plugin):
        self.features.remove(feature, plugin)
        plugin.features.remove(feature)
        self._check_plugin(plugin)


###########################################################
# Component framework: ATTENTION UNTESTED AND UGLY
class ComponentPlugin(Plugin):
    def __init__(self, component_factory):
        self.keys = component_factory.get_interfaces()
        self.features = component_factory.get_features()
        self.factory = component_factory

    def unplug(self):
        try:
            self.service.unload()
        except AttributeError:
            pass
            
class AggregationPoint(object):
    def __init__(self, feature):
        self.feature = feature
        
    def __get__(self, obj, obj_type=None):
        return obj.registry.get_features(feature)

class Dependency(object):
    def __init__(self, interface):
        self.interface = interface
    
    def __get__(self, obj, obj_type=None):
        return getattr(obj, self.attr_name)()

class MetaComponent(type):
    def __init__(cls, name, bases, vals):
        cls._services = []
        for key, val in vals.iteritems():
            if issubclass(val, Service):
                val.attr_name = "_%s" % name
                val.name = name

class IComponent:
    
    def unload():
        """Called when the service is terminated"""

class Component(object):
    __meta__ = MetaComponent
    __implements__ = IComponent,
    
    def __init__(self, registry):
        self._registry = weakref.ref(registry)
        self._cascade = set()
    
    registry = property(lambda self: self._registry())
    
    def load(self):
        for dependency in self._dependencies:
            service = self.registry.get_service(dependency.interface)
            service._cascade.add(weakref.ref(self))
            setattr("_%s", weakref.ref(service))
    
    def unload(self):
        for service in self._cascade:
            service.registry_keys
            