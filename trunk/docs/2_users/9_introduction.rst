===============
The PIDA Manual
===============

:author: Ali Afshar
:contact: aafshar@gmail.com

.. contents:: Table Of Contents

Copyright
---------

PIDA is released under the MIT_ license. This is not a particularly philosophical
decision, except that the PIDA developers consider it a good thing that PIDA is
not GPL_, or even closed source.

The PIDA Project is owned by Ali Afshar (this author).


Editing code
------------

Keeping track of unfinished tasks
+++++++++++++++++++++++++++++++++

Pida now has supports a TODO list, featured in some other python IDEs. As 
you write code, you can include comment tags with the word "TODO:" in. In
the side panel for browsing source code (the source browser & error buttons),
click on the small icon at the bottom, and you'll see a list of your tasks 
still undone. Clicking on one of these will take you to the appropriate place 
in your document, and you can do whatever small task it was that required the
note in the first place.

Appendix A
==========

The MIT License::

  Copyright (c) 2005-2006 The PIDA Project

  Permission is hereby granted, free of charge, to any person obtaining a copy of
  this software and associated documentation files (the "Software"), to deal in
  the Software without restriction, including without limitation the rights to
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
  the Software, and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
  IN AN ACTION OF CONTRACT, TORT, TURTLE, OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Appendix B: Extra tools for Vim
===============================

For others using Vim, there's a few bits and pieces you might find useful, including:

Pydiction_, which lets you add python modules, including classes and methods, to vim's 
autocomplete functionality. You can also add your own project(s) to the autocompleting.
Download from the site, extract it, and put these lines in your .vimrc::

  if has("autocmd")
    autocmd FileType python set complete+=k/path/to/pydiction isk+=.,(
  endif " has("autocmd") 


Now when you press Ctrl+n (next), or Ctrl+p (previous), vim should autocomplete to 
the appropriate python code.


Python.vim_, which has some extra functions for handling python code, including:

- Select a block of lines with the same indentation
- Select a function
- Select a class
- Go to previous/next class/function
- Go to the beginning/end of a block
- Comment the selection
- Uncomment the selection
- Jump to the last/next line with the same indent
- Shift a block (left/right) 

.. _Pydiction: http://www.vim.org/scripts/script.php?script_id=850
.. _Python.vim: http://www.vim.org/scripts/script.php?script_id=30
.. _GPL: http://www.opensource.org/licenses/gpl-license.php
.. _Gazpacho: http://gazpacho.sicem.biz/
