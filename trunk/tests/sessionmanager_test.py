
from pida.utils.testing import _ServiceTest, _setup

from pida.core.document import document

from pida.services import sessionmanager

import nose
import os
import tempfile

set_up = _setup

class SessionLoadTest(nose.TestCase):

    def setUp(self):
        f, self.tfile = tempfile.mkstemp()
        os.close(f)
        self.docs = {}
        for l in 'abcdefg':
            self.docs[l] = document(filename=l)

    def test_1_save(self):
        sessionmanager.save_documents_to_file(self.docs, self.tfile)
        f = open(self.tfile, 'r')
        orig = set('abcdefg')
        load = set()
        for line in f:
            load.add(line.strip())
        self.assertEqual(orig, load)

    def test_2_load(self):
        sessionmanager.save_documents_to_file(self.docs, self.tfile)
        docs = sessionmanager.get_documents_from_file(self.tfile)
        orig = set('abcdefg')
        load = set()
        for doc in docs:
            load.add(doc)
        self.assertEqual(orig, load)
        
    def tearDown(self):
        os.remove(self.tfile)

