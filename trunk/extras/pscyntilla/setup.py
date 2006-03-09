# Author: Roberto Cavada <cavada@irst.itc.it>
# Copyright 2004 by Roberto Cavada
#
# This file contains code that allow you to use the Scintilla text
# widget from within pygtk2.  Pygtk2 is a Python extensions set that
# allow you to use the Gtk2 toolkit in Python programs. The author of
# pygtk2 is James Henstridge <james@daa.com.au>.
# 
# Scintilla <http://www.scintilla.org> is a very powerful editing
# component developed by Neil Hodgson <neilh@scintilla.org>. 
# 
# Also, there exists a python binding of Scintilla for Gtk+-1.x and
# pygtk-0.6.5.  It is named PyGtkScintilla, and it was made by Michele
# Campeotto <moleskine@f2s.com>. 
# 
# PygtkScintilla is partially based on ideas "stolen" from GtkScintilla2, 
# a wrapper of Scintilla for GTK2, which is developed and maintained by
# Dennis J Houy <djhouy@paw.co.za>. 
#
#
# PygtkScintilla is free software; you can redistribute it and/or 
# modify it under the terms of the GNU Lesser General Public 
# License as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later version.
#
# PygtkScintilla is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public 
# License along with this library; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#
# If you have any enhancements or bug reports, please send them to me at
# cavada@isrt.itc.it.

from distutils.core import setup, Extension, Command
from distutils.command.build import build

import scripts.utils
import scripts.main
import sys
import os.path
import glob
import fnmatch
import shutil


# Change this if you need to compile against a different version or
# location of Scintilla's top level dir:
SCINTILLA_PREFIX = "."


def get_scintilla_dir(prefix):
    entries = os.listdir(prefix)
    candidates = []
    for f in entries:
        ff = os.path.join(prefix, f)
        if os.path.isdir(ff) and fnmatch.fnmatch(f, "scintilla*") and \
               os.path.isfile(os.path.join(ff, "include/Scintilla.iface")):
            candidates.append(ff)
            pass
        pass

    if len(candidates) > 0 : return max(candidates)
    return ""

# ----------------------------------------------------------------------
def check_requirements(packages, python_req_ver):
    """returns True if all requirements are fit"""

    python_ver = sys.version.split()[0]
    if (scripts.utils.get_version_number_from_string(python_ver) <
        scripts.utils.get_version_number_from_string(python_req_ver)):
        print "Required version %s of python, found %s" \
              % (python_req_ver, python_ver)
        return 0
    
    if not scripts.utils.have_pkgconfig(): return 0

    for pkg in packages.keys():
        if not scripts.utils.pkgc_version_check(pkg, packages[pkg][0], packages[pkg][1]):
            return 0
        pass

    if not os.path.isdir(SCINTILLA_DIR):
        if os.path.normpath(SCINTILLA_PREFIX) == ".": str = "the current directory"
        else: str = "'%s/'" % os.path.normpath(SCINTILLA_PREFIX)
        
        print "Error:"
        print " Could not find Scintilla's top level directory in %s." % str
        print " Download Scintilla archive from http://www.scintilla.org"
        print " and unpack it in %s. Then run setup again." % str
        print 
        return 0

    if not os.path.isfile(SCINTILLA_LIB):
        print "Error:"
        print "It seems that you did not build scintilla."
        print "Enter directory '%s/gtk' and do 'make'" % SCINTILLA_DIR
        print
        return 0

    return 1
# ----------------------------------------------------------------------


def generate_wrappers(dependencies):
    """A list of 4 elements: ( ((sources),(targets),function,arg), ...).
    functions takes (sources),(targets) and arg"""

    for tuple in dependencies:
        most_recent_time = 0
        for f in tuple[0]:
            tm = os.path.getmtime(f)
            if tm > most_recent_time: most_recent_time = tm
            
        for f in tuple[1]:
            if not os.path.isfile(f) or (os.path.getmtime(f) < most_recent_time):
                tuple[2](tuple[0], tuple[1], tuple[3])
                break

    return


# ----------------------------------------------------------------------

def call_wrapper_gen(sources, targets, arg):
    """args is the path to the scintilla ifc"""
    scripts.main.generate_wrapper(arg, "src")
    return


def call_gen_marshal(source, targets, arg):
    assert(len(source) == 1)
    if not scripts.utils.have_glib_genmarshal():
        print "glib-genmarshal not found: files ", targets, "\ncannot be generated."
        return

    os.system('glib-genmarshal --header %s > src/marshallers.h' % source[0])
    os.system('glib-genmarshal --body %s > src/marshallers.c' % source[0])

