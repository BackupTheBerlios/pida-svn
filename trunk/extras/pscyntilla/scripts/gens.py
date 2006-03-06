# Author: Roberto Cavada <cavada@irst.itc.it>
# Copyright 2004 by Roberto Cavada
# Copytight 2006 by Tiago Cogumbreiro
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

import string


# ----------------------------------------------------------------------
class SignalsGen:
    
    def __init__(self, iface, allow_deprecated):
        self.iface = iface
        self.allow_deprecated = allow_deprecated
        self.ren = NameRemapper()
        self.typeconv = TypesConverter()
        self.beautier = CCodeBeautier()
        
        
        self.dont_generate = ()

        self.signals_enums = []
        self.signals_pointers = []

        self.signals_marshal = []
        self.signal_news = []
        self.signal_emitters = []

        self.signal_new_template = """klass->signals[%s] =
g_signal_new ("%s",
G_OBJECT_CLASS_TYPE(object_class),
G_SIGNAL_RUN_LAST,
G_STRUCT_OFFSET(GtkScintillaClass, %s),
NULL, NULL,
%s, 
%s, %d%s);
"""
        self.signal_emitter_template = """case %s:        
%s  g_signal_emit(G_OBJECT (data), klass->signals[%s], 0%s);
%sbreak;
%s
"""
            
        return


    def gen_signals(self):
        cats = self.iface.get_categories()
        for cat in cats.keys():
            is_deprecated = self.iface.is_deprecated(cat)
            if is_deprecated and not self.allow_deprecated: continue
            signals = cats[cat]['signals']
            for s in signals:
                self.gen_signal(s[0], s[1], is_deprecated)
                pass
            pass
        
        return

    def gen_signal(self, sgn, cmt, is_deprecated):
        name = sgn[0]
        ret_type = sgn[1]
        args = sgn[2]
        id = sgn[3]

        if name in self.dont_generate: return

        glib_ret_type = self.typeconv.sci2glib(ret_type)
        args_glib = []

        signal_name = self.ren.rename_signal_name(name)
        enum_name = self.ren.rename_signal_enum(name)
        pointer_name = name
        scintilla_event_name = "SCN_%s" % name.upper()

        self.signals_enums.append(enum_name)

        # pointers for signals:
        pars = ""
        for arg in args:
            if len(arg) < 2: continue

            glib_type = self.typeconv.sci2glib(arg[0])
            pars += "%s %s, " % (glib_type, arg[1])
            args_glib.append((glib_type, arg[1]))
            pass
        
        entry = "%s (*%s) (GtkWidget* w, %sgpointer user_data);" \
                % (glib_ret_type, pointer_name, pars)

        self.signals_pointers.append(entry)

        # marshal:

        if len(args) > 1: marshal_prefix = "g_cclosure_user_marshal_"
        else: marshal_prefix = "g_cclosure_marshal_"
        
        ret_type_marshal = self.typeconv.glib2marshaller(glib_ret_type)
        if len(args_glib) == 0:
            marshaller_name = "%s%s__VOID" % (marshal_prefix, ret_type_marshal)
        else: marshaller_name = "%s%s__" % (marshal_prefix, ret_type_marshal)
        marshal = "%s:" % ret_type_marshal
        is_first = True
        for glib in args_glib:
            arg_marshal = self.typeconv.glib2marshaller(glib[0])

            if is_first:
                is_first = False
                marshaller_name += arg_marshal
                marshal += arg_marshal
            else:
                marshaller_name += "_%s" % arg_marshal
                marshal += ",%s" % arg_marshal
                pass
                
            pass

        if marshal not in self.signals_marshal and len(args) > 1:
            self.signals_marshal.append(marshal)
            pass

        # signal creation code
        args_glib_types = ""
        for glib in args_glib:
            args_glib_types += ", %s" % self.typeconv.glib2glibtype(glib[0])
            pass
        
        signal_new = self.signal_new_template \
                     % (enum_name, signal_name, pointer_name,
                        marshaller_name,
                        self.typeconv.glib2glibtype(glib_ret_type),
                        len(args_glib), args_glib_types)

        self.signal_news.append(signal_new)


        # emitters:
        if is_deprecated:
            depre_code =  "if (warn == 0) {\ng_warning(\"Scintilla's signal '%s' is deprecated and should not be used.\");\nwarn = 1;\n}\n"\
                         % signal_name
            depre_code_prefix = "{\n static int warn=0;\n"
            depre_code_suffix = "}\n"
            
        else:
            depre_code = ""
            depre_code_prefix = ""
            depre_code_suffix = ""
            pass

        pars = ""
        for glib in args_glib: pars += ", (%s) notification->%s" % glib
        signal_emit = self.signal_emitter_template \
                      % (scintilla_event_name, depre_code_prefix, enum_name, pars, depre_code, depre_code_suffix)

        signal_emit = self.beautier.indent(signal_emit, 2)                
        self.signal_emitters.append(signal_emit)
        return
    


    pass # end of class


