# Author: Roberto Cavada <cavada@irst.itc.it>
# Copyright 2004 by Roberto Cavada
# Copyright 2006 by Pida Project
#
# This file contains code generators that allow you to use the Scintilla text
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
# PyScintilla2 is partially based on ideas "stolen" from GtkScintilla2, 
# a wrapper of Scintilla for GTK2, which is developed and maintained by
# Dennis J Houy <djhouy@paw.co.za>. 
#
#
# PyScintilla2 is free software; you can redistribute it and/or 
# modify it under the terms of the GNU Lesser General Public 
# License as published by the Free Software Foundation; either 
# version 2 of the License, or (at your option) any later version.
#
# PyScintilla2 is distributed in the hope that it will be useful, 
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


from iface import IFace
from gens import SignalsGen, PythonWrapperGen

from os import path
import parsers

################
# parser of headers


# this part generates gtk scintilla:
def gen_gtk_scintilla_header(signals_gen, basedir):

    header_templ = open(path.join(basedir, "gtkscintilla.h.in"), "r")
    header_text = header_templ.read()
    header_templ.close()
  
    str = ""
    is_first = True
    for enum in signals_gen.signals_enums:
        if is_first:
            is_first = False
            str += enum + " = 0,\n"
        else: str += enum + ",\n"
        pass
    header_text = header_text.replace("%signals_enums%", str)

    str = ""
    for pointer in signals_gen.signals_pointers:
        str += pointer + "\n"
        pass
    header_text = header_text.replace("%signal_handlers_pointers%", str)

    header =  open(path.join(basedir, "gtkscintilla.h"), "w")
    header.write(header_text)
    header.close()
    return


def gen_gtk_scintilla_impl(signal_gen, basedir, deprecated_enabled):
    impl_templ = open(path.join(basedir, "gtkscintilla.c.in"), "r")
    impl_text = impl_templ.read()
    impl_templ.close()

    if deprecated_enabled:
        impl_text = impl_text.replace("%set_deprecated_features%",
                                      "#define INCLUDE_DEPRECATED_FEATURES")
    else: impl_text = impl_text.replace("%set_deprecated_features%",
                                        "#undef INCLUDE_DEPRECATED_FEATURES")

    str = ""
    for constr in signal_gen.signal_news:
        str += constr + "\n"
        pass

    impl_text = impl_text.replace("%signals_construction%", str)

    str = ""
    for constr in signal_gen.signal_emitters:
        str += constr + "\n"
        pass

    impl_text = impl_text.replace("%notif_handling_code%", str)   

    impl =  open(path.join(basedir, "gtkscintilla.c"), "w")
    impl.write(impl_text)
    impl.close()
    return

def gen_glib_marshallers(signal_gen, basedir):
    marsh_fname = "marshallers.list"

    str = ""
    for m in signal_gen.signals_marshal: str += "%s\n" % m


    if path.isfile(marsh_fname):
        # writes it only if changed:
        mf = open(path.join(basedir, marsh_fname), 'r')
        if str == mf.read():
            mf.close()
            print "Marshallers did not change: skipping generation"
            return
        mf.close()
        pass

    mf = open(path.join(basedir, "marshallers.list"), "w")
    mf.write(str)
    mf.close()
    return


# This part generates pyscintilla
def gen_pyscintilla_wrapper(pygen, basedir):
    impl_templ = open(path.join(basedir, "pyscintilla.c.in"), "r")
    impl_text = impl_templ.read()
    impl_templ.close()

    # methods definitions:
    str = ""
    for meth in pygen.meth_defs:
        str += "%s\n" % meth
        pass
    impl_text = impl_text.replace("%methods_definitions%", str)

    impl_text = impl_text.replace("%methods_table%", pygen.meth_table)

    # constants:
    str = ""
    for c in pygen.constants:
        str += "if (PyModule_AddIntConstant(m, \"%s\", %s) != 0) { return NULL; }\n" % c
    impl_text = impl_text.replace("%constants_defs%", str)

    impl = open(path.join(basedir, "pyscintilla.c"), "w")
    impl.write(impl_text)
    impl.close()
    return
    

def update_constants(header, pygen):
    try:
        fd = open(header)
        for name, val in parsers.iter_header_constants(fd):
            pygen.dump_constant(name, str(val))
    finally:
        fd.close()


def generate_wrapper(headers_dir, basedir, enable_deprecated_features=True):
    """The highest level function"""
    
    scintilla_iface = path.join(headers_dir, "Scintilla.iface")
    header = path.join(headers_dir, "Scintilla.h")
    
    ifc = IFace(scintilla_iface)
    signals_gen = SignalsGen(ifc, enable_deprecated_features)
    signals_gen.gen_signals()
    
    gen_gtk_scintilla_header(signals_gen, basedir)
    gen_gtk_scintilla_impl(signals_gen, basedir, enable_deprecated_features)       
    gen_glib_marshallers(signals_gen, basedir)
    
    pygen = PythonWrapperGen(ifc)
    update_constants(header, pygen)
    pygen.dump()
    
    gen_pyscintilla_wrapper(pygen, basedir)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Usage: python main.py <path_to_scintilla_iface_file>"
        sys.exit(1)
        pass
    
    generate_wrapper(sys.argv[1], ".")


