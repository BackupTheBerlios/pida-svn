#!/usr/local/bin/python
""" Program to perform a grep on files, by Hugh Sasse. 

    This is a context grep program which will descend into
    directories if required, and supress unprintable characters.
    The module holds classes:
    Pygrep:
	This does the searching of files, and returns
        exit codes as appropriate.  It also produces
	results in self.results which can be handled
	with methods of the Pygrep_results class.
    Pygrep_results:
	This is a dictionary of matching files with the
	lines that match.  The methods it supports are
	for combining search results in various ways
	beyond the functionality of the Pygrep class.

    Author: Hugh Sasse
    Institution: De Montfort University, Leicester UK

    You may use this software and modify it for your own
    needs, and redistribute it freely, but you may not 
    claim that your wrote it.  Enhancements would be
    welcomed.  Andrew Kuchling <amk@magnet.com> has 
    already suggested a huge speedup. Many thanks to him.
"""

import sys	# for file i/o etc
import string	# for character translations, etc
import re	# for regular expression matching etc.
import getopt	# for argument processing.
import os	# for handling the files and dirs
import glob	# In case we get * or ? or [..]
import stat	# for finding out what a file is.
from UserDict import UserDict
		# for the base class of Pygrep_results

# globchars that may be used in a glob style match.
globchars = re.compile(r'[\!\*\?\[\]]')

# global functions to wrap up the stat functions.

def is_dir(file):
    """Test if filespec is a directory
    """
    mystat=os.stat(file)
    mymode=mystat[stat.ST_MODE]
    return stat.S_ISDIR(mymode)

def is_reg_file(file):
    """Test if filespec is a regular file
    """
    mystat=os.stat(file)
    mymode=mystat[stat.ST_MODE]
    return stat.S_ISREG(mymode)


def is_link(file):
    """Test if filespec is a symbolic link
    """
    mystat=os.lstat(file)
    mymode=mystat[stat.ST_MODE]
    return stat.S_ISLNK(mymode)

class Pygrep_err(Exception):
    """ Exceptions raised by the pygrep class
    """
    pass;

