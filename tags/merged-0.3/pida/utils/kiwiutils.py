#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005 Async Open Source
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
# 
# Author(s): Lorenzo Gil Sanchez <lgs@sicem.biz>
#            Johan Dahlin <jdahlin@async.com.br>
#

"""GObject utilities and addons"""

import struct
import sys

import gobject

def gsignal(name, *args, **kwargs):
    """
    Add a GObject signal to the current object.
    It current supports the following types:
      str, int, float, long, object, enum
    @param name:     name of the signal
    @type name:      string
    @param args:     types for signal parameters,
      if the first one is a string 'override', the signal will be
      overridden and must therefor exists in the parent GObject.
    @keyword flags: One of the following:
      - gobject.SIGNAL_RUN_FIRST
      - gobject.SIGNAL_RUN_LAST
      - gobject.SIGNAL_RUN_CLEANUP
      - gobject.SIGNAL_NO_RECURSE
      - gobject.SIGNAL_DETAILED
      - gobject.SIGNAL_ACTION
      - gobject.SIGNAL_NO_HOOKS
    @keyword retval: return value in signal callback
    """

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
    finally:
        del frame
        
    if not '__gsignals__' in locals:
        dict = locals['__gsignals__'] = {}
    else:
        dict = locals['__gsignals__']

    if args and args[0] == 'override':
        dict[name] = 'override'
    else:
        retval = kwargs.get('retval', None)
        if retval is None:
            default_flags = gobject.SIGNAL_RUN_FIRST
        else:
            default_flags = gobject.SIGNAL_RUN_LAST
            
        flags = kwargs.get('flags', default_flags)
        if retval is not None and flags != gobject.SIGNAL_RUN_LAST:
            raise TypeError(
                "You cannot use a return value without setting flags to "
                "gobject.SIGNAL_RUN_LAST")
    
        dict[name] = (flags, retval, args)

def _max(c):
    # Python 2.3 does not like bitshifting here
    return 2 ** ((8 * struct.calcsize(c)) - 1) - 1

_MAX_VALUES = {int : _max('i'),
               float : _max('f'),
               long : _max('l') }
_DEFAULT_VALUES = {str : '', float : 0.0, int : 0, long : 0L}
                   
def gproperty(name, ptype, default=None, nick='', blurb='',
              flags=gobject.PARAM_READWRITE, **kwargs):
    """
    Add a GObject property to the current object.
    @param name:   name of property
    @type name:    string
    @param ptype:   type of property
    @type ptype:    type
    @keyword default:  default value
    @keyword nick:     short description
    @keyword blurb:    long description
    @keyword flags:    parameter flags, one of:
      - PARAM_READABLE
      - PARAM_READWRITE
      - PARAM_WRITABLE
      - PARAM_CONSTRUCT
      - PARAM_CONSTRUCT_ONLY
      - PARAM_LAX_VALIDATION
    Optional, only for int, float, long types:
    @keyword minimum:  minimum allowed value 
    @keyword maximum:  maximum allowed value
    """

    # General type checking
    if default is None:
        default = _DEFAULT_VALUES.get(ptype)
    elif not isinstance(default, ptype):
        raise TypeError("default must be of type %s, not %r" % (
            ptype, default))
    if not isinstance(nick, str):
        raise TypeError('nick for property %s must be a string, not %r' % (
            name, nick))
    nick = nick or name
    if not isinstance(blurb, str):
        raise TypeError('blurb for property %s must be a string, not %r' % (
            name, blurb))

    # Specific type checking
    if ptype == int or ptype == float or ptype == long:
        default = (kwargs.get('minimum', ptype(0)),
                   kwargs.get('maximum', _MAX_VALUES[ptype]),
                   default)
    elif ptype == bool:
        if (default is not True and
            default is not False):
            raise TypeError("default must be True or False, not %r" % (
                default))
        default = default,
    elif gobject.type_is_a(ptype, gobject.GEnum):
        if default is None:
            raise TypeError("enum properties needs a default value")
        elif not isinstance(default, ptype):
            raise TypeError("enum value %s must be an instance of %r" %
                            (default, ptype))
        default = default,
    elif ptype == str:
        default = default,
    elif ptype == object:
        if default is not None:
            raise TypeError("object types does not have default values")
        default = ()
    else:
        raise NotImplementedError("type %r" % ptype)
    
    if flags not in (gobject.PARAM_READABLE, gobject.PARAM_READWRITE,
                     gobject.PARAM_WRITABLE, gobject.PARAM_CONSTRUCT,
                     gobject.PARAM_CONSTRUCT_ONLY,
                     gobject.PARAM_LAX_VALIDATION):
        raise TypeError("invalid flag value: %r" % flags)

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
        if not '__gproperties__' in locals:
            dict = locals['__gproperties__'] = {}
        else:
            dict = locals['__gproperties__']
    finally:
        del frame

    dict[name] = (ptype, nick, blurb) + default + (flags,)
