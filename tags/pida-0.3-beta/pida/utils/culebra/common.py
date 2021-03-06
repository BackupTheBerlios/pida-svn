__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__doc__ = """This module contains constants and utility functions
that are shared amongst many modules.
"""

import gtk
import weakref

#############
# Constants
(
RESPONSE_FORWARD,
RESPONSE_BACK,
RESPONSE_REPLACE,
RESPONSE_REPLACE_ALL,
) = range(4)

KEY_ESCAPE = gtk.gdk.keyval_from_name("Escape")

###############
# Actual code

class ChildObject(object):
    def __init__(self, parent):
        self.__parent = weakref.ref(parent)
    
    def get_parent(self):
        return self.__parent()


def escape_text(txt):
    return txt.replace("\t", "¬").replace("\n", "¶")


def unescape_text(txt):
    return txt.replace("¬", "\t").replace("¶", "\n")