# ----------------------------------------------------------------------
class PythonWrapperGen:

    def __init__(self, iface):

        self.ren = NameRemapper()
        self.typeconv = TypesConverter()
        self.iface = iface
        self.beautier = CCodeBeautier()
        self.constants = []

        self.dont_generate = ["AddStyledText", "FindText",  
                              "FormatRange",
                              "GetStyledText", "GetTextRange"]

        self.code_fact = CodeFactory()

        self.did_not_generate = []

        self.meth_decls = []
        self.meth_defs = []
        self.meth_table = ""

        self.signals_enums = []
        return

    
    def dump(self):
        self.dump_funcs()
        self.dump_getters()
        self.dump_setters()
        self.dump_meth_table()
        self.dump_constants()
        return

    def dump_constants(self):
        cats = self.iface.get_categories()
        for cat in cats.keys():
            cs = cats[cat]['constants']
            for c in cs:
                self.dump_constant(c)
                pass
            pass
        
        return

    def dump_constant(self, c):
        self.constants.append((c[0][0], c[0][1]))
        return


    def dump_meth_table(self):
        head = "PyMethodDef pyscintilla_methods[] = {\n"
        tail = "  { NULL, NULL, 0, NULL}\n};"

        meths = []
        cats = self.iface.get_categories()
        for cat in cats.keys():
            funcs = cats[cat]['functions'] + cats[cat]['setters'] +  cats[cat]['getters']
            for func in funcs:
                if func[0][0] in (self.dont_generate + self.did_not_generate): continue
                has_args = False
                for arg in func[0][2]:
                    if arg:
                        has_args = True
                        break
                    pass
                
                if has_args:  arg_type = "METH_VARARGS|METH_KEYWORDS"
                else: arg_type = "METH_NOARGS"
                comment = self.beautier.clean_string(func[1])
                func_name = self.ren.rename_fun(func[0][0])
                meths.append("{\"%s\", (PyCFunction)_wrap_%s, %s, \"%s\"}" \
                             % (func_name, func_name,
                                arg_type, comment))
                pass
            pass

        self.meth_table = head
        for meth in meths:
            self.meth_table += "  " + meth + ",\n"
            pass
        self.meth_table += tail + "\n"
        return
        

    def dump_funcs(self):
        cats = self.iface.get_categories()
        for cat in cats.keys():
            funcs = cats[cat]['functions']
            for func in funcs:
                #self.dump_fun(func[0], func[1])
                try: self.dump_fun(func[0], func[1])
                except Exception, e:
                    print "An error occurred while generating function '%s': %s" % (func[0][0], e)
                    self.did_not_generate.append(func[0][0])
                    pass
                pass
            pass

        return

    def dump_getters(self):
        cats = self.iface.get_categories()
        for cat in cats.keys():
            funcs = cats[cat]['getters']
            for func in funcs:
                try: self.dump_fun(func[0], func[1])
                except Exception, e:
                    print "An error occurred while generating getter '%s': %s" % (func[0][0], e)
                    self.did_not_generate.append(func[0][0])
                    pass                
                pass
            pass

        return

    def dump_setters(self):
        cats = self.iface.get_categories()
        for cat in cats.keys():
            funcs = cats[cat]['setters']
            for func in funcs:
                try: self.dump_fun(func[0], func[1])
                except Exception, e:
                    print "An error occurred while generating setter '%s': %s" % (func[0][0], e)
                    self.did_not_generate.append(func[0][0])
                    pass
                pass
            pass
        
        return


    def dump_fun(self, fun, comment):
        name = fun[0]
        args = fun[2]
        id = fun[3]

        ret_types = [(fun[1], "sci_ret")]
        before_return_code = ""
        
        if name in self.dont_generate: return
        
        local_vars = []
        call_vars = []
        cmpx_objects_code = []
        stringresult = None # par string name

        # collects info about arguments
        format = ""
        for arg in args:
            if arg is not None:
                if len(arg) < 2:
                    call_vars.append(None)
                    continue
                t = self.typeconv.sci2glib(arg[0])
                assert t

                if arg[0] == "stringresult":
                    stringresult = arg[1]
                    local_vars.append((t, "_" + arg[1]))
                    call_vars.append(("(char*)", "_%s" % arg[1]))
                    ret_types.append(("string", "_%s" % arg[1]))
                    
                    # makes the length optional
                    if (len(args) == 2) and args[0] and (args[0][0] == "int") and  (args[0][1] == "length"):
                        format = "|%s" % format
                    else:
                        # force length to be declared:
                        if not ("gint", "_length") in local_vars:
                            local_vars.append(("gint", "_length"))
                            pass
                        pass
                        
                    continue
                    
                local_vars.append((t, "_" + arg[1]))

                f = self.typeconv.sci2format(arg[0])
                assert f
                format += f

                if f == 'O':
                    local_vars.append(("long", "_%s_c" % arg[1]))
                    call_vars.append (("long", "_%s_c" % arg[1]))
                    cmpx_objects_code.append(self.code_fact.sci2code(arg[0], arg[1]))
                else: call_vars.append((t, "_" + arg[1]))

                pass
            pass

        # function prototype
        if len(local_vars) == 0: proto = "static PyObject* _wrap_%s(PyGObject* self)"  \
           % self.ren.rename_fun(name)
        else: proto = "static PyObject* _wrap_%s(PyGObject* self, PyObject* args, "\
                      "PyObject* keywds)"  % self.ren.rename_fun(name)

        # keywords
        kwlist = ""
        parse_str = ""
        if len(local_vars) > 0:
            kwlist = "  static char* __kwlist__[] = { "
            for arg in args:
                if stringresult and arg and arg[1] == stringresult: continue  # skips text
                if arg: kwlist += "\"%s\", " % arg[1]
                pass
            kwlist += "NULL };\n"
        
            parse_str = "  if (!PyArg_ParseTupleAndKeywords(args, keywds, \"%s\", __kwlist__" \
                        % format
            vars_ref = ""
            for var in local_vars: vars_ref += ", &%s" % var[1]
            parse_str += vars_ref + ")) { \n    return NULL;\n  }"
            pass


        # object checks
        cmpx_obj_checks = "\n"
        for cmpx in cmpx_objects_code:
            cmpx_obj_checks += cmpx
            pass

        cmpx_obj_checks = self.beautier.indent(cmpx_obj_checks, 2)

        # call to scintilla method
        call_args = ['0', '0']
        for i in range(len(call_vars)):
            if call_vars[i]: call_args[i] = "(int) %s" % call_vars[i][1]
            pass

        if (ret_types[0][0] != 'void'):
            if (ret_types[0][0] == "colour"): tmp = "gint"
            else: tmp = self.typeconv.sci2glib(ret_types[0][0])
            local_vars.append((tmp, ret_types[0][1]))
            scintilla_call = "  %s = (%s) scintilla_send_message(SCINTILLA(GTK_SCINTILLA(self->obj)->scintilla), %s, %s, %s);\n" \
                             % (ret_types[0][1], tmp, id, call_args[0], call_args[1])
        else: scintilla_call = "  scintilla_send_message(SCINTILLA(GTK_SCINTILLA(self->obj)->scintilla), %s, %s, %s);\n" \
                               % (id, call_args[0], call_args[1])

        # special handle for string result
        strresult_code = ""
        if stringresult:
            strresult_code = \
