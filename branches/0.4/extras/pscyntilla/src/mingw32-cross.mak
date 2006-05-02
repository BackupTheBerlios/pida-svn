BASEDIR=

M = i586-mingw32msvc
CC=$(M)-gcc
NM=$(M)-nm
DLLWRAP=$(M)-dllwrap
DLLTOOL=$(M)-dlltool
PYVER=24

PYDIR=$(BASEDIR)/Python$(PYVER)

PKGCONFIG = pkg-config
PACKAGES = gtk+-2.0 glib-2.0 pygtk-2.0 gthread-2.0

# Compiler flags
INCLUDES=-I$(PYDIR)/include -I$(BASEDIR)/include `$(PKGCONFIG) --cflags $(PACKAGES)` -I../scintilla/include

LDFLAGS+=-L$(PYDIR)/libs -L$(BASEDIR)/libs -L$(SCINTILLADIR)/bin -lscintilla -lstdc++ `$(PKGCONFIG) --libs $(PACKAGES)`

LIBS=-lpython$(PYVER)


CFLAGS+=-fno-strict-aliasing -DNDEBUG -g -O3 -Wall -Wstrict-prototypes $(INCLUDES)


LIB2DEF=./lib2def.py

LIBPY_DEF=$(PYDIR)/libs/libpython$(PYVER).def
LIBPY_A=$(PYDIR)/libs/libpython$(PYVER).a

MODULE=scintilla

INPUT=scintillamodule.o marshallers.o pyscintilla.o gtkscintilla_signals.o gtkscintilla.o

OUTPUT=$(MODULE).pyd
MODULE_DEF=$(MODULE).def

all: $(OUTPUT)

$(LIBPY_DEF): $(PYDIR)/libs/python$(PYVER).lib
	NM=$(NM) PYVER=$(PYVER) $(LIB2DEF) $^ $@

$(LIBPY_A): $(LIBPY_DEF)
	$(DLLTOOL) --dllname python$(PYVER).dll --def $^ --output-lib $@

$(OUTPUT): $(INPUT) $(LIBPY_A) $(MODULE_DEF)
	$(DLLWRAP) --dllname $(MODULE).pyd --driver-name $(CC) --def $(MODULE_DEF) -o $@ $(INPUT) -s --entry _DllMain@12 --target=i586-mingw32 $(LDFLAGS) $(LIBS)

clean:
	rm -f *.o *.py