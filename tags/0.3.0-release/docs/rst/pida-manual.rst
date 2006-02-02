===============
The PIDA Manual
===============

:author: Ali Afshar
:contact: aafshar@gmail.com

.. contents:: Table Of Contents

Front Matter
============

Introduction
------------

PIDA is an integrated development environment for all types of development. It
is written in Python using the PyGTK Toolkit.

PIDA is different from other IDEs. Rather than attempting to write a set of
development tools of its own, PIDA uses tools that the developer has available.
In this regards PIDA is a framework for assembling a bespoke IDE. PIDA allows
you to choose the editor you wish to use (yes, Vim out of the box works).

Although still a young application, pIDA can already boast a huge number of
features because of the power of some of the tools it integrates. For example
features such as code completion and syntax highlighting are well implemented in
PIDA's integrated editors far better than any editor built for a commercial
IDE.

Additionally PIDA insists on stealing excellent ideas from applications it
cannot embed. For example the Rapid Application Development in the style of
Microsoft's development products is achieved by the combination of Gazpacho_ (a
user interface designer) and Tepache_ (a code sketcher), via the text editor.

Copyright
---------

PIDA is released under the MIT_ license. This is not a particularly philosophical
decision, except that the PIDA developers consider it a good thing that PIDA is
not GPL_, or even closed source.

The PIDA Project is owned by Ali Afshar (this author).


Authors
-------

- Ali Afshar
- Bernard Pratz
- Alejandro Mery

Contributors
------------

Stephen Holmes - A consistent and competent source of pain and suffering.

Getting Started
===============

Requirements to run PIDA
------------------------

Your requirements will largely depend on what you want to do with PIDA.

Minimum Requirements
++++++++++++++++++++

Python : 2.4
  Python is most likely installed on UNIX systems. PIDA requires version 2.4,
  which is available to download at py24download_.

PyGTK : 2.6
  GTK is the graphical toolkit used in PIDA, and PyGTK is the set of bindings
  for the Python programing language. You should use the latest version
  available at pygtkdownload_

Optional Requirements
+++++++++++++++++++++

Gazpacho User Interface Designer : 0.6.4
  Gazpacho is a GTK (Glade cmpatible) user interface designer. The latest
  version is available at the Gazpacho_ web site.

Installing PIDA
---------------

If you can get PIDA from your distribution, this is best. Otherwise you will
need to download the source tarball. Unpack the tarball, and in the top-level
directory, issue the command (you may require super user access on your computer for a system install)::

  python setup.py install

PIDA will now be installed in your default python location, and be available
to all users of the system.


.. note ::
  If you do not wish to install PIDA, it can be run from the local directory.
  (See `Running pida without installing`_)

Running PIDA
------------

Running pida after installation
+++++++++++++++++++++++++++++++

If PIDA has been installed, simply issue the command::

  pida

If correctly installed, PIDA will start.

Running pida without installing
+++++++++++++++++++++++++++++++

The ``develop.sh`` script in the top-level source directory can be used to run
PIDA without installing system-wide. To execute it, issue the command::

  ./develop.sh

The script generates a PIDA egg in a temporary directory for the duration of
the session.

Using PIDA
==========

PIDA is very varied in its features and what you may want to do with it might
not be what someone else might want to do with it (this is fine). In order to
familiarise yourself with PIDA, the following chapters are designed to take
you through the basic common functionality that we think you would all like to
use.

Projects
--------

PIDA projects are the way in which PIDA organises a set of files. The default
project type maps to a single source directory, which is then used for quick
navigation and version control functions.

Adding a project to the workbench
+++++++++++++++++++++++++++++++++

Firstly, from the *Project* menu select *New Project*, and Enter the
information into the newly displayed form.

Name
  The name you would like to use for the project

Save In
  The directory you would like to save the project file in (or the default
  pida projects directory by default).

Type
  The type of project this project is

Once you have entered this information click *ok*.

You will be presented with the initial project configuration dialog for the
project.

Depending on the type of project, you will have different options. The most
common option is *Source Directory*. This is the directory that will be
navigated to when clicking on a project, and the directory that is used for
project functions, including version control. When you are happy with the
configuration, press the *save* button.

Your new project will have appeared on the project list, and is available to
browse and use.

.. note :: The project file may be stored in the project source directory if
  required. The initial value of the project source directory actually
  defaults to the location of the project source file. This allows you to add
  the project file to a version control system and monitor the changes.

Using a project
+++++++++++++++

First, Locate the project list. It is in the pane marked *plugins* and
has an icon signifying a project. This pane will be used to access projects.

Selecting a project from this project list will open a file manager in the
source directory of the project, whatever that is configured to be.

Right-clicking on a project gives the context menu. This context menu is
divided into three sections of contexts.

Directory 
    These are file system actions to be performed on the source directory.

Source Code
    These are version control commands to be performed in the context of the
    project.

Project
    These are actions to be performed on the actual project object, e.g.
    project configuration.

Configuring a project
+++++++++++++++++++++

Projects are configured using the project configuration dialog. To open the
project configuration dialog, either:

1.  Select *Properties* from the *Project* menu.

2.  Right click on a project, and in the context menu, select *Configure this
    project* from the *Project* submenu.

You should click the *Save* button when you have finished and are happy.

The *Undo* button allows you to revert changes to the configuration back to
the last saved state.

The *Cancel* button closes the dialog without saving any changes. Closing the
dialog manually will have the same effect as pressing *Cancel*.

Version Control
---------------

PIDA automatically detects which version control system you are using for a
particular source directory. This allows you to choose the version control
system you wish to use.

PIDA currently supports:

- CVS
- Subversion
- Darcs
- Mercurial
- Monotone
- Bzr
- Arch

Version control is used throughout PIDA in 3 ways which are outlined below.

Project Management Version Control
++++++++++++++++++++++++++++++++++

The project list states the version control system for a project. When a
project is selected, main version control commands (from the main menu and
main toolbar) will be executed in the source directory of the project,
automatically using the correct version control system.

The version control commands may also be accessed using the context menu
made available by right-clicking on a project.

File Browsing Version Control
+++++++++++++++++++++++++++++

The built-in file browser autoimatically lists version control information
for listed files. This information appears as a standard set of letters
(e.g. *M* for a locally modified file) adjacent to filenames in the browser.

To use this, click on any project, in order to open the browser at the
project's source directory.

When right clicking on a file or directory, you are given a list of version
control commands which can be carried out n the file or directory.


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