"""if (_length == -1) {
  _length = %s}
_%s = g_new(char, _length + 1);
""" % (scintilla_call, stringresult)

            before_return_code += "g_free(_%s);\n" % stringresult
            pass

        if (ret_types[0][0] == "bool"):
            before_return_code += "Py_INCREF(__res__);\n"
            pass
        
        # prepares return statement:
        if before_return_code:
            local_vars.append(("PyObject*", "__res__"))
            res_assgm = "__res__ = %%s;%sreturn __res__;" % before_return_code
        else: res_assgm = "return %s;"
        
        if len(ret_types) == 1:
            if ret_types[0][0] == "void":                
                return_stmnt = "Py_INCREF(Py_None); %s" % res_assgm % "Py_None"
            elif ret_types[0][0] == "bool":
                return_stmnt = res_assgm % "(%s) ? Py_True : Py_False" % ret_types[0][1]
            else:
                return_stmnt = res_assgm % "PyInt_FromLong(%s)" % ret_types[0][1]
                pass
        else:
            format = ""
            build_args = ""
            for ret_type in ret_types:
                if ret_type[0] != "void":
                    format += self.typeconv.sci2format(ret_type[0])
                    build_args += ", %s" % ret_type[1]
                    pass
                pass

            return_stmnt = res_assgm % "Py_BuildValue(\"%s\" %s)" % (format, build_args)
            pass
        
        return_stmnt = self.beautier.indent(return_stmnt, 2)

        vars_decl = ""
        for var in local_vars:
            if stringresult and var[0] == "gint" and var[1] == "_length":
                vars_decl += "  %s %s=-1; \n" % var
            elif stringresult and var[1] == ("_%s" % stringresult):
                vars_decl += "  %s %s=(char*) NULL; \n" % var
            else: vars_decl += "  %s %s; \n" % var
            pass

        self.meth_decls.append(proto + ";")
        meth_body = "%s\n{\n%s%s%s%s\n%s%s\n%s}\n" \
                    % (proto, vars_decl, kwlist, parse_str, cmpx_obj_checks, self.beautier.indent(strresult_code, 2), 
                       scintilla_call, return_stmnt)
        self.meth_defs.append(meth_body)
        return
           
    pass # end of class


