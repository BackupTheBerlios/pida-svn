import parsers

def test_module(filename):
    import scintilla
    total = 0
    missing = []
    try:
        header = open(filename)
        for name, val in parsers.iter_header_constants(header):
            if not hasattr(scintilla, name):
                missing.append((name, val))
            total += 1
    finally:
        header.close()
    
    for name, val in missing:
        print "%s = %d" % (name, val)
    print "Compliance: %d/%d" % (total - len(missing), total)

if __name__ == '__main__':
    import sys
    import glob
    from os import path
    base_path = path.dirname(__file__)
    val = path.join(base_path, * "../build/lib.*/scintilla.*".split("/"))
    files = glob.glob(val)
    
    print val
    assert len(files) == 1, "run 'setup.py build' first"
    sys.path.insert(0, path.dirname(files[0]))
    test_module(path.join(base_path, * "../scintilla/include/Scintilla.h".split("/")))


