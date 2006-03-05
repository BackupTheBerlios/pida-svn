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

import re

class IFaceParser:

    def __init__(self):
        """Sets up a set of structure to be used later by methods"""

        # good comment:
        com_reg = r"^#\s*(?P<comment>.*)"
        self.com_re = re.compile(com_reg)

        # category:
        cat_reg = r"^cat\s+(?P<name>\w+)"
        self.cat_re = re.compile(cat_reg)

        # functions:
        function_str = r"(?P<ret_type>\w+)\s+(?P<name>\w+)\s*=\s*(?P<id>\d+)\s*\((?P<pars>.*,.*)\)"
        fun_reg = r"^fun\s+%s" % function_str
        self.fun_re = re.compile(fun_reg)
        get_reg = r"^get\s+%s" % function_str
        self.get_re = re.compile(get_reg)
        set_reg = r"^set\s+%s" % function_str
        self.set_re = re.compile(set_reg)

        evt_str = r"(?P<ret_type>\w+)\s+(?P<name>\w+)\s*=\s*(?P<id>\d+)\s*\((?P<pars>.*)\)"
        evt_reg = r"^evt\s+%s" % evt_str
        self.evt_re = re.compile(evt_reg)

        # enu:
        enu_reg = r"^enu\s+(?P<name>\w+)=(?P<prefix>\w*)"
        self.enu_re = re.compile(enu_reg)

        # val:
        val_reg = r"^val\s+(?P<name>\w+)=(?P<value>[\-\d\w]*)"
        self.val_re = re.compile(val_reg)

        # lex:
        lex_reg = r"^lex\s+(?P<name>\w+)=(?P<id>\w+)\s+(?P<prefix>\w+)"
        self.lex_re = re.compile(lex_reg)

        return

    def match_get(self, str):
        """Returns a matched re object is str contains get definition, None otherwise"""
        return self.get_re.match(str)

    def match_set(self, str):
        """Returns a matched re object is str contains set definition, None otherwise"""
        return self.set_re.match(str)

    def match_fun(self, str):
        """Returns a matched re object is str contains fun definition, None otherwise"""
        return self.fun_re.match(str)

    def match_evt(self, str):
        """Returns a matched re object is str contains fun definition, None otherwise"""
        return self.evt_re.match(str)

    def match_enu(self, str):
        """Returns a matched re object is str contains an enu definition, None otherwise"""
        return self.enu_re.match(str)

    def match_val(self, str):
        """Returns a matched re object is str contains an enu definition, None otherwise"""
        return self.val_re.match(str)

    def match_com(self, str):
        """Returns a matched re object is str contains an comment, None otherwise"""
        return self.com_re.match(str)

    def match_lex(self, str):
        """Returns a matched re object is str contains an enu definition, None otherwise"""
        return self.lex_re.match(str)

    def match_cat(self, str):
        """Returns a matched re object is str contains an enu definition, None otherwise"""
        return self.cat_re.match(str)
    
    def is_empty_comment(self, str):
        """Returns true if str is a not useful comment or an empty line, false otherwise"""
        stripped = str.strip()
        return (stripped == "") or (stripped[0:2] == "##")

    def extract_function(self, match):
        """Returns (name, ret_type, [(formal_type, formal_name), ...], id).
        match is the already matched re object"""

        formal_pars = []
        pars = match.group("pars")
        couples = pars.split(",")
        for couple in couples:
            formal_pars.append(couple.split())
            pass

        return match.group("name"), match.group("ret_type"), formal_pars, match.group("id")

    def extract_cat(self, match):
        """Returns (name, prefix)"""
        return match.group("name")

    def extract_com(self, match):
        """Returns (name, prefix)"""
        return match.group("comment")

    def extract_enu(self, match):
        """Returns (name, value)"""
        return match.group("name"), match.group("prefix")

    def extract_val(self, match):
        """Returns (name, value)"""
        return match.group("name"), match.group("value")


    def extract_evt(self, match):
        """Returns (name, ret_type, [(formal_type, formal_name), ...], id)"""
        return self.extract_function(match)

    def extract_lex(self, match):
        """Returns (name, id, prefix)"""
        return match.group("name"), match.group("id"), match.group("prefix")

    
    pass # end of class