# ----------------------------------------------------------------------
class CCodeBeautier:

    def clean_string(self, text):
        text = text.replace("\\", "\\\\")
        text = text.replace("\r", "")
        text = text.replace("\n", "\\n")
        text = text.replace('"', '\\"')
        return text
    

    def indent(self, code, indent_level):
        res = ""

        lines = code.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                res += "\n"
                continue

            prefix_text = " " * indent_level
            if ";" in line:
                line_lines = line.split(";")
                for l in line_lines:
                    l = l.strip()
                    if l: res += "%s%s;\n" % (prefix_text, l)
                    pass
                pass
            else: res += "%s%s\n" % (prefix_text, line)
            
            if line[-1] == "{": indent_level += 2
            if line[-1] == "}" and indent_level > 0: indent_level -= 2
            pass
        
        return res
    
    pass # end of class


# ----------------------------------------------------------------------

WHITE_LIST = {
    "UTF8": "Utf8",
    "EOL": "Eol",
    "VCHome": "Vchome",
}

def camel_to_gnu(name):

    if len(name) == 0:
        return name

    for key, val in WHITE_LIST.items():
        name = name.replace(key, val)

    return camel_to_gnu_aux(name, 0)


def camel_to_gnu_aux(name, offset):
    if name[0].isupper():
        name = "%s%s" % (name[0].lower(), name[1:])
        
        
    words = name.split(string.ascii_uppercase[offset])
    if len(words) > 1:
        prepend_char = lambda word: "%s%s" % (string.ascii_lowercase[offset], word)
        
        n_words = map(prepend_char, words[1:])
        n_words.insert(0, words[0])
        words = n_words

    offset += 1
    if offset == len(string.ascii_uppercase):
        return "_".join(words)

    else:
        return "_".join(map(lambda w: camel_to_gnu_aux(w, offset), words))

class NameRemapper:

    def rename_fun(self, name):
        return camel_to_gnu(name)

    def rename_signal_enum(self, name):
        return name.upper()

    def rename_signal_name(self, name):
        return camel_to_gnu(name).replace("_", "-")



