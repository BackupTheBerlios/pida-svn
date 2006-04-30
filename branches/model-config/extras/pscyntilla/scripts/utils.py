import sys
import os

# This functions were taken and adapted from pygtk distribution.
# 

def getoutput(cmd):
    """Return output (stdout or stderr) of executing cmd in a shell."""
    return getstatusoutput(cmd)[1]


def get_version_number_from_string(str):
    return map(int, str.split("."))


def getstatusoutput(cmd):
    """Return (status, output) of executing cmd in a shell."""
    if sys.platform == 'win32':
        pipe = os.popen(cmd, 'r')
        text = pipe.read()
        sts = pipe.close() or 0
        if text[-1:] == '\n':
            text = text[:-1]
        return sts, text
    else:
        from commands import getstatusoutput
        return getstatusoutput(cmd)

def have_pkgconfig():
    """Checks for the existence of pkg-config"""
    if (sys.platform == 'win32' and
        os.system('pkg-config --version > NUL') == 0):
        return 1
    else:
        if getstatusoutput('pkg-config')[0] == 256:
            return 1

def have_glib_genmarshal():
    """Checks for the existence of glib-genmarshal"""
    if os.system('glib-genmarshal --version') == 0: return 1
    else: return 0


def pkgc_version_check(name, longname, req_version):
    is_installed = not os.system('pkg-config --exists %s' % name)
    if not is_installed:
        print "Could not find %s" % longname
        return 0
    
    orig_version = getoutput('pkg-config --modversion %s' % name)
    version = get_version_number_from_string(orig_version)
    pkc_version = get_version_number_from_string(req_version)
                      
    if version >= pkc_version: return 1
    else:
        print "Warning: Too old version of %s" % longname
        print "         Need %s, but %s is installed" % \
              (pkc_version, orig_version)
        self.can_build_ok = 0
        pass
    
    return 0

    
    
def pkgc_get_include_dirs(name):
    output = getoutput('pkg-config --cflags-only-I %s' % name)
    return output.replace('-I', '').split()

def pkgc_get_libraries(name):
    output = getoutput('pkg-config --libs-only-l %s' % name)
    return output.replace('-l', '').split()
    
def pkgc_get_library_dirs(name):
    output = getoutput('pkg-config --libs-only-L %s' % name)
    return output.replace('-L', '').split()
