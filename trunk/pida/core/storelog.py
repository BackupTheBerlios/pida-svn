# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Bernard Pratz <bernard@pratz.net>

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


class logs(object):
    """
    List of all the logs
    """
    def __init__(self):
       self.logs = {}
    
    def push_record(self,key,record):
        self.logs[key] = record

    def get_top(self): ## DEBUG
        return self.logs[self.logs.keys()[len(self.logs.keys())-1]]
    top = property(get_top)

    def get_keys(self):
        return self.logs.keys()
    keys = property(get_keys)

    def get_values(self):
        return self.logs
    values = property(get_values)

    def get_iter(self):
        for log in self.logs.keys():
            yield self.logs[log]
    iter = property(get_iter)

    def filter_list(self,property,filter):
        for log in self.logs.keys():
            if hasattr(self.logs[log],property):
                if filter == getattr(self.logs[log],property):
                    yield self.logs[log]
    
