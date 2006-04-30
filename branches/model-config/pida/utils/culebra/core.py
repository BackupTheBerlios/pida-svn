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

    @classmethod
    def factory(cls):
        return BaseServiceFactory(cls)
        
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

