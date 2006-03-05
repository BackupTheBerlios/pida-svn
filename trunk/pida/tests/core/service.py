# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

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

from pida.core.testing import TestCase

import pida.core.service as service
defs = service.definitions

class service_preinit(TestCase):

    def setUp(self):
        class svc(service.service_base):
            

            def cmd_foo_blah(self, foo, blah=1):
                pass

            class banana(defs.optiongroup):
                """bananadocs"""
                class colour(defs.option):
                    """colourdocs"""
                    default = 'yellow'
                    rtype = service.types.string

            class melon(defs.event):
                """I happen when something blah blah"""

            def bnd_soothsayer_see_future(self):
                """I am a binding"""

            def init(self):
                pass

            
        self.svc = svc

    def test_a_commands_exist(self):
        self.assert_(self.svc.__commands__)

    def test_b_commads_registered(self):
        ctemplate = self.svc.__commands__[0]
        self.assertEquals('cmd_foo_blah', ctemplate.func_name)
    
    def test_e_options_exist(self):
        self.assert_(self.svc.options)

    def test_f_registry_created(self):
        otemplate = self.svc.__options__

    def test_g_options_registered(self):
        otemplate = self.svc.__options__

    def test_h_options_doc_registered(self):
        otemplate = self.svc.__options__

    def test_i_option_registered(self):
        otemplate = self.svc.__options__

    def test_j_option_doc(self):
        otemplate = self.svc.__options__

    def test_k_option_default(self):
        otemplate = self.svc.__options__

    def test_l_option_type(self):
        otemplate = self.svc.__options__

    def test_m_events_exist(self):
        etemplate = self.svc.__events__
        print etemplate
        self.assert_(etemplate)
        
    def test_o_events_not_registered(self):
        etemplate = self.svc.__events__

    def test_p_events_gettable(self):
        etemplate = self.svc.__events__

    def test_q_bindings_exist(self):
        btemplate = self.svc.__bindings__
        self.assert_(btemplate)


class file_handler_preinit(TestCase):

    def setUp(self):
        import pida.core.document as document
        class svc(service.service_base):
            class file_handler(document.document_handler):
                globs = ['foo*']
                def create_buffer(self, filename):
                    print 'bcreated'
        self.svc = svc
        self.handlers = svc.__documenttypes__
        print self.handlers

    def test_a_handlers_exist(self):
        self.assert_(self.handlers)
        self.assert_(len(self.handlers))

    def test_b_handler_details(self):
        self.assertEquals(self.handlers[0].globs[0], 'foo*')