# ----------------------------------------------------------------------
class CodeFactory:
    def __init__(self):
        colour_code = """
if (PyInt_Check(_%(var_name)s)) _%(var_name)s_c = PyInt_AsLong(_%(var_name)s); 
else if (pyg_boxed_check(_%(var_name)s, GDK_TYPE_COLOR)) {
  GdkColor* _%(var_name)s_py; 
  _%(var_name)s_py = pyg_boxed_get(_%(var_name)s, GdkColor);
  /* color is scaled down to 24 bits: */
  _%(var_name)s_c = (((((int)((double)_%(var_name)s_py->blue  * 255.0 / 65535.0)) << 8) | 
                       ((int)((double)_%(var_name)s_py->green * 255.0 / 65535.0)) << 8) | 
                       ((int)((double)_%(var_name)s_py->red   * 255.0 / 65535.0)));
}
else {
  PyErr_SetString(PyExc_TypeError, "'%(var_name)s' should be either a GdkColor or an integer number.");
  return NULL; 
}
"""

        self.__sci2code = { 'colour' : colour_code,
                            'color'  : colour_code
                            }

        return


    def sci2code(self, sci_type, var_name):
        ret = None
        if self.__sci2code.has_key(sci_type):
            ret = self.__sci2code[sci_type]  % {'var_name' : var_name}
        return ret
    
    pass # end of class
    

# ----------------------------------------------------------------------
class TypesConverter:

    def __init__(self):

        self.__sci2format = {
            'void' : "",
            'int'  : "i", 
            'bool' : "i",
            'position' : "l",
            'color' : "O",
            'colour' : "O",
            'string' : "s",
            'cells' : None,  # not supported at the moment
            'textrange' : "O",
            'findtext' : None, 
            'keymod' : "i"
            }

        self.__sci2glib = {
            'void' : "void", 
            'int'  : "gint", 
            'bool' : "gboolean",
            'position' : "glong",
            'color' : "PyObject*",
            'colour' : "PyObject*",
            'string' : "gchar*",
            'stringresult' : "gchar*", 
            'cells' : None,  # not supported at the moment
            'textrange' : "PyObject*",
            'findtext' : None, 
            'keymod' : "gint"
            }

        self.__glib2marshaller = {
            "void"      : "VOID",
            "gboolean"  : "BOOLEAN",
            "gint"      : "INT",
            "guint"     : "UINT", 
            "glong"     : "LONG",
            "gulong"    : "ULONG",
            "gfloat"    : "FLOAT",
            "gdouble"   : "DOUBLE", 
            "gchar"     : "CHAR",
            "gchar*"    : "STRING",
            "gpointer"  : "POINTER",
            "PyObject*" : "OBJECT",
            "GObject*"  : "OBJECT",
            "GBoxed*"   : "BOXED"
            }

        self.__glib2glibtype = {
            "void"      : "G_TYPE_NONE",
            "gboolean"  : "G_TYPE_BOOLEAN",
            "gint"      : "G_TYPE_INT",
            "guint"     : "G_TYPE_UINT", 
            "glong"     : "G_TYPE_LONG",
            "gulong"    : "G_TYPE_ULONG",
            "gfloat"    : "G_TYPE_FLOAT",
            "gdouble"   : "G_TYPE_DOUBLE", 
            "gchar"     : "G_TYPE_CHAR",
            "gchar*"    : "G_TYPE_STRING",
            "gpointer"  : "G_TYPE_POINTER",
            "PyObject*" : "G_TYPE_OBJECT",
            "GObject*"  : "G_TYPE_OBJECT",
            "GBoxed*"   : "G_TYPE_BOXED"
            }
            
        
        return

    def glib2marshaller(self, glib_type):
        res = None
        if self.__glib2marshaller.has_key(glib_type): res = self.__glib2marshaller[glib_type]
        return res

    def glib2glibtype(self, glib_type):
        res = None
        if self.__glib2glibtype.has_key(glib_type): res = self.__glib2glibtype[glib_type]
        return res

    def sci2glib(self, scitype):
        res = None
        if self.__sci2glib.has_key(scitype): res = self.__sci2glib[scitype]
        return res
        
    def sci2format(self, scitype):
        res = None
        if self.__sci2format.has_key(scitype): res = self.__sci2format[scitype]
        return res

    pass # end of class

