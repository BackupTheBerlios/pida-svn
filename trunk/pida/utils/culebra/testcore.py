from core import *
import unittest
import weakref

class Service2(BaseService):
    def do_something(self):
        return "something"

class Service1(BaseService):

    service2 = Depends("Service2")
    
    has_bind = False
    
    def bind(self, service_provider):
        super(Service1, self).bind(service_provider)
        self.has_bind = True

    def do_something_else(self):
        return self.service2.do_something() + " else"

class TestServiceProvider(unittest.TestCase):
    def setUp(self):
        self.provider = ServiceProvider()
        
    def test_services(self):
        provider = ServiceProvider()
        
        # Keys can be anything, even strings
        provider.register_factory(Service1, "service1")
        provider.register_factory(Service2, "Service2")
        
        s1 = provider.get_service("service1")
        assert s1.has_bind
        assert isinstance(s1.service2, Service2), s1.service2
        
        assert s1 is not None
        assert isinstance(s1, Service1)
        self.assertEquals(s1.do_something_else(), "something else")
        
        ghost = weakref.ref(s1)
        
        # Direct referencing works too
        s1 = None
        provider = None
        assert ghost() is None

    def test_simple_factory(self):
        prov = self.provider
        one_srv = lambda service_provider: "one"
        two_srv = lambda service_provider: "two"
        prov.register_simple_factory(one_srv, "one")
        prov.register_simple_factory(two_srv, "two")
        
        self.assertEquals(prov.get_service("one"), "one")
        self.assertEquals(prov.get_service("two"), "two")
    
    def test_multiple_factory_base(self):
        prov = self.provider
        prov.register_factory(Service2, "service1", "service2", "service3")
        assert prov.factories.has_key("service1")
        srv1 = prov.get_service("service1")
        assert isinstance(srv1, Service2), repr(srv1)
        srv2 = prov.get_service("service2")
        assert srv1 is srv2
        srv3 = prov.get_service("service3")
        assert srv3 is srv1
    
    def test_multiple_factory(self):
        prov = self.provider
        prov.register_simple_factory(
            lambda service_provider: "one",
            "service1",
            "service2",
            "service3",
        )
        assert prov.factories.has_key("service1")
        srv1 = prov.get_service("service1")
        self.assertEquals(srv1, "one")
        srv2 = prov.get_service("service2")
        assert srv1 is srv2
        srv3 = prov.get_service("service3")
        assert srv3 is srv1

    def test_multiple_service(self):
        prov = self.provider
        prov.register_service("one", "service1", "service2", "service3")
        srv1 = prov.get_service("service1")
        self.assertEquals(srv1, "one")
        srv2 = prov.get_service("service2")
        assert srv1 is srv2
        srv3 = prov.get_service("service3")
        assert srv3 is srv1

    def test_remove_service(self):
        prov = self.provider
        prov.register_factory(Service2, "service1")
        srv1 = prov.get_service("service1")
        srv2 = prov.get_service("service1")
        assert srv1 is srv2
        # When we unregister a service the other is created too
        prov.unregister_service("service1")
        srv2 = prov.get_service("service1")
        assert srv1 is not srv2

    def test_remove_service2(self):
        prov = self.provider
        prov.register_service("one", "service1")
        srv1 = prov.get_service("service1")
        srv2 = prov.get_service("service1")
        assert srv1 is srv2
        # When we unregister a service the other is created too
        prov.unregister_service("service1")
        try:
            srv2 = prov.get_service("service1")
            assert False
        except ServiceError:
            pass
        
    def test_remove_multiple_factories(self):
        prov = self.provider
        prov.register_factory(Service2, "service1", "service2", "service3")
        srv1 = prov.get_service("service1")
        prov.unregister_factory("service1")
        
        try:
            srv2 = prov.get_service("service1")
        except ServiceNotFoundError:
            pass
        
        try:
            srv2 = prov.get_service("service2")
        except ServiceNotFoundError:
            assert False
        
        assert srv2 is srv1
        
        # now 'Service2' factory instance is present on both 'service2'
        # and 'service3'
        prov.unregister_service("service2")
        try:
            prov.unregister_service("service3")
            # The service3 should already be vacant
            assert False
        except ServiceError:
            pass
            
        srv3 = prov.get_service("service3")
        new_srv2 = prov.get_service("service2")
        assert srv3 is new_srv2
        assert srv2 is not new_srv2
        
        # Try to change the order, everything should work the same
        try:
            prov.unregister_service("service2")
        except ServiceError:
            assert False
            
        srv2 = new_srv2
        new_srv2 = prov.get_service("service2")
        srv3 = prov.get_service("service3")
        assert srv3 is new_srv2
        assert srv2 is not new_srv2
        
    def test_propagation(self):
        prov = self.provider
        prov.register_factory(Service2, "service1", "service2", "service3")
        
        prov.register_service("foo", "service1")
        assert prov.get_service("service2") == "foo"
        assert prov.get_service("service3") == "foo"
        
if __name__ == '__main__':
    unittest.main()
