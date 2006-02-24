========================
Requirements to run PIDA
========================

.. contents:: Table Of Contents

:author: Ali Afshar
:contact: aafshar@gmail.com

Minimum Requirements
++++++++++++++++++++

Python : >=2.4
  Python is most likely installed on UNIX systems. PIDA requires version 2.4,
  which is available to download at the `Python web site`_.

PyGTK : >=2.6
  GTK is the graphical toolkit used in PIDA, and PyGTK is the set of bindings
  for the Python programing language. You should use the latest version
  available at the `PyGTK web site`_

Setuptools : >=0.6.9 (I think)
  Setuptools is used for installation, plugins, and runtime source discovery.
  It is available in most distributions, or from the `Setuptools web site`_

VTE Terminal widget : Any recent
  The VTE terminal widget is required (for now) with Python bindings. If you
  FBSD, you will have to hack your ports Makefile.

Python-gnome-extras : Any recent
  Despite the name, this is a library of gtk widgets, and has very little to
  do with gnome. It is available in most distributions and is actually a tiny
  set of bindings.

Optional Requirements
+++++++++++++++++++++

Gazpacho User Interface Designer : svn trunk
  Gazpacho is a GTK (Glade cmpatible) user interface designer. The latest
  version is available at the `Gazpacho web site`_.

.. _Python web site: http://python.org/
.. _PyGTK web site: http://pygtk.org/
.. _Setuptools web site: http://peak.telecommunity.com/DevCenter/setuptools
.. _Gazpacho web site: http://gazpacho.sicem.biz/

