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

from parsers import IFaceParser

class IFace:

    def __init__(self, filename):
        self.parser = IFaceParser()

        self.filename = filename

        self.groups = (
            ('functions', self.parser.match_fun, self.parser.extract_function),
            ('getters', self.parser.match_get, self.parser.extract_function),
            ('setters', self.parser.match_set, self.parser.extract_function),
            ('enums', self.parser.match_enu, self.parser.extract_enu),
            ('constants', self.parser.match_val, self.parser.extract_val),
            ('signals', self.parser.match_evt, self.parser.extract_evt),
            ('lexers', self.parser.match_lex, self.parser.extract_lex) )

        self.current_cat = ""
        self.categories = {}

        self.current_comment = ""

        self.set_category("Basics")
        self.__parse_iface()
        return


    def set_category(self, name):
        self.current_cat = name
        if not self.categories.has_key(name):
            self.categories[name] = {}
            for group in self.groups:
                self.categories[name][group[0]] = []
                pass
            pass
        return


    def add_to_category(self, what, values):
        defs = self.categories[self.current_cat][what]
        defs.append((values, self.current_comment))
        return


    def get_categories(self):
        return self.categories


    def is_deprecated(self, cat):
        """returns true if given category is deprecated"""
        return cat.lower() == "deprecated"
    
    def __parse_iface(self):
        iface_f = open(self.filename, "r")
        
        line = iface_f.readline()
        while (line):
            str = line.rstrip()
            # empty line or unuseful comments:
            if self.parser.is_empty_comment(str):
                # resets the current useful comment
                self.current_comment = ""
                line = iface_f.readline()
                continue

            # useful comments:
            m = self.parser.match_com(str)
            if m:
                com = self.parser.extract_com(m)
                if self.current_comment == "": self.current_comment = com
                else: self.current_comment += "\n%s" % com
                line = iface_f.readline()
                continue
                

            # categories:
            m = self.parser.match_cat(str)
            if m:
                value = self.parser.extract_cat(m)
                self.set_category(value)
                line = iface_f.readline()
                continue

            for group in self.groups:
                m = group[1](str)  # Calls the matcher
                if m:
                    value = group[2](m) # Extract the value(s)
                    self.add_to_category(group[0], value)
                    pass
                pass

            line = iface_f.readline()
            pass # while loop
        
        return

    pass # end of class
