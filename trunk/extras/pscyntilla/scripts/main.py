# Author: Roberto Cavada <cavada@irst.itc.it>
# Copyright 2004 by Roberto Cavada
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

import os.path


# this part generates gtk scintilla:
def gen_gtk_scintilla_header(signals_gen, path):

    header_templ = open(os.path.join(path, "gtkscintilla.h.in"), "r")
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

    header =  open(os.path.join(path, "gtkscintilla.h"), "w")
    header.write(header_text)
    header.close()
    return


def gen_gtk_scintilla_impl(signal_gen, path, deprecated_enabled):
    impl_templ = open(os.path.join(path, "gtkscintilla.c.in"), "r")
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

    impl =  open(os.path.join(path, "gtkscintilla.c"), "w")
    impl.write(impl_text)
    impl.close()
    return

def gen_glib_marshallers(signal_gen, path):
    marsh_fname = "marshallers.list"

    str = ""
    for m in signal_gen.signals_marshal: str += "%s\n" % m


    if os.path.isfile(marsh_fname):
        # writes it only if changed:
        mf = open(os.path.join(path, marsh_fname), 'r')
        if str == mf.read():
            mf.close()
            print "Marshallers did not change: skipping generation"
            return
        mf.close()
        pass

    mf = open(os.path.join(path, "marshallers.list"), "w")
    mf.write(str)
    mf.close()
    return


# This part generates pyscintilla
def gen_pyscintilla_wrapper(pygen, path):
    impl_templ = open(os.path.join(path, "pyscintilla.c.in"), "r")
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
        pass
    impl_text = impl_text.replace("%constants_defs%", str)

    impl = open(os.path.join(path, "pyscintilla.c"), "w")
    impl.write(impl_text)
    impl.close()
    return
    


def generate_wrapper(sci_ifc_path, path, enable_deprecated_features=True):
    """The highest level function"""
    ifc = IFace(sci_ifc_path)
    signals_gen = SignalsGen(ifc, enable_deprecated_features)
    signals_gen.gen_signals()
    
    gen_gtk_scintilla_header(signals_gen, path)    
    gen_gtk_scintilla_impl(signals_gen, path, enable_deprecated_features)       
    gen_glib_marshallers(signals_gen, path)        
    
    pygen = PythonWrapperGen(ifc)
    pygen.dump()
    gen_pyscintilla_wrapper(pygen, path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Usage: python main.py <path_to_scintilla_iface_file>"
        sys.exit(1)
        pass
    
    generate_wrapper(sys.argv[1], ".")



