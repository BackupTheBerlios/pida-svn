===============
The PIDA Manual
===============

:author: Ali Afshar
:contact: aafshar@gmail.com

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

The MIT License (PIDA Variation)::

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


Authors
-------

Ali Afshar
Bernard Pratz
Alejandro Mery

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
version is available at 

Installing PIDA
---------------

Running PIDA
------------

Using PIDA
==========

Projects
--------

PIDA projects are the way in which PIDA organises a set of files. The default
project type maps to a single source directory, which is then used for quick
navigation and version control functions.

Adding a project to the workbench
+++++++++++++++++++++++++++++++++

1. From the *Project* menu select *Add Project*.
2. Enter the information into the newly displayed form.

Version Control
---------------

Terminal Emulators
------------------

Developing PIDA
===============




.. _GPL: http://www.opensource.org/licenses/gpl-license.php
.. _Gazpacho: http://gazpacho.sicem.biz/
