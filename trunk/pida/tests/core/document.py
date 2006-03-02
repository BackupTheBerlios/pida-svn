
import os

from pida.core.document import document
from pida.core.testing import test, assert_equal, assert_notequal

def c():
    tmp = os.popen('tempfile').read().strip()
    f = open(tmp, 'w')
    txt ="""Hello I am a document
               vlah blah"""
    f.write(txt)
    f.close()
    doc = document(filename=tmp)
    return doc, tmp, txt

def d(tmp):
    os.system('rm %s' % tmp)

@test
def new_document(boss):
    doc = document()
    assert_equal(doc.is_new, True)

@test
def unnamed_document(boss):
    doc = document()
    assert_equal(doc.filename, None)

@test
def unnamed_is_new(boss):
    doc = document()
    assert_equal(doc.is_new, True)
    assert_equal(doc.filename, None)

@test
def new_index(boss):
    doc = document()
    doc2 = document()
    assert_notequal(doc.newfile_index, doc2.newfile_index)

@test
def no_project(boss):
    doc = document()
    assert_equal(doc.project_name, '')

@test
def no_handler(boss):
    doc = document()
    assert_equal(doc.handler, None)

@test
def unique_id(boss):
    doc = document()
    doc2 = document()
    assert_notequal(doc.unique_id, doc2.unique_id)

@test
def real_file(boss):
    doc, tmp, txt = c()
    assert_equal(doc.filename, tmp)
    d(tmp)

@test
def file_text(boss):
    doc, tmp, txt = c()
    assert_equal(doc.string, txt)
    d(tmp)

@test
def file_lines(boss):
    doc, tmp, txt = c()
    assert_equal(len(doc.lines), 2)
    d(tmp)

@test
def file_len(boss):
    doc, tmp, txt = c()
    assert_equal(len(doc), len(txt))
    d(tmp)

@test
def file_length(boss):
    doc, tmp, txt = c()
    assert_equal(doc.length, len(doc))
    d(tmp)

@test
def directory(boss):
    doc, tmp, txt = c()
    assert_equal(doc.directory, '/tmp')
    d(tmp)

@test
def directory_basename(boss):
    doc, tmp, txt = c()
    assert_equal(doc.directory_basename, 'tmp')
    d(tmp)

