from core import *
import unittest
import weakref
import gc

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
        prov.register_factory(one_srv, "one", base_service=False)
        prov.register_factory(two_srv, "two", base_service=False)
        
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
        prov.register_factory(lambda service_provider: "one", "service1", "service2", "service3", base_service=False)
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
        except ServiceNotFoundError:
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

if __name__ == '__main__':
    unittest.main()
