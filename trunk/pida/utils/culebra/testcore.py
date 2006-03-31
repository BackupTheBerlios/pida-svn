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

# Service discovery stuff
class TestPlugin(unittest.TestCase):
    def test_service(self):
        reg = PluginRegistry()
        reg.register_plugin(
            service="foo",
            keys=("key1", "key2", "key3"),
        )
        reg.register_plugin(
            service="bar",
            keys=("key4",)
        )
        assert reg.get_service("key1") == "foo"
        assert reg.get_service("key2") == "foo"
        assert reg.get_service("key3") == "foo"
        assert reg.get_service("key4") == "bar"
        try:
            reg.get_service("key5")
            assert False
        except ServiceError:
            pass

    def test_features(self):
        reg = PluginRegistry()
        reg.register_plugin(
            service="foo",
            features=("feat1", "feat2", "feat3")
        )
        reg.register_plugin(
            service="bar",
            features=("feat1", "feat3"),
        )
        reg.register_plugin(
            service="gin",
            features=("feat2", "feat3", "feat4"),
        )
        
        
        self.assert_eq(reg.get_features("feat1"), ["bar", "foo"])
        self.assert_eq(reg.get_features("feat2"), ["gin", "foo"])
        self.assert_eq(reg.get_features("feat3"), ["bar", "foo", "gin"])
        self.assert_eq(reg.get_features("feat4"), ["gin"])
        self.assert_eq(reg.get_features("df"), [])

    def assert_eq(self, l1, l2):
        l1 = list(l1)
        l1.sort()
        l2.sort()
        self.assertEquals(l1, l2)

    def test_factory(self):
        reg = PluginRegistry()
        reg.register_plugin(factory=lambda foo: "bar", keys=("foo",))
        self.assertEquals(reg.get_service("foo"), "bar")
        
        class S:
            def __init__(self, foo):
                pass
        
        # Make sure the objects are created once
        reg.register_plugin(factory=S, keys=("bar",))
        s1 = reg.get_service("bar")
        s2 = reg.get_service("bar")
        assert s1 is s2
        
    def test_unregister_plugin(self):
        reg = PluginRegistry()
        p = reg.register_plugin(factory=lambda foo: "bar", keys=("foo",), feats=("bar",))
        reg.unregister(p)
        
        try:
            reg.get_service("foo")
            assert False
        except ServiceError:
            pass

    def test_unregister_service(self):
        reg = PluginRegistry()
        p = reg.register_plugin(factory=lambda foo: "me", keys=("foo",), features=("bar",))
        self.assert_eq(reg.get_features("bar"), ["me"])
        self.assertEqual(reg.get_service("foo"), "me")

        reg.unregister_service("foo")
        assert len(p.keys) == 0
        try:
            reg.get_service("foo")
            assert False
        except ServiceError:
            pass
            
        self.assert_eq(reg.get_features("bar"), ["me"])
        
        try:
            reg.unregister_service("sdfds")
            assert False
        except ServiceError:
            pass

    def test_unregister_features(self):
        reg = PluginRegistry()
        p = reg.register_plugin(factory=lambda foo: "me", keys=("foo",), features=("bar",))
        self.assert_eq(reg.get_features("bar"), ["me"])
        self.assertEqual(reg.get_service("foo"), "me")

        reg.unregister_feature("bar", p)
        self.assert_eq(reg.get_features("bar"), [])

    def test_service_conflict(self):
        reg = PluginRegistry()
        p1 = reg.register_plugin(factory=lambda foo: "me", keys=("foo",), features=("bar",))
        try:
            p2 = reg.register_plugin(factory=lambda foo: "me2", keys=("foo",), features=("bar",))
            assert False
        except ServiceError:
            pass
        self.assert_eq(reg.get_features("bar"), ["me"])
        assert reg.get_service("foo") == "me"

    def test_ghost_services(self):
        reg = PluginRegistry()
        p1 = reg.register_plugin(factory=lambda foo: "me", keys=("foo",))
        assert len(reg.plugins) == 1
        assert len(p1.keys) == 1
        assert len(p1.features) == 0
        reg.unregister_service("foo")
        assert len(reg.plugins) == 0, reg.plugins
        assert len(p1.keys) == 0
        assert len(p1.features) == 0

        p1 = reg.register_plugin(factory=lambda foo: "me", features=("foo",))
        assert len(reg.plugins) == 1
        assert len(p1.keys) == 0
        assert len(p1.features) == 1
        reg.unregister_feature("foo", p1)
        assert len(reg.plugins) == 0
        assert len(p1.keys) == 0
        assert len(p1.features) == 0

if __name__ == '__main__':
    unittest.main()
