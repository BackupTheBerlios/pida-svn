import os

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

class TestDocument2_Named(nose.TestCase):

    def setUp(self):
        self.tmp = os.popen('tempfile').read().strip()
        f = open(self.tmp, 'w')
        self.txt ="""Hello I am a document
                   vlah blah"""
        f.write(self.txt)
        f.close()
        self.doc = document.realfile_document(filename=self.tmp)
       
    def test_1_filename(self):
        self.assertEqual(self.doc.filename, self.tmp)

    def test_2_string(self):
        self.assertEqual(self.doc.string, self.txt)

    def test_3_lines(self):
        self.assertEqual(len(self.doc.lines), 2)

    def test_3_len(self):
        self.assertEqual(len(self.doc), len(self.txt))

    def test_4_length(self):
        self.assertEqual(len(self.doc), self.doc.length)

    def test_5_directory(self):
        self.assertEqual(self.doc.directory, '/tmp')

    def test_6_directorybasename(self):
        self.assertEqual(self.doc.directory_basename, 'tmp')

    def tearDown(self):
        os.system('rm %s' % self.tmp)