class Pygrep_results(UserDict):
    """ results of a call to pygrep.pygrep

        the results clsass is a dicitionary of filespecs
        which are strings, and the entries in each is a
	list of matching line numbers.  This class extends
	the dictionary class to allow setwise combination
	of results.
    """

    # We can use the dictionary methods for most things.



    def __init__(self, value=None):
        UserDict.__init__(self)
        if value != None:
            for key in value.keys():
                self[key] = value[key][:]
        return None

    def __or__(self, other):
        """ OR two pygrep_results together: a | b

            NOTE this is bot a bitwise or. It is a 
	    file by file,and then line by line or.
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if other.has_key(key):
                if len(other[key]) > 0:
		    newlist = []
		    mylist = self[key] + other[key]
		    for i in range(len(mylist)):
			if (not mylist[i] in mylist[i+1:]):
			    newlist.append(mylist[i])
		    new[key] = newlist[:]
            else:
                new[key] = self[key][:]
        for key in other.keys():
            if not self.has_key(key):	# because already copied
                if len(other[key]) > 0:
		    new[key] = other[key][:]
        for key in new.keys():
            new[key].sort()
        return new


    def __add__(self, other):
        """ Add two pygrep_results together: a + b

            This is the same as an or, because of the
            way they are merged.
        """

        new = self | other
        return new

    def __and__(self, other):
        """ AND two pygrep_results together: a & b

            Only files which both have some lines 
            that match will be retained. This is not
	    a line by line AND, because that can be
	    done with the pygrep method's -j option, 
	    and we need a filewise AND somewhere. It
	    can also be done with a * (__mul__).
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if other.has_key(key):
                # OR the actual lines together.
                newlist = []
                mylist = self[key] + other[key]
		for i in range(len(mylist)):
		    if (not mylist[i] in mylist[i+1:]):
			newlist.append(mylist[i])
                new[key] = newlist[:]
        for key in new.keys():
	     new[key].sort()
        return new


    def __xor__(self, other):
        """ XOR two pygrep_results together: a ^ b

            this is a filewise XOR. A line by line XOR
            can be done with (A * B) % B.
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if not other.has_key(key):
                new[key] = self[key][:]
        for key in keys(other):
            if not self.has_key(key):
                new[key] = self[key][:]
        for key in new.keys():
	    new[key].sort()
        return new

    def __mul__(self, other):
        """ linewise AND two Pygrep_results together: a * b

            Only lines which are in  both 
            self and other will be  retained. This is
            basically the same as -j option to the
	    pygrep method.
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if other.has_key(key):
                # OR the actual lines together.
                newlist = []
		for i in self[key]:
		    if i in other[key]:
			newlist.append(i)
                new[key] = newlist[:]
        for key in new.keys():
            new[key].sort()
        return new


    def __mod__(self, other):
        """ remove other's lines from self : a - b

            Only lines which are in self but not in 
            other will remain.   This is not a
	    commutative operation.
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if other.has_key(key):
                # subtract  the actual lines....
                newlist = []
		for i in self[key]:
		    if not (i in other[key]):
			newlist.append(i)
                new[key] = newlist[:]
            else:
                new[key] = self[key][:]
        for key in new.keys():
            new[key].sort()
        return new



    def __sub__(self, other):
        """ remove files matching  other from self : a - b

            Only files which are in self but not in 
            other will remain.   This is not a
	    commutative operation. '-' was used because
	    this is what most people mean by subtracting
	    results.
        """

        new = Pygrep_results()	# a new dictionary for the results.
        for key in self.keys():
            if not other.has_key(key):
                new[key] = self[key][:]
        for key in new.keys():
            new[key].sort()
        return new

    def display(self):
        """display the set of results in some generic form

           This displays the lines in the files, with the
	   line numbers.  When context searching is in use
	   the results may be a bit odd if lines of one
	   file are knocked out by combining with another.
        """
        for file in self.keys():
            try:
                fp = open(file)
		lines = fp.readlines()
                fp.close()
            except IOError:
                sys.stderr.write("pygrep: Unable to open %s for reading\n" % file)
            for line in self[file]:
                print "%s:%d:%s" % file, line, lines[line - 1]
        pass

# test the class and bomb out
def test_Pygrep_results():
    print "In test_Pygrep_results()..."
    results = Pygrep_results()
    print "results is ",results

    results = Pygrep_results({"This":[1,2,3], "That":[4,5,6]})
    print "results is ",results

    results2 = Pygrep_results({"That":[4,5,7]})
    print "results2 is ",results2

    results3 = results * results2
    print "results3 is ",results3

    results4 = results & results2
    print "results4 is ",results4

    results5 = results2 & results
    print "results5 is ",results5

    results6 = results | results2
    print "results6 is ",results6

    results7 = results | results2
    print "results7 is ",results7

    results8 = results - results2
    print "results8 is ",results8

    results9 = results2 - results
    print "results9 is ",results9

    results10 = results % results2
    print "results10 is ",results10

    results11 = results2 % results
    print "results11 is ",results11

    results12 = results + results2
    print "results12 is ",results12

    results13 = results2 + results
    print "results13 is ",results13

    print "Leaving test_Pygrep_results()..."
    return None


class Pygrep:
    """grep files using Perl REs.

       This takes a list of args in the same way as
       the program does, and sorts out what do do
       with getopt...
    """

    # We need to know what constitutes control chars of 
    # the sort that won't appear in a text file.  For this
    # reason backspace, del, formfeed and vertical tab are
    # removed.  These were handled by regular expression
    # substitutions, but Andrew Kuchling <amk@magnet.com>
    # suggested I change them tu use string.translate.
    # This was a huge speedup, so Thank You, Andrew.

    control_chars = string.join(map(chr, range(0,011) + [013,014] + range(016,040)),"")

    # Characters with the hi bit set can cause problems, so
    # we may wish to knock them out.
    hi_bit_chars = string.join(map(chr, range(0200,0400)),"")
    # print "hi_bit_chars is",len(hi_bit_chars),"characters long"

    binary_re = re.compile(r'[\000-\010\013\014\016-\037\200-\377]')
    # now we need a table to map [\200-\377] to [\000-\177]
    # Remember range(a,b) gives [a,...b-1]
    table = range(0,128) * 2
    # convert to a string.
    hi_lo_table = string.join(map(chr,table),"")
    # print "hi_lo_table is",len(hi_lo_table),"characters long"

    all_chars = string.join(map(chr,range(0,256)),"")
    # print "all_chars is",len(all_chars),"characters long"


    def __init__(self):
        """ Initilise the flags etc 
        """
        self.a_flag = self.A_flag =  self.B_flag = \
         self.c_flag = self.C_flag = self.d_flag = self.D_flag = \
         self.E_flag = self.F_flag = \
         self.h_flag = self.H_flag = self.i_flag = self.I_flag = self.l_flag = \
         self.n_flag = self.R_flag = self.s_flag = self.S_flag = \
         self.v_flag = self.V_flag  = 0 

        self.and_flag = 0;
        self.patterns = []
        self.cpatterns = [];	# compiled patterns
        self.patfiles = []
        self.files = []
        self.status = 0		# the exit status
        self.show_dashes = 0
        self.show_names = 0
        self.show_number = 0
        self.line_count = 0
        self.results = Pygrep_results()


    def set_options(self, optlist):
        """Given a list of options, set the flags.

           The flags are set to 1 if they are boolean,
           or to the supplied value.  If the help flags
           are used then the usage proc is called and
           this funtion exits, returning 1, so you
	   can tell if this has happened.
        """
 
        for option, value in optlist:
            if option == '-a':
                self.a_flag = 1
            elif option == '-A':
                self.A_flag = 1
            elif option == '-B':
                self.B_flag = 1
            elif (option == '-c') or (option == "--count"):
                self.c_flag = 1
            elif (option == '-C') or (option == "--Context"):
                self.C_flag = string.atoi(value);
            elif option == '-d':
                self.d_flag = 1
            elif option == '-D':
                self.D_flag = 1
            elif option == '-e':
                self.patterns.append(value)
            elif option == '-E':
                self.E_flag = 1
            elif option == '-f':
                self.patfiles.append(value)
            elif option == '-F':
                self.F_flag = 1
            elif (option == '-h') or (option == "--head"):
                self.h_flag = 1
            elif (option == '-H') or (option == '--help'):
                self.usage()
                ### maybe raise exception??
                return 1
            elif option == '-i':
                self.i_flag = 1
            elif option == '-I':
                self.I_flag = 1
            elif (option == '-j') or (option == "--and"):
                self.and_flag = 1
            elif option == "--or":	# has no short form
                self.and_flag = 0
            elif option == '-l':
                self.l_flag = 1
            elif option == '-n':
                self.n_flag = 1
            elif option == '-R':
                self.R_flag = 1
            elif option == '-s':
                self.s_flag = 1
            elif option == '-S':
                self.S_flag = 1
            elif (option == '-v') or (option == "--invert"):
                self.v_flag = 1
            elif (option == '-V') or (option == "--version"):
                self.V_flag = 1
                print "pygrep version 1.5"
                return 1
        return 0
         

    def match_patterns(self, str):
        """ peform a map on the patterns to match string

            Actually use search as its results are more useful
        """

        if self.i_flag:
	    str = string.lower(str)

        if self.F_flag:	# fixed strings, no patterns
	    patterns = self.patterns
	    result = map(lambda x,y=str : (string.find(y,x)>-1), patterns)
        else:
	    cpatterns = self.cpatterns
	    result = map(lambda x,y=str : x.search(y), cpatterns)

        return result


    def or_matches_together(self, matchlist):
        """ Given a list of matches, say if any matched
        """
        result = reduce( lambda x,y: x or y, matchlist,0)
        return result


    def and_matches_together(self, matchlist):
        """ Given a list of matches, say if all matched
        """
        result = reduce( lambda x,y: x and y, matchlist,1)
        return result


    def find_context(self, indices, maxind ):
        """ add lines 'in context' to a list of line numbers

            Work out the surrounding context of each listed
            line, and deal with overlaps and start/end of 
            the file.  maxind is the last possible line.
        """
        if (self.C_flag % 2): 	# if it is odd
	    context = self.C_flag - 1
        else:
	    context = self.C_flag
        half_context = context / 2
        start = []
        end = []
        for i in indices:
            startpos = i - half_context
            if startpos < 1:
                start.append(1)
            else:
                start.append(startpos)
            endpos = i + half_context
            if endpos > maxind:
                end.append(maxind)
            else:
                end.append(endpos)

        # merge the start and end lists into one long
	# list with lots of redundancy.

        temp = []
        for i in range(len(start)):
            temp = temp + range(start[i],end[i]+1)

        results = []
        for i in range(len(temp)):
            # print "i is ",i,"temp[i] is ", temp[i]
            if (not temp[i] in temp[i+1:]):
                results.append(temp[i])
                # print temp[i], " not in ", temp[i+1:]
          # else:
          #     print temp[i]," in ", temp[i+1:]

        return results



    def expand_files(self):
        """ Expand a list of supplied files.

	    This does globbing, expanding directories
	    recursively, and checking for files that
	    are not regular files.
        """
        start = 0;
        while (start < len(self.files)):
	    for f in range(start, len(self.files)):
		file = self.files[f]
		if file == "-":	# this is stdin
                    start = start + 1
		    continue

		if globchars.search(file) != None:
		    self.files = self.files + glob.glob(file)
                    self.files[f:f+1] = []
		    break # reprocess the new list
                if is_link(file):
                    ostart = start
                    try:
                        if is_reg_file(file):
                            start = start + 1
                        else:
		  	    self.files[f:f+1] = []
                    except os.error:
			if not self.E_flag:
			    sys.stderr.write("pygrep: %s is a link to a missing file or directory\n" % file)
			if not self.S_flag:
			    self.status = 2
                        self.files[f:f+1] = []
                    if (start == ostart):
                       break
                    else:
		       continue
		if is_dir(file):
		    if self.R_flag:
			contents = os.listdir(file)
			# print "contents is ", contents, "\n"
			contents = map(lambda x,f=file: f + os.sep +x, contents)
			# print "contents is ", contents, "\n"
			self.files = self.files + contents
		    else:
			if not self.E_flag:
			    sys.stderr.write("pygrep: %s is a directory. Use -R for recorsion\n" % file)
			if not self.S_flag:
			    self.status = 2
		    self.files[f:f+1] = []
		    break
		if not is_reg_file(file):
		    if not self.E_flag:
			sys.stderr.write("pygrep: %s is not a regular file\n" % file)
		    if not self.S_flag:
			self.status = 2
		    self.files[f:f+1] = []
		    break
                start = start + 1
       


    def pygrep(self, args):
        """Do the actual grepping based on the supplied
           arguments.
        """
        optlist, self.files = getopt.getopt(args,
	 "aABcC:dDe:Ef:FhHiIjlnRsSvV", ["and", "context",
         "count", "head", "help", "invert", "or", "version"])

        # print "optlist is ", optlist
        # print "files is ", self.files

        if self.set_options(optlist):
            # true if Usage is called or version requested.
            return 0

        # Now read the patterns in the patfiles if any
	# into tee pattern list.
        for file in self.patfiles:
            fp = sys.open(file)
            lines = fp.readlines()
            fp.close()
            lines = map(lambda x:re.sub(r'\n$',"",x), lines)
            self.patterns.append(lines)

        if len(self.patterns) == 0:
            # we have no patterns in the option list
            # so the first "file" must be a pattern
            if len(self.files) > 0:
		self.patterns.append(self.files[0])
		self.files = self.files[1:]
            else:
                sys.stderr.write("pygrep: No pattern supplied\n")
                self.usage()
                raise Pygrep_err, "No pattern supplied"

        # We now have a complete list of the patterns.
        # Searching for regular expressions is more expensive
	# than searching for strings.  If our patterns
	# contain no metacharacters then we can use string
	# searches instead.
        if not filter(lambda x: re.match(r'[^\w\s]',x),
                   self.patterns):
            # nothing like a metachar found here...
            self.F_flag = 1


        if len(self.files) == 0:
            self.files = ["-"]	#read from stdin if no files.

        # expand the list of files -- expand directories
        # to contents, globs to groups of files, etc
        self.expand_files()


        # If we are using fixed patterns we don't need to
	# compile the regexps.
	if self.F_flag:
	    if self.i_flag:
                # If case insensitive make it all lower case.
		self.patterns = map(lambda x:string.lower(x),self.patterns)
	else:	# not fixed patterns
	    if self.i_flag:
		self.cpatterns = map(re.compile, self.patterns);
            else:
		self.cpatterns = map(lambda x:re.compile(x,re.I), self.patterns);

        if self.l_flag:
            self.show_names = 1
        else:
	    if (len(self.files) > 1) or (self.R_flag):
                self.show_names = 1
            if self.C_flag:
                self.show_dashes = 1
	    if self.n_flag:
	        self.show_number = 1
            if self.D_flag:
                self.show_dashes = 0


	# Now get down and do the grepping!

        for file in self.files:
            lines = []
            try:
                if file == "-":
                    lines = sys.stdin.readlines()
                else:
		    fp = open(file)
		    lines = fp.readlines()
		    fp.close()
            except IOError:
                if not self.E_flag:
                    sys.stderr.write("pygrep: Unable to read %s\n" % file)
                if not self.S_flag:
                    self.status = 2
                continue	# try the next file.


	    # filter out characters we don't want to
            # display .
            # first deal with the high bit chars...
            if not (self.a_flag or self.A_flag):
                lines = map(lambda x,y=self : string.translate(x, y.all_chars, y.hi_bit_chars), lines)

            if self.A_flag:
                lines = map(lambda x,y=self: string.translate(x, y.hi_lo_table),lines)

            if self.I_flag:
                found = 0
                x = 0;
                while (not(found) and (x < len(lines))):
		    if self.binary_re.match(lines[x]):
			found = 1
			break 
                    x = x + 1
                if found:
                    continue # with next file
                   

            if not self.B_flag:
                lines = map(lambda x,y=self : string.translate(x, y.all_chars, y.control_chars), lines)

            # now match the patterns agains the lines.

            # print file, ":len(lines) = ", len(lines)

            if self.and_flag: # and the patterns together
		indices = \
		    map(lambda x,y=self,z=lines:	# for each index...
			 (
			     y.and_matches_together(
				 y.match_patterns(z[x])
			     )
			 ) and (x+1),
			range(len(lines))
		       )
            else: # or the patterns together.
		indices = \
		    map(lambda x,y=self,z=lines:	# for each index...
			 (
			     y.or_matches_together(
				 y.match_patterns(z[x])
			     )
			 ) and (x+1),
			range(len(lines))
		       )
            # print file,":len(indices) matched  = ", len(indices)
            # print "indices = ", indices
            indices = filter(None, indices)

            # print file,":len(indices) filtered = ", len(indices)
            # print "indices = ", indices

            if self.v_flag:	# invert the logic
                indices = map(lambda x,y=indices:
                                 (((x+1) not in y) or None) and (x+1),
                                 # the or is to make Not return None
                                 range(len(lines))
                             )
                indices = filter(None, indices)

            # print file, ":len(indices) inverted = ", len(indices)

            if (len(indices)>0):
                self.status = 1
                if self.C_flag:
		   indices = self.find_context(indices,len(lines))

	    # Now save the results in the variable.
            new_results = Pygrep_results({file:indices})
            self.results = self.results + new_results

	    # we are now ready to print out the results
	    # for this file.
            return
            if not self.s_flag: 	#silent
                if (len(indices) == 0):
		    if self.d_flag:
			print file
                else:		# len(indices) > 0
                    if self.d_flag:
                        continue # with next file
		    if self.l_flag:
			print file
                    elif self.c_flag:
                        if self.show_names:
			    print "%s:%d" % (file, len(indices))
                        else:
			    print "%d" % len(indices)
                        self.line_count = self.line_count + len(indices)
		    else:
		       if self.show_dashes:
			   print "---"
		       for i in range(len(indices)-1):
			   if self.show_names:
			       print "%s:" % file,
			   if self.show_number:
			       print "%d:" % indices[i],
			   print lines[indices[i]-1],
			   if (indices[i]+1 != indices[i+1]) and self.show_dashes:
			       print "---"
		       if self.show_names:
			   print "%s:" % file,
		       if self.show_number:
			   print "%d:" % indices[-1],
		       print lines[indices[-1]-1],
		       if self.show_dashes:
			   print "---"
        return
        if not self.s_flag:
            if self.c_flag:
                print "total = ",self.line_count

        return self.status


                   
    def usage(self):
        """Explain how to use the pygrep utility

           This sends the explanation to the standard
           error stream because it may be called in the
           event of an error.
        """
        sys.stderr.write( """
