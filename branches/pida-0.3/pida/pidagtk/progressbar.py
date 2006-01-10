# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:
#Copyright (c) 2005 Bernard Pratz aka Guyzmo, guyzmo@m0g.net

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import gtk
import gobject

class progress_bar(gtk.ProgressBar):
    def __init__(self):
        '''Initializes the ProgressBar'''
        gtk.ProgressBar.__init__(self)
        self.__loop = False
        self.hide()

    def __progress_timeout(self):
        '''Internal function to update the pulse'''
        self.pulse()
        return self.__loop

    def start_pulse(self):
        '''Begins the pulse'''
        self.__loop = True
        self.timer = gobject.timeout_add (10, self.__progress_timeout)

    def show_pulse(self):
        '''Shows and begins the pulse'''
        self.show()
        self.start_pulse()

    def stop_pulse(self):
        '''Stops the pulse'''
        self.__loop = False

    def hide_pulse(self):
        '''Stops and hide the pulse'''
        self.hide()
        self.stop_pulse()

