/*
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
*/


#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>

extern void pyscintilla_register_classes(PyObject *d);
extern PyObject* pyscintilla_register_constants(PyObject* m);


static PyMethodDef scintilla_funcs[] = {
    {NULL}
};

DL_EXPORT(void) initscintilla()
{
    PyObject *m, *d;

    /* initialise gobject */
    init_pygobject();
    g_assert(pygobject_register_class != NULL);


    m = Py_InitModule("scintilla", scintilla_funcs);
    d = PyModule_GetDict(m);
	
    pyscintilla_register_classes(d);
    pyscintilla_register_constants(m);

    if (PyErr_Occurred()) {
	Py_FatalError ("can't initialise module scintilla");
    }
}
