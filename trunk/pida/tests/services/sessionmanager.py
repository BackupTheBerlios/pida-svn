

from pida.core.testing import test, assert_equal

from pida.core.document import document

from pida.services import sessionmanager

import os
import tempfile

def c():
    f, tfile = tempfile.mkstemp()
    os.close(f)
    docs = {}
    for l in 'abcdefg':
        docs[l] = document(filename=l)
    return docs, tfile
    
def d(tfile):
    os.remove(tfile)

@test
def save(boss):
    docs, tfile = c()
    sessionmanager.save_documents_to_file(docs, tfile)
    f = open(tfile, 'r')
    orig = set('abcdefg')
    load = set()
    for line in f:
        load.add(line.strip())
    assert_equal(orig, load)
    d(tfile)

@test
def load(boss):
    docs, tfile = c()
    sessionmanager.save_documents_to_file(docs, tfile)
    docs = sessionmanager.get_documents_from_file(tfile)
    orig = set('abcdefg')
    load = set()
    for doc in docs:
        load.add(doc)
    assert_equal(orig, load)
    d(tfile)        