# ----------------------------------------------------------------------


SCINTILLA_DIR = get_scintilla_dir(SCINTILLA_PREFIX)

if not os.path.isdir(SCINTILLA_DIR) and os.environ.has_key('SCINTILLA_DIR'):
    print "Reading SCINTILLA_DIR from environment variable"
    SCINTILLA_DIR = os.environ['SCINTILLA_DIR']

#if SCINTILLA_DIR: print "Found scintilla in '%s'" % SCINTILLA_DIR

SCINTILLA_LIB = os.path.join(SCINTILLA_DIR, "bin/scintilla.a")
SCINTILLA_IFC = os.path.join(SCINTILLA_DIR, "include/Scintilla.iface")

PACKAGES = { "gtk+-2.0" : ("Gtk2", "2.0.0"),
             "glib-2.0" : ("Glib2", "2.0.0"),
             "pygtk-2.0" : ("PyGTk2", "1.99.10"),
             "gthread-2.0" : ("GThread2", "2.0.0")
             }

SOURCES = ['src/pyscintilla.c',
           'src/scintillamodule.c',
           'src/gtkscintilla.c',
           'src/marshallers.c',
           'src/gtkscintilla_signals.c']



# creates libscintilla:
LIBSCINTILLA_LIB = os.path.join(SCINTILLA_DIR, "bin/libscintilla.a")



INCLUDE_DIRS = [os.path.join(SCINTILLA_DIR, 'include'), os.path.join(SCINTILLA_DIR, 'src')]
LIBRARY_DIRS = [os.path.dirname(LIBSCINTILLA_LIB)]
LIBRARIES = ['stdc++', 'scintilla', 'stdc++']

for pkg in PACKAGES.keys():
    INCLUDE_DIRS += scripts.utils.pkgc_get_include_dirs(pkg)
    LIBRARY_DIRS += scripts.utils.pkgc_get_library_dirs(pkg)
    LIBRARIES += scripts.utils.pkgc_get_libraries(pkg)


src_dependencies = (
    (("src/pyscintilla.c.in", "src/gtkscintilla.h.in", "src/gtkscintilla.c.in", SCINTILLA_IFC),
     ("src/pyscintilla.c", "src/gtkscintilla.h", "src/gtkscintilla.c", "src/marshallers.list"),
     call_wrapper_gen, SCINTILLA_IFC),
    (('src/marshallers.list',), ('src/marshallers.h', 'src/marshallers.c'),
     call_gen_marshal, None)
    )



scintilla = Extension('scintilla',
                      define_macros = [("GTK",1), ("SCI_LEXER",1)],
                      include_dirs = INCLUDE_DIRS,
                      libraries = LIBRARIES,
                      library_dirs = LIBRARY_DIRS, 
                      sources = SOURCES)

class CrossCompile(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        bdist_dir = self.get_finalized_command('bdist').bdist_base
        bdist_dir = os.path.join(bdist_dir, "cross-compile")
        lib_dir = os.path.join(bdist_dir, "PURELIB")
        self.mkpath(lib_dir)
        self.spawn([os.path.join(".", "cross-compile-scintilla")])
        self.spawn([os.path.join(".", "cross-compile-pscyntilla")])
        self.copy_file("src/scintilla.pyd", os.path.join(lib_dir, "scintilla.pyd"))
        args = self.distribution.get_option_dict("bdist_wininst")
        args["bdist_dir"] = ("command line", bdist_dir)
        args["skip_build"] = ("command line", True)
        self.run_command("bdist_wininst")


if len(sys.argv) > 1 and sys.argv[1] == 'crosscompile':
    # Don't list the 'scintilla' module otherwise we'll not be able
    # to create the installer
    kwargs = {
    }
else:
    if not check_requirements(PACKAGES, "2.2.0"):
        sys.exit(1)
    shutil.copyfile(SCINTILLA_LIB, LIBSCINTILLA_LIB)
    generate_wrappers(src_dependencies)

    kwargs = {
        "ext_modules": [scintilla]
    }



setup (name = 'pscyntilla',
       version = '1.0',
       description = 'Python wrapper for Scintilla under GTK2',
       author = 'Tiago Cogumbreiro',
       author_email = 'cogumbreiro@users.sf.net',
       url = 'http://pida.berlios.de/',
       cmdclass = {'crosscompile': CrossCompile},
       long_description = '''
Pscyntilla is a wrapper for the widget Scintilla (GTK+ version), a textual 
editing component.
''',
       **kwargs
)


