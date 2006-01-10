import base
import unittest

class TestBoss(base.Test):
    

    def _check_subplug(name):
        def check(self):
            subplug = getattr(self.pida.boss, name, 1)
            self.assertNotEqual(subplug, None)
            self.assertNotEqual(subplug, 1)
        return check

    def test_boss_loaded(self):
        self.assertNotEqual(self.pida.boss, None)
    
    def test_action_accountfork(self):
        self.pida.boss.action_accountfork(-999)
        self.assert_(-999 in self.pida.boss.child_processes)

    def test_action_fork(self):
        l1 = len(self.pida.boss.child_processes)
        self.pida.boss.action_fork(['uname', '-a'])
        l2 = len(self.pida.boss.child_processes)
        self.assertNotEquals(l1, l2)

    def test_boss_is_base(self):
        self.assertEquals(self.pida.boss, self.pida.prop_boss)

    test_subplugin_shortcuts = _check_subplug('shortcuts')
    test_subplugin_terminal = _check_subplug('terminal')
    test_subplugin_browser = _check_subplug('browser')
    test_subplugin_filetype = _check_subplug('filetype')

class TestMainWindow(base.Test):

    def test_mainwindow_exists(self):
        self.assert_(hasattr(self.pida, 'mainwindow'))

class TestEmbedWindow(base.Test):

    def test_embedwindow_exists(self):
        self.assert_(hasattr(self.pida, 'embedwindow'))
        
class TestEditor(base.Test):

    def test_culebra(self):
        self.assertEquals(self.pida.editor.NAME, 'Culebra')

    def test_gotoline(self):
        self.assert_(hasattr(self.pida.editor, 'edit_gotoline'))

    def test_openfile(self):
        self.assert_(hasattr(self.pida.editor, 'edit_openfile'))


    

tests = [TestMainWindow, TestBoss, TestEmbedWindow, TestEditor]
suites = [unittest.makeSuite(t) for t in tests]
alltests = unittest.TestSuite(suites)

for ed in ['culebra']:
    base.pida.registry.components.editor.set(ed)
    base.pida.startup()
    unittest.TextTestRunner(verbosity=5).run(alltests)
