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

""" Script to create new PIDA modules from the templates. """

import os
import sys
import time

def create_file(modulename, authorname, authoremail):
    """
    Create the file from the templates and the given parameters
    """
    scripts_directory = os.path.split(__file__)[0]
    template_directory = os.path.join(os.path.split(scripts_directory)[0],
                                  'templates')
    encoding_f = open(os.path.join(template_directory, 'encoding.txt'), 'r')
    modeline_f = open(os.path.join(template_directory, 'modeline.txt'), 'r')
    license_f = open(os.path.join(template_directory, 'license.txt'), 'r')
    
    license = license_f.read() % {'year':time.strftime('%Y'),
                                  'name':authorname,
                                  'email':authoremail}
    license_f.close()
    modeline = modeline_f.read().strip()
    modeline_f.close()
    encoding = encoding_f.read()
    encoding_f.close()

    outfile = open('%s.py' % modulename, 'w')
    outfile.write('\n'.join([encoding, modeline, license]))
    outfile.close()

def get_module_details():
    """
    Get the module details from the user.
    """
    modulename = raw_input('Enter the module name: ').strip()
    if not modulename:
        raise Exception, 'Must enter a module name.'
    authorname = raw_input('Enter your name: ').strip()
    if not authorname:
        authorname = 'The PIDA Project'
    authoremail = raw_input('Enter your email address: ')
    if not authoremail:
        authoremail = ''
    return modulename, authorname, authoremail

if __name__ == '__main__':
    create_file(*get_module_details())