usage grep [-BcdEFhHilnRsSvV] [-C context]
          {-e pattern}|pattern|{-f patfile} path [ path ...]

where these terms have the following meanings:
options:
-a		allow 8 bit characters through. Normally filtered out.
-A		collapse 8-bit to 7-bit ASCII. Implies -a.
-B		allow Binary files through unfiltered.
		Normally control chars are filtered out.
		Characters with the high bit set may not be
		extended ASCII, so this option DOES NOT
		imply -a.
-c		Only count lines
-C count	lines of context to show. An odd number
		includes the line, even excludes it.
-d		list only names of files that Don't have
		matching lines
-D		Don't Display Dashes between matching
		segments
-e pattern	match this pattern
-E		suppress error messages
-f patfile	file of patterns to match, 1 per line
-F 		Act as fgrep -- treat metachars as normal characters
-h		don't put names at start of the lines
-H		Give this help message
-i		ignore case in matches
-I		completely Ignore files containing binary
		characters (control chars). Takes account
		of -a and -A flags
-j		match lines using conJunction (AND) of
                patterns: lines match if all the patterns
		match. The default is disjunction (OR):
		lines match if any patterns match.
-l		list only names of files with matching lines
-n		include the linenumber in the outppt
-R		descend into directories Recursively.
-s		silent, don't write lines or filenames to output,
		just set the status.
-S		suppress setting the exit Status on error
-v		inVert the matching logic-- show lines that don't match
-V		Show the Version number, etc

and the long options are:

--and		same as -j
--context count	same as -C
--count		same as -c
--head		same as -h
--help		same as -H
--invert	same as -i
--or		turns off -j. This is the default anyway
--version	same as -V

path is the path of a file (or for -R, a directory)

pygrep will search through the files and find lines that
match the regular expression supplied.  If there is
more than one file to process then the nane of the 
file is prepended to the line (unless the -h option is
in use.

Default settings have been chosen so as to prevent garbage
appearing on the screen (options -a -A -B) or excessive
output (-R), but to give reasonable diagnostics (-s -S).

Bugs: Too many options.  Maybe the setup needs to be
done interacting at a prompt!?  So many options means
the options must be case sensitive.  -j for conjunction
is an awful mnemonic for and.  The program is
written to read in a file at one go. It is thus memory
hungry, but my memory stingy version (in Perl) ran too
slowly. 
""")
        pass	# to help with aligning text





# Some of the processing we only need to do if
# run as a program.

if __name__ == '__main__':
    # test_Pygrep_results()
    grep = Pygrep()
    sys.exit(grep.pygrep(sys.argv[1:]))
