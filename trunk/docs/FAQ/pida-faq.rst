============
The PIDA FAQ
============

:author: Ali Afshar
:contact: aafshar@gmail.com

General
-------

Is PIDA available for Windows?
++++++++++++++++++++++++++++++


Vim
---

I close buffers in Vim. Why are they still visible in PIDA?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you have closed a vim buffer using ``:bd`` or ``Delete`` from the
``Buffer`` menu, the buffer will still remain in the PIDA buffer list. This is
not a bug but a feature of how Vim works. It does not actually delete the
buffer on ``:bd`` but merely hides it.

The solution is to use ``:bw``. This properly unloads the buffer and PIDA
correctly recognises this situation. If you have read the Vim docs (like a
good Vimmer) you know hat the documentation regarding ``:bw`` is a bit scary,
and asks you to *make sure you know what you are doing*. Rest assured, it
works fine.

