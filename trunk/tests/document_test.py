
import nose

import pida.utils.testing as testing
import pida.core.document as document

setup = testing._setup

class TestDocument1_Unnamed(nose.TestCase):

    def setUp(self):
        self.doc = document.document()
        self.doc2 = document.document()

    def test_1_filename(self):
        self.assertEqual(self.doc.filename, None)

    def test_2_uid(self):
        self.assertNotEqual(self.doc.unique_id, self.doc2.unique_id)

    def test_3_markup(self):
        self.assert_(self.doc.markup.endswith('None'))

    def test_4_project(self):
        self.assertEqual(self.doc.project_name, '')

    def test_4_project_path(self):
        self.assertRaises(AttributeError, self.doc.get_project_relative_path)

    def test_5_handler(self):
        self.assertEqual(self.doc.handler, None)

