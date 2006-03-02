
from pida.core.testing import test, assert_in, assert_equal, block_delay

import gobject

def bm(boss):
    return boss.get_service('buffermanager')

def docs(boss):
    return bm(boss).call('get_documents')

def curdoc(boss):
    return bm(boss)._Buffermanager__currentdocument

@test
def start_up(boss):
    b = bm(boss)
    assert_equal({}, docs(boss))

@test
def open_file(boss):
    b = bm(boss)
    b.call('open_file', filename='/etc/passwd')
    assert_equal(1, len(docs(boss)))
    block_delay(1)
    for doc in docs(boss).values():
        assert_equal(doc, curdoc(boss))

@test
def close_document(boss):
    # opened file from the previous test
    b = bm(boss)
    assert_equal(1, len(docs(boss)))
    for doc in docs(boss).values():
        b.call('close_document', document=doc)
    block_delay(1)
    assert_equal(0, len(docs(boss)))
        
    
