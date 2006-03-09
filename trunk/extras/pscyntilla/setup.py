__copyright__ = """"2006 by Tiago Cogumbreiro <cogumbreiro@users.sf.net>
2004 by Roberto Cavada <cavada@irst.itc.it>"""
__license__ = "LGPL <http://www.gnu.org/copyleft/lesser.txt>"

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
    description = ("cross compile the Python extension module to win32 "
                   "and generate the installer for it.")
    user_options = [
        ("scintilla-dir=", None, "Scintilla source directory."),
        ("build-scintilla", None, ("cross compiles the Scintilla library, "
                                   "and quits.")),
        ("build-only", None, "doesn't create the installer."),
        ("clean-only", None, "cleans the generated files and quits."),
    ]
    
    boolean_options = ["build-scintilla", "build-only", "clean-only"]

    def initialize_options(self):
        self.scintilla_dir = None
        self.build_scintilla = False
        self.build_only = False
        self.clean_only = False
        
        get_dir = lambda foo: os.path.join(".", foo)
        self._compile_scintilla = get_dir("cross-compile-scintilla")
        self._compile_pscyntilla = get_dir("cross-compile-pscyntilla")
        
    def finalize_options(self):
        if self.scintilla_dir is None:
            self.scintilla_dir = os.path.abspath(os.path.join(".", "scintilla"))

    def _make(self, make, *args):
        cmd = ["sh", make, self.scintilla_dir]
        cmd.extend(args)
        self.spawn(cmd)

    def scintilla_make(self, *args):
        self._make(self._compile_scintilla, *args)
        
    def pscyntilla_make(self, *args):
        self._make(self._compile_pscyntilla, *args)

    def create_installer(self):
        bdist_dir = self.get_finalized_command('bdist').bdist_base
        bdist_dir = os.path.join(bdist_dir, "cross-compile")
        lib_dir = os.path.join(bdist_dir, "PURELIB")
        self.mkpath(lib_dir)
        self.copy_file("src/scintilla.pyd", os.path.join(lib_dir, "scintilla.pyd"))
        args = self.distribution.get_option_dict("bdist_wininst")
        args["bdist_dir"] = ("command line", bdist_dir)
        args["skip_build"] = ("command line", True)
        self.run_command("bdist_wininst")

    def run(self):
        if self.clean_only:
            self.scintilla_make("clean")
            self.pscyntilla_make("clean")
            return

        self.scintilla_make()
        if self.build_scintilla:
            return
            
        self.pscyntilla_make()
        
        if self.build_only:
            return
        
        self.create_installer()


CrossCompile.__name__ = "crosscompile"

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

