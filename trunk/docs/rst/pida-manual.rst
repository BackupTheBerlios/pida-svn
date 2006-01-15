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

Firstly, from the *Project* menu select *Add Project*, and Enter the
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

Version Control
---------------

Terminal Emulators
------------------

Developing PIDA
===============


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


.. _GPL: http://www.opensource.org/licenses/gpl-license.php
.. _Gazpacho: http://gazpacho.sicem.biz/
