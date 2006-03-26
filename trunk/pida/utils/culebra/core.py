__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2006, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import weakref

class IService:
    def bind(self, service_provider):
        pass


class ServiceFactory:
    """Should return a service provider"""


class ServiceNotFoundError(StandardError):
    pass

class DependencyError(StandardError):
    pass

class FactoryPresentError(StandardError):
    pass

class FactoryNotPresentError(StandardError):
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
                    
                except ServiceNotFoundError:
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
    def __init__(self):
        self.factories = {}
        self.services = {}
    ## TODO: factories that are called with one argument and return the service in question
    
    def register_factory(self, factory, *keys, **kwargs):
        """Registers a certain key with a factory"""
        base_service = kwargs.get("base_service", True)
        
        # First check for validation
        for key in keys:
            try:
                self.factories[key]
                raise FactoryPresentError(key)
            except KeyError:
                pass

        if base_service:
            factory = BaseServiceFactory(factory)
            
        if len(keys) > 1:
            factory = MultiFactory(factory, list(keys))
        
        for key in keys:
            self.factories[key] = factory

    
    def unregister_factory(self, key):
        """Unregisters the factory"""
        try:
            factory = self.factories[key]
            if isinstance(factory, MultiFactory):
                factory.keys.remove(key)
            del self.factories[key]
        except KeyError:
            raise FactoryNotPresentError(key)

    def register_service(self, service, *keys):

        for key in keys:
            self.services[key] = service

    def unregister_service(self, key):
        try:
            del self.services[key]
        except KeyError:
            raise ServiceNotFoundError

    def get_service(self, interface):
        """Returns the service associated with a certain interface"""
        try:
            service = self.services[interface]
            
        except KeyError:
            try:
                factory = self.factories[interface]
                
                service = factory(self)
                
                self.services[interface] = service
                
                # MultiFactories register a service in more then one keys
                if isinstance(factory, MultiFactory):
                    for key in factory.keys:
                        self.services[interface] = service
                        
            except KeyError:
                raise ServiceNotFoundError(interface)
                
        return service
    
    def destroy_services(self):
        """
        Removes all the services associated created thus far.
        Since we still hold the factories we can create them aftwerwards
        when the user calls `get_service()`.
        """
        
        self.services.clear()

