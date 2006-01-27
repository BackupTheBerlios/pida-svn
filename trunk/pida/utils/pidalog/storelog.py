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

import time
import os

from logging import _levelNames as level_names

class stream_handler(object):
    def __init__(self, stream=None):
        if not stream:
            stream = sys.stderr
        self.stream = stream
        self.level = None

    def flush(self):
        self.stream.flush()

    def set_level(self, level, type='='):
        self.level = level
        self.level_type = type
        self.stream.write("%s pIDA (PID %s) logging on %s started.\n" % (
                                        time.strftime("%Y/%m/%d %H:%M:%S"),
                                      os.getpid(),level_names[self.level]))

    def __level_is_valid(self,record):
        if self.level is not None:
            if self.level_type is '=':
                if record.levelno is self.level:
                    return True
            elif self.level_type is '+':
                if record.levelno > self.level:
                    return True
            elif self.level_type is '-':
                if record.levelno < self.level:
                    return True
        return False

    def emit(self, record):
        if self.__level_is_valid(record):
            msg = record.getMessage()
            self.stream.write("%s %s %s:%s %s\n" % (
                time.strftime("%Y/%m/%d %H:%M:%S", \
                                             time.localtime(record.created)),
                record.module, record.name, record.lineno, msg))
            self.stream.flush()

    def close(self):
        pass

class file_handler(stream_handler):
    def __init__(self, filename, mode='a'):
        stream = open(filename, mode)
        stream_handler.__init__(self,stream)
        self.base_filename = os.path.abspath(filename)
        self.mode = mode

    def close(self):
        """
        Closes the stream
        """
        self.flush()
        self.stream.close()

class rotating_file_handler(file_handler):
    def __init__(self,filename,mode='a',max_bytes=0,backup_count=0):
        if max_bytes > 0:
            mode = 'a'
        file_handler.__init__(self,filename,mode)
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def emit(self, record):
        if self.should_rollover(record):
            self.rollover()
        file_handler.emit(self,record)

    def rollover(self):
        self.stream.close()
        if self.backup_count > 0:
            for i in range(self.backup_count -1, 0, -1):
                sfn = "%s.%d" % (self.base_filename, i)
                dfn = "%s.%d" % (self.base_filename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.base_filename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.base_filename, dfn)
        self.stream = open(self.base_filename, 'w')
            
    def should_rollover(self, record):
        if self.max_bytes > 0:
            msg = "%s\n" % record.getMessage()
            self.stream.seek(0,2)
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return True
        return False

class logs(object):
    """
    List of all the logs
    """
    def __init__(self,path=None):
       self.logs = {}
       self.__stream = []
       self.__last = None
       if path:
            self.__log_path = path
            for level in (10,20,30,40,50):
                if isinstance(level,int):
                    self.open_stream('%s/%s.log' % (path, \
                                       level_names[level].lower()), level, '=')

    def open_stream(self,file=None,level=None,level_type=None):
        if file is None:
            handler = stream_handler()
        else:
            handler = rotating_file_handler(file,max_bytes=102400,backup_count=3)
        if level is not None:
            handler.set_level(level,level_type)
        # first get all stored logs
        for log in self.logs:
            handler.emit(log)
        # second get all emitted log
        self.__stream.append(handler)

    def __log_buffer_rotate(self):
        if len(self.logs) > 100:
            self.logs = {}
    
    def push_record(self,key,record):
        self.__log_buffer_rotate()
        self.logs[key] = record
        self.__last = record
        for stream in self.__stream:
            stream.emit(record)

    def get_last(self):
        return self.__last
    last = property(get_last)

    def get_keys(self):
        return self.logs.keys()
    keys = property(get_keys)

    def get_values(self):
        return self.logs
    values = property(get_values)

    def __iter__(self):
        for log in self.logs.keys():
            yield self.logs[log]

    def get_iter(self):
        for log in self.logs.keys():
            yield self.logs[log]
    iter = property(get_iter)

    def filter_list(self,property,filter):
        for log in self.logs.keys():
            if hasattr(self.logs[log],property):
                if filter == getattr(self.logs[log],property):
                    yield self.logs[log]
                elif isinstance(filter,list):
                    for f in filter:
                        if f == getattr(self.logs[log],property):
                            yield self.logs[log]

