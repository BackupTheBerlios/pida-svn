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

class entry_multi_completion(gtk.Entry):
    def __init__(self):
        gtk.Entry.__init__(self)
        self.completion = gtk.EntryCompletion()
        # customize the matching function to match multiple space
        # separated words
        self.completion.set_match_func(self.match_func, None)
        # handle the match-selected signal, raised when a completion
        # is selected from the popup
        self.completion.connect('match-selected', self.on_completion_match)
        self.set_completion(self.completion)
    
    def match_func(self, completion, key_string, iter, data):
        model = self.completion.get_model()
        # get the completion strings
        modelstr = model[iter][0]
        # check if the user has typed in a space char,
        # get the last word and check if it matches something
        if " " in key_string:
            last_word = key_string.split()[-1]
            return modelstr.startswith(last_word)
        # we have only one word typed
        return modelstr.startswith(key_string)
    
    def on_completion_match(self, completion, model, iter):
        current_text = self.get_text()
        # if more than a word has been typed, we throw away the
        # last one because we want to replace it with the matching word
        # note: the user may have typed only a part of the entire word
        #       and so this step is necessary
        if " " in current_text:
            current_text = " ".join(current_text.split()[:-1])
        # add the matching word
        current_text = "%s %s" % (current_text, model[iter][0])
    
        # set back the whole text
        self.set_text(current_text)
        # move the cursor at the end
        self.set_position(-1)
    
        # stop the event propagation
        return True

