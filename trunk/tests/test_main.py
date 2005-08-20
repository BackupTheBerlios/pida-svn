import base
import unittest

class TestBoss(base.Test):
    
    def _check_subplug(name):
        def check(self):
            subplug = getattr(self.pida.boss, name, 1)
            self.assertNotEqual(subplug, None)
            self.assertNotEqual(subplug, 1)
        return check

    def test_loaded(self):
        ''' Check the boss has been loaded properly '''
        self.assertNotEqual(self.pida.boss, None)
    
    def test_account_fork(self):
        self.pida.boss.action_accountfork(-999)
        self.assert_(-999 in self.pida.boss.child_processes)

    def test_fork(self):
        l1 = len(self.pida.boss.child_processes)
        self.pida.boss.action_fork(['ls', '-al'])
        l2 = len(self.pida.boss.child_processes)
        self.assertNotEquals(l1, l2)

    test_shortcuts = _check_subplug('shortcuts')
    test_terminal = _check_subplug('terminal')
    test_browser = _check_subplug('browser')
    test_filetype = _check_subplug('filetype')

base.main()
