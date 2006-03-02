
from pida.core.testing import test, assert_in, assert_equal, block_delay,\
    assert_notequal

import gobject
import os

def bm(boss):
    return boss.get_service('buffermanager')

def docs(boss):
    return bm(boss).call('get_documents')

def curdoc(boss):
    return bm(boss)._Buffermanager__currentdocument

def bd(boss):
    if boss.get_service('editormanager').editor.NAME.startswith('vim'):
        block_delay(1)
    else:
        block_delay(1)

@test
def start_up(boss):
    b = bm(boss)
    assert_equal({}, docs(boss))

@test
def open_file(boss):
    b = bm(boss)
    b.call('open_file', filename='/etc/passwd')
    bd(boss)
    assert_equal(1, len(docs(boss)))
    for doc in docs(boss).values():
        assert_equal(doc, curdoc(boss))

@test
def close_document(boss):
    # opened file from the previous test
    b = bm(boss)
    assert_equal(1, len(docs(boss)))
    for doc in docs(boss).values():
        b.call('close_document', document=doc)
    bd(boss)
    assert_equal(0, len(docs(boss)))

@test
def open_some_documents(boss):
    b = bm(boss)
    assert_equal(0, len(docs(boss)))
    for fn in ['/etc/passwd', '/etc/profile', '/etc/aliases']:
        b.call('open_file', filename=fn)
    bd(boss)
    assert_equal(3, len(docs(boss)))

@test
def close_some_documents(boss):
    """This test fails in vim."""
    b = bm(boss)
    assert_equal(3, len(docs(boss)))
    b.call('close_documents', documents=docs(boss).values())
    bd(boss)
    assert_equal(0, len(docs(boss)))

@test
def open_many_documents(boss):
    b = bm(boss)
    hdir = os.path.expanduser('~')
    slen = len(docs(boss))
    fs = 0
    for name in os.listdir(hdir):
        path = os.path.join(hdir, name)
        if os.path.isfile(path):
            try:
                b.call('open_file', filename=path)
                fs = fs + 1
            except:
                pass
            if fs == 30:
                break
    assert_equal(slen+30, len(docs(boss)))
    
@test
def close_many_documents(boss):
    """This test fails in vim."""
    b = bm(boss)
    b.call('close_documents', documents=docs(boss).values())
    block_delay(3)
    assert_equal(0, len(docs(boss)))

@test
def current_document(boss):
    b = bm(boss)
    b.call('open_file', filename='/etc/passwd')
    assert_equal(curdoc(boss).filename, '/etc/passwd')

@test
def auto_select_after_close(boss):
    b = bm(boss)
    for fn in ['/etc/passwd', '/etc/profile', '/etc/aliases']:
        b.call('open_file', filename=fn)
    bd(boss)
    b.call('close_file', filename='/etc/passwd')
    block_delay(2)
    assert_notequal(curdoc(boss), None)

    
        
    
    
        
    
