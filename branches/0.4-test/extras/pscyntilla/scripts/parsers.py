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

import re
import models

class NotMatchedError(StandardError):
    """Raised when the given string is not matched"""

class Parser:
    groups = None
    expression = None

    def __init__(self):
        self.pattern = re.compile(self.expression)
    
    def match(self, text):
        return self.pattern.match(text)

    def extract(self, match):
        val = map(lambda name: match.group(name), self.groups)
        if len(val) == 1:
            return val[0]

        return tuple(val)

    def parse(self, text):
        match = self.match(text)
        if match is None:
            raise NotMatchedError
        return self.extract(match)

class CategoryParser(Parser):
    groups = "name",
    expression = r"^cat\s+(?P<name>\w+)"

class EnumParser(Parser):
    category = "enums"
    groups = "name", "prefix"
    expression = r"^enu\s+(?P<name>\w+)=(?P<prefix>\w*)"
    
class ConstantParser(Parser):
    category = "constants"
    groups = "name", "value"
    expression = r"^val\s+(?P<name>\w+)=(?P<value>[\-\d\w]*)"

class LexerParser(Parser):
    category = "lexers"
    groups = "name", "id", "prefix"
    expression = r"^lex\s+(?P<name>\w+)=(?P<id>\w+)\s+(?P<prefix>\w+)"

class CommentParser(Parser):
    groups = "comment",
    expression = r"^#\s*(?P<comment>.*)"

FUNCTION_EXP = (r"(?P<ret_type>\w+)\s+(?P<name>\w+)\s*"
                r"=\s*(?P<id>\d+)\s*\((?P<pars>.*,.*)\)")

class AbstractFunctionParser(Parser):

    def extract(self, match):
        pars = match.group("pars")
        couples = pars.split(",")
        formal_pars = map(lambda foo: foo.split(), couples)

        return models.Function(match.group("name"), match.group("ret_type"),
                               formal_pars, match.group("id"))

class FunctionParser(AbstractFunctionParser):
    category = "functions"
    expression = r"^fun\s+%s" % FUNCTION_EXP

class GetterParser(AbstractFunctionParser):
    category = "getters"
    expression = r"^get\s+%s" % FUNCTION_EXP

class SetterParser(AbstractFunctionParser):
    category = "setters"
    expression = r"^set\s+%s" % FUNCTION_EXP

class SignalParser(AbstractFunctionParser):
    category = "signals"
    expression = (r"^evt\s+(?P<ret_type>\w+)\s+(?P<name>\w+)\s*="
                  r"\s*(?P<id>\d+)\s*\((?P<pars>.*)\)")


class IFaceParser:
    parsers = (
        FunctionParser(), GetterParser(), SetterParser(), EnumParser(),
        ConstantParser(), SignalParser(), LexerParser()
    )

    def is_empty_comment(self, str):
        """Returns true if str is a not useful comment or an empty line, false otherwise"""
        stripped = str.strip()
        return (stripped == "") or (stripped[0:2] == "##")


DEC_PATT = re.compile(r"#define\s+([A-Z][A-Z0-9_]*)\s+([0-9]+)")
HEX_PATT = re.compile(r"#define\s+([A-Z][A-Z0-9_]*)\s+(0[xX][0-9]+)")
def extract_constants(line):
    val = DEC_PATT.search(line)
    if val is not None:
        name, val = val.groups()
        return name, int(val)
        
    val = HEX_PATT.search(line)
    if val is not None:
        name, val = val.groups()
        val = int(val[2:], 16)
        return name, val

def iter_header_constants(buff):
    """Accepts a file like object and iterates over it to extract the constants
    """
    for line in buff.readlines():
        vals = extract_constants(line)
        if vals is not None:
            yield vals

# 209