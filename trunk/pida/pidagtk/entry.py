# -*- coding: utf-8 -*- 
        
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Bernard Pratz <guyzmo@m0g.net>
    
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

class completed_entry(gtk.Entry):
     def __init__(self):
         gtk.Entry.__init__(self)
         self.comp_list = []
         completion = gtk.EntryCompletion()
         completion.set_match_func(self.match_func)
         completion.connect("match-selected",
                             self.on_completion_match)
         completion.set_model(gtk.ListStore(str))
         completion.set_text_column(0)
         self.set_completion(completion)

     def match_func(self, completion, key, iter):
         model = completion.get_model()
         return model[iter][0].startswith(self.get_text())
     
     def on_completion_match(self, completion, model, iter):
         self.set_text(model[iter][0])
         self.set_position(-1)
     
     def add_words(self, words):
         model = self.get_completion().get_model()
         for word in words:
            if not word in self.comp_list:
                model.append([word])
                self.comp_list.append(word)

