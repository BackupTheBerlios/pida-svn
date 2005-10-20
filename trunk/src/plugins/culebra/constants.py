# -*- coding: utf-8 -*-
# Copyright 2005, Tiago Cogumbreiro <cogumbreiro@users.sf.net>
# Copyright 2005, Fernando San Martín Woerner <fsmw@gnome.org>
# $Id: edit.py 589 2005-10-14 00:14:56Z cogumbreiro $
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# This file is part of Culebra plugin.
import gtk

RESPONSE_FORWARD     = 0
RESPONSE_BACK        = 1
RESPONSE_REPLACE     = 2
RESPONSE_REPLACE_ALL = 3

KEY_ESCAPE = gtk.gdk.keyval_from_name ("Escape")
