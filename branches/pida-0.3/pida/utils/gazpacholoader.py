# Copyright (C) 2005 Johan Dahlin
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# TODO:
# Parser tags: atk, relation
# Document public API
# Parser subclass
# Improved unittest coverage
# Old style toolbars
# Require importer/resolver (gazpacho itself)
# GBoxed properties

import os
from gettext import textdomain, dgettext
from xml.parsers import expat

import gobject
import gtk
from gtk import gdk

#from gazpacho.loader.custom import adapter_registry, flagsfromstring, \
#     str2bool

__all__ = ['ObjectBuilder', 'ParseError']

class ParseError(Exception):
    pass

class Stack(list):
    push = list.append
    def peek(self):
        if self:
            return self[-1]

class BaseInfo:
    def __init__(self):
        self.data = ''

    def __repr__(self):
        return '<%s data=%r>' % (self.__class__.__name__,
                                 self.data)
        
class WidgetInfo(BaseInfo):
    def __init__(self, attrs, parent):
        BaseInfo.__init__(self)
        self.klass = str(attrs.get('class'))
        self.id = str(attrs.get('id'))
        self.constructor  = attrs.get('constructor')
        self.children = []
        self.properties = []
        self.signals = []
        self.uis = []
        self.accelerators = []
        self.parent = parent
        self.gobj = None
        # If it's a placeholder, used by code for unsupported widgets
        self.placeholder = False
        
    def is_internal_child(self):
        return self.parent and self.parent.internal_child

    def __repr__(self):
        return '<WidgetInfo of type %s>' % (self.klass)
    
class ChildInfo(BaseInfo):
    def __init__(self, attrs, parent):        
        BaseInfo.__init__(self)
        self.internal_child = attrs.get('internal-child')
        self.properties = []
        self.packing_properties = []
        self.placeholder = False
        self.parent = parent
        self.widget = None
        
    def __repr__(self):
        return '<ChildInfo containing a %s>' % (self.widget)
    
class PropertyInfo(BaseInfo):
    def __init__(self, attrs):
        BaseInfo.__init__(self)
        self.name = str(attrs.get('name'))
        self.translatable = str2bool(attrs.get('translatable', 'no'))
        self.context = str2bool(attrs.get('context', 'no'))
        self.agent = attrs.get('agent') # libglade
        self.comments = attrs.get('comments')
        
    def __repr__(self):
        return '<PropertyInfo of type %s=%r>' % (self.name, self.data)

class SignalInfo(BaseInfo):
    def __init__(self, attrs):
        BaseInfo.__init__(self)
        self.name = attrs.get('name')
        self.handler = attrs.get('handler')
        self.after = str2bool(attrs.get('after', 'no'))
        self.object = attrs.get('object')
        self.last_modification_time = attrs.get('last_modification_time')
        self.gobj = None

class AcceleratorInfo(BaseInfo):
    def __init__(self, attrs):
        BaseInfo.__init__(self)
        self.key = gdk.keyval_from_name(attrs.get('key'))
        self.modifiers = flagsfromstring(attrs.get('modifiers'),
                                         flags=gdk.ModifierType)
        self.signal = str(attrs.get('signal'))
  
class UIInfo(BaseInfo):
    def __init__(self, attrs):
        BaseInfo.__init__(self)
        self.id = attrs.get('id')
        self.filename = attrs.get('filename')
        self.merge = str2bool(attrs.get('merge', 'yes'))

class ExpatParser(object):
    def __init__(self, domain):
        self._domain = domain
        self.requires = []
        self._stack = Stack()
        self._state_stack = Stack()
        self._parser = expat.ParserCreate()
        self._parser.buffer_text = True
        self._parser.StartElementHandler = self._handle_startelement
        self._parser.EndElementHandler = self._handle_endelement
        self._parser.CharacterDataHandler = self._handle_characterdata
        
    # Public API
    def parse_file(self, filename):
        fp = open(filename)
        self._parser.ParseFile(fp)
        
    def parse_stream(self, buffer):
        self._parser.Parse(buffer)

    # Expat callbacks
    def _handle_startelement(self, name, attrs):
        self._state_stack.push(name)
        name = name.replace('-', '_')
        func = getattr(self, '_start_%s' % name, None)
        if func:
            item = func(attrs)
            self._stack.push(item)
            
    def _handle_endelement(self, name):
        self._state_stack.pop()
        name = name.replace('-', '_')
        func = getattr(self, '_end_%s' % name, None)
        if func:
            item = self._stack.pop()
            func(item)
        
    def _handle_characterdata(self, data):
        info = self._stack.peek()
        if info:
            info.data += str(data)

    # Tags
    def _start_glade_interface(self, attrs):
        # libglade extension, add a domain argument to the interface
        if 'domain' in attrs:
            self._domain = str(attrs['domain'])
        
    def _end_glade_interface(self, obj):
        pass
    
    def _start_requires(self, attrs):
        self.requires.append(attrs)
        
    def _end_requires(self, obj):
        pass
    
    def _start_signal(self, attrs):
        if not 'name' in attrs:
            raise ParseError("<signal> needs a name attribute")
        if not 'handler' in attrs:
            raise ParseError("<signal> needs a handler attribute")
        return SignalInfo(attrs)

    def _end_signal(self, signal):
        obj = self._stack.peek()
        obj.signals.append(signal)

    def _start_widget(self, attrs):
        if not 'class' in attrs:
            raise ParseError("<widget> needs a class attribute")
        if not 'id' in attrs:
            raise ParseError("<widget> needs an id attribute")
        
        return WidgetInfo(attrs, self._stack.peek())
    _start_object = _start_widget
    
    def _end_widget(self, obj):
        obj.parent = self._stack.peek()

        if not obj.gobj:
            obj.gobj = gobj = self._build_phase1(obj)

        self._build_phase2(obj)

        if obj.parent:
            obj.parent.widget = obj.gobj
            
    _end_object = _end_widget
        
    def _start_child(self, attrs):
        obj = self._stack.peek()
        obj.gobj = self._build_phase1(obj)

        return ChildInfo(attrs, parent=obj)

    def _end_child(self, child):
        obj = self._stack.peek()
        obj.children.append(child)
        
    def _start_property(self, attrs):
        if not 'name' in attrs:
            raise ParseError("<property> needs a name attribute")
        return PropertyInfo(attrs)

    def _end_property(self, prop):
        if prop.agent and prop.agent not in ('libglade', 'gazpacho'):
            return

        if prop.translatable:
            prop.data = dgettext(self._domain, prop.data)
            
        obj = self._stack.peek()
        
        property_type = self._state_stack.peek()
        if property_type == 'widget' or property_type == 'object':
            obj.properties.append(prop)
        elif property_type == 'packing':
            obj.packing_properties.append(prop)
        else:
            raise ParseError("property must be a node of widget or packing")

    def _start_ui(self, attrs):
        if not 'id' in attrs:
            raise ParseError("<ui> needs an id attribute")
        return UIInfo(attrs)
    
    def _end_ui(self, ui):
        if not ui.data or ui.filename:
            raise ParseError("<ui> needs CDATA or filename")
        
        obj = self._stack.peek()
        obj.uis.append(ui)

    def _start_placeholder(self, attrs):
        pass

    def _end_placeholder(self, placeholder):
        obj = self._stack.peek()
        obj.placeholder = True

    def _start_accelerator(self, attrs):
        if not 'key' in attrs:
            raise ParseError("<accelerator> needs a key attribute")
        if not 'modifiers' in attrs:
            raise ParseError("<accelerator> needs a modifiers attribute")
        if not 'signal' in attrs:
            raise ParseError("<accelerator> needs a signal attribute")
        obj = self._stack.peek()
        return AcceleratorInfo(attrs)
    
    def _end_accelerator(self, accelerator):
        obj = self._stack.peek()
        obj.accelerators.append(accelerator)

class ObjectBuilder:
    def __init__(self, filename='', buffer=None, root=None, placeholder=None,
                 custom=None, domain=None):
        if ((not filename and not buffer) or
            (filename and buffer)):
            raise TypeError("need a filename or a buffer")

        self._filename = filename
        self._buffer = buffer
        self._root = root
        self._placeholder = placeholder
        self._custom = custom
        
        self.toplevels = []
        # name -> GObject
        self._widgets = {}
        self._signals = []
        # GObject -> Constructor
        self._constructed_objects = {}
        # ui definition name -> UIMerge, see _mergeui
        self._uidefs = {}
        # ui definition name -> constructor name (backwards compatibility)
        self._uistates = {}
        self._tooltips = gtk.Tooltips()
        self._tooltips.enable()
        self._focus_widget = None
        self._default_widget = None
        self._toplevel = None
        self._accel_group = None
        self._delayed_properties = {}
        self._internal_children = {}
        
        # If domain is not specified, fetch the default one by
        # calling textdomain() without arguments
        if not domain:
            domain = textdomain()
            
        self._parser = ExpatParser(domain)
        self._parser._build_phase1 = self._build_phase1
        self._parser._build_phase2 = self._build_phase2
        if filename:
            self._parser.parse_file(filename)
        elif buffer:
            self._parser.parse_stream(buffer)
        self._parse_done()
        
    def __len__(self):
        return len(self._widgets)

    def __nonzero__(self):
        return True

    # Public API

    def get_widget(self, widget):
        return self._widgets.get(widget)

    def get_widgets(self):
        return self._widgets.values()
    
    def signal_autoconnect(self, obj):
        for gobj, name, handler_name, after, object_name in self.get_signals():
            # Firstly, try to map it as a dictionary
            try:
                handler = obj[handler_name]
            except AttributeError, TypeError:
                # If it fails, try to map it to an attribute
                handler = getattr(obj, handler_name, None)
                if not handler:
                    continue

            if object_name:
                other = self._widgets.get(object_name)
                if after:
                    gobj.connect_object_after(name, handler, other)
                else:
                    gobj.connect_object(name, handler, other)
            else:
                if after:
                    gobj.connect_after(name, handler)
                else:
                    gobj.connect(name, handler)

    def show_windows(self):
        # First set focus, warn if more than one is focused
        toplevel_focus_widgets = []
        for widget in self.get_widgets():
            if not isinstance(widget, gtk.Widget):
                continue
            
            if widget.get_data('gazpacho::is-focus'):
                toplevel = widget.get_toplevel()
                name = toplevel.get_name()
                if name in toplevel_focus_widgets:
                    print ("Warning: Window %s has more than one "
                           "focused widget" % name)
                toplevel_focus_widgets.append(name)

        # At last, display all of the visible windows
        for toplevel in self.toplevels:
            if not isinstance(toplevel, gtk.Window):
                continue
            value = toplevel.get_data('gazpacho::visible')
            toplevel.set_property('visible', value)
            
    def get_internal_children(self, gobj):
        if not gobj in self._internal_children:
            return []
        return self._internal_children[gobj]
    
    # Adapter API
    
    def add_signal(self, gobj, name, handler, after=False, sig_object=None):
        self._signals.append((gobj, name, handler, after, sig_object))

    def get_signals(self):
        return self._signals
    
    def find_resource(self, filename):
        dirname = os.path.dirname(self._filename)
        path = os.path.join(dirname, filename)
        if os.access(path, os.R_OK):
            return path
        
    def get_ui_definitions(self):
        return [(name, info.data) for name, info in self._uidefs.items()]
    
    def get_constructor(self, gobj):
        return self._constructed_objects[gobj]
    
    def ensure_accel(self):
        if not self._accel_group:
            self._accel_group = gtk.AccelGroup()
            if self._toplevel:
                self._toplevel.add_accel_group(self._accel_group)
        return self._accel_group

    def add_delayed_property(self, obj_id, pspec, value):
        delayed = self._delayed_properties
        if not obj_id in delayed:
            delayed_properties = delayed[obj_id] =[]
        else:
            delayed_properties = delayed[obj_id]

        delayed_properties.append((pspec, value))

    # Private
    
    def _setup_signals(self, gobj, signals):
        for signal in signals:
            self.add_signal(gobj, signal.name, signal.handler,
                           signal.after, signal.object)
            
    def _setup_accelerators(self, widget, accelerators):
        if not accelerators:
            return
        
        accel_group = self.ensure_accel()
        widget.set_data('gazpacho::accel-group', accel_group)
        for accelerator in accelerators:
            widget.add_accelerator(accelerator.signal,
                                   accel_group,
                                   accelerator.key,
                                   accelerator.modifiers,
                                   gtk.ACCEL_VISIBLE)

    def _apply_delayed_properties(self):
        for obj_id, props in self._delayed_properties.items():
            widget = self._widgets.get(obj_id)
            if widget is None:
                raise AssertionError
            
            adapter = adapter_registry.get_adapter(widget, self)

            prop_list = []
            for pspec, value in props:
                if gobject.type_is_a(pspec.value_type, gobject.GObject):
                    other = self._widgets.get(value)
                    if other is None:
                        raise ParseError(
                            "property %s of %s refers to widget %s which "
                            "does not exist" % (pspec.name, obj_id,value))
                    prop_list.append((pspec.name, other))
                else:
                    raise NotImplementedError(
                        "Only delayed object properties are "
                        "currently supported")

            adapter.set_properties(widget, prop_list)

    def _merge_ui(self, uimanager_name, name,
                  filename='', data=None, merge=True):
        uimanager = self._widgets[uimanager_name]
        if merge:
            if filename:
                filename = self.find_resource(filename)
                # XXX Catch GError
                merge_id = uimanager.add_ui_from_file(filename)
            elif data:
                # XXX Catch GError
                merge_id = uimanager.add_ui_from_string(data)
            else:
                raise AssertionError
        else:
            merge_id = -1

        class UIMerge:
            def __init__(self, uimanager, filename, data, merge_id):
                self.uimanager = uimanager,
                self.filename = filename
                self.data = data
                self.merge_id = merge_id
                         
        current = self._uidefs.get(name)
        if current:
            current.merge_id = merge_id
        else:
            self._uidefs[name] = UIMerge(uimanager, filename, data,
                                         merge_id)

        # Backwards compatibility
        self._uistates[name] = uimanager_name
        
    def _uimanager_construct(self, uimanager_name, obj_id):
        uimanager = self._widgets[uimanager_name]
        
        widget = uimanager.get_widget('ui/' + obj_id)
        if widget is None:
            # XXX: untested code
            uimanager_name = self._uistates.get(obj_id)
            if not uimanager_name:
                raise AssertionError
            uimanager = self._widgets[uimanager_name]
        
        return widget
    
    def _find_internal_child(self, obj):
        child = None
        childname = str(obj.parent.internal_child)
        parent = obj.parent
        while parent:
            if isinstance(parent, ChildInfo):
                parent = parent.parent
                continue
            
            gparent = parent.gobj
            if not gparent:
                break

            adapter = adapter_registry.get_adapter(gparent, self)
            child = adapter.find_internal_child(gparent, childname)
            if child is not None:
                break
            
            parent = parent.parent

        if child is not None:
            if not gparent in self._internal_children:
                self._internal_children[gparent] = []
            self._internal_children[gparent].append((childname, child))
        
        return child

    def _create_custom(self, obj):
        kwargs = dict(name=obj.id)
        for prop in obj.properties:
            prop_name = prop.name
            if prop_name in ('string1', 'string2',
                             'creation_function',
                             'last_modification_time'):
                kwargs[prop_name] = prop.data
            elif prop_name in ('int1', 'int2'):
                kwargs[prop_name] = int(prop.data)

        if not self._custom:
            return gtk.Label('<Custom: %s>' % obj.id)
        elif callable(self._custom):
            func = self._custom
            return func(**kwargs)
        else:
            func_name = kwargs['creation_function']
            try:
                func = self._custom[func_name]
            except (TypeError, KeyError, AttributeError):
                func = getattr(self._custom, func_name, None)

            return func(name=obj.id,
                        string1=kwargs.get('string1', None),
                        string2=kwargs.get('string2', None),
                        int1=kwargs.get('int1', None),
                        int2=kwargs.get('int2', None))
            
    def _create_placeholder(self, obj=None):
        if not obj:
            klass = name = 'unknown'
        else:
            name = obj.id
            klass = obj.klass
            
        if not self._placeholder:
            return

        return self._placeholder(name)
        
    def _build_phase1(self, obj):
        root = self._root
        if root and root != obj.id:
            return

        if obj.klass == 'Custom':
            return self._create_custom(obj)
        
        try:
            gtype = gobject.type_from_name(obj.klass)
        except RuntimeError:
            print 'Could not construct object: %s' % obj.klass
            obj.placeholder = True
            return self._create_placeholder(obj)

        adapter = adapter_registry.get_adapter(gtype, self)
        construct, normal = adapter.get_properties(gtype,
                                                   obj.id,
                                                   obj.properties)
        if obj.is_internal_child():
            gobj = self._find_internal_child(obj)
        elif obj.constructor:
            if self._widgets.has_key(obj.constructor):
                gobj = self._uimanager_construct(obj.constructor, obj.id)
                constructor = obj.constructor
            # Backwards compatibility
            elif self._uistates.has_key(obj.constructor):
                constructor = self._uistates[obj.constructor]
                gobj = self._uimanager_construct(constructor, obj.id)
            else:
                raise ParseError("constructor %s for object %s could not "
                                 "be found" % (obj.id, obj.constructor))
            self._constructed_objects[gobj] = self._widgets[constructor]
        else:
            gobj = adapter.construct(obj.id, gtype, construct)

        if gobj:
            self._widgets[obj.id] = gobj

            adapter.set_properties(gobj, normal)

            # This is a little tricky
            # We assume the default values for all these are nonzero, eg
            # either False or None
            # We also need to handle the case when we have two labels, if we
            # do we respect the first one. This is due to a bug in the save code
            for propinfo in obj.properties:
                key = 'i18n_is_translatable_%s' % propinfo.name
                if not gobj.get_data(key) and propinfo.translatable:
                    gobj.set_data(key, propinfo.translatable)

                key = 'i18n_has_context_%s' % propinfo.name
                if not gobj.get_data(key) and propinfo.context:
                    gobj.set_data(key, propinfo.context)

                # XXX: Rename to i18n_comments
                key = 'i18n_comment_%s' % propinfo.name
                if not gobj.get_data(key) and propinfo.comments:
                    gobj.set_data(key, propinfo.comments)
                    
        return gobj
    
    def _build_phase2(self, obj):
        # If we have a root set, we don't want to construct all
        # widgets, filter out unwanted here
        root = self._root
        if root and root != obj.id:
            return
            
        # Skip this step for placeholders, so we don't
        # accidentally try to pack something into unsupported widgets
        if obj.placeholder:
            return
       
        gobj = obj.gobj
        if not gobj:
            return
        
        adapter = adapter_registry.get_adapter(gobj, self)
        
        for child in obj.children:
            self._pack_child(adapter, gobj, child)

        self._setup_signals(gobj, obj.signals)
        self._setup_accelerators(gobj, obj.accelerators)
        
        # Toplevels
        if not obj.parent:
            if isinstance(gobj, gtk.UIManager):
                for ui in obj.uis:
                    self._merge_ui(obj.id,
                                   ui.id, ui.filename, ui.data, ui.merge)
                    self.accelgroup = gobj.get_accel_group()
            elif isinstance(gobj, gtk.Window):
                self._set_toplevel(gobj)

            self.toplevels.append(gobj)
        
    def _pack_child(self, adapter, gobj, child):

        if child.placeholder:
            widget = self._create_placeholder()
            if not widget:
                return
        elif child.widget:
            widget = child.widget
        else:
            return

        if child.internal_child:
            gobj = child.parent.gobj
            name = child.parent.id
            if isinstance(gobj, gtk.Widget):
                gobj.set_name(name)
            self._widgets[name] = gobj
            return
        
        # 5) add child
        try:
            adapter.add(gobj,
                        widget,
                        child.packing_properties)
        except NotImplementedError, e:
            print TypeError('%s does not support children' % (
                gobject.type_name(gobj)))

    def _parse_done(self):
        self._apply_delayed_properties()
        self.show_windows()
        
    def _set_toplevel(self, window):
        if self._focus_widget:
            self._focus_widget.grab_focus()
            self._focus_widget = None
        if self._default_widget:
            if self._default_widget.flags() & gtk.CAN_DEFAULT:
                self._default_widget.grab_default()
            self._default_widget = None
        if self._accel_group:
            self._accel_group = None

        # the window should hold a reference to the tooltips object 
        window.set_data('gazpacho::tooltips', self._tooltips)
        self._toplevel = window

# custom

import gobject
import gtk
from gtk import gdk

def enumfromstring(value_name, pspec=None, enum=None):
    if not value_name:
        return 0
    
    try:
        value = int(value_name)
    except ValueError:
        if pspec:
            enum_class = pspec.enum_class
            if enum_class is None:
                return 0
        elif enum:
            enum_class = enum
        else:
            raise ValueError("Need pspec or enm")
        
        for value, enum in enum_class.__enum_values__.items():
            if value_name in (enum.value_name, enum.value_nick):
                return value

    raise ValueError("Invalid enum value: %r" % value_name)

def flagsfromstring(value_name, pspec=None, flags=None):
    if not value_name:
        return 0

    try:
        return int(value_name)
    except ValueError:
        pass
    
    value_names = [v.strip() for v in value_name.split('|')]

    if pspec:
        flags_class = pspec.flags_class
    elif flags:
        flags_class = flags
    else:
        raise ValueError("need pspec or flags")
    
    flag_values = flags_class.__flags_values__
    new_value = 0
    for mask, flag in flag_values.items():
        if (flag.value_names[0] in value_names or
            flag.value_nicks[0] in value_names):
            new_value |= mask

    return new_value

def str2bool(value):
    return value[0].lower() in ('t', 'y') or value == '1'

def get_child_pspec_from_name(gtype, name):
    for pspec in gtk.container_class_list_child_properties(gtype):
        if pspec.name == name:
            return pspec

def get_pspec_from_name(gtype, name):
    for pspec in gobject.list_properties(gtype):
        if pspec.name == name:
            return pspec

class AdapterMeta(type):
    def __new__(meta, name, bases, dict):
        t = type.__new__(meta, name, bases, dict)
        t.add_adapter()
        return t

class IObjectAdapter:
    """This interface is used by the loader to build
    a custom object.

    object_type is a GType representing which type we can construct
    """
    object_type = None
    
    def construct(self, name, properties):
        """constructs a new type of type gtype
        name:  string representing the type name
        gtype: gtype of the object to be constructed
        properties: construct properties
        """
        pass

    def add(self, gobj, child, properties):
        """Adds a child to gobj with properties"""
        pass
    
    def get_properties(self, gtype, obj_id, properties):
        pass
    
    def set_properties(self, gobj, properties):
        pass

    def prop_set_NAME(self, widget, value_string):
        """
        Sets the property NAME for widget, note that you have to convert
        from a string manully"""
        pass
    
    def find_internal_child(self, gobj, name):
        """Returns an internal child"""

    def get_internal_child_name(self, gobj, child):
        """
        Returns the name of a widget, as an internal child or None
        if it cannot be found
        """
        
class Adapter(object):
    __metaclass__ = AdapterMeta
    _adapters = []

    def __init__(self, build):
        self._build = build
        
    def add_adapter(cls):
        if cls.__name__ != 'Adapter':
            cls._adapters.append(cls)
    add_adapter = classmethod(add_adapter)
    
    def get_adapters(cls):
        return cls._adapters
    get_adapters = classmethod(get_adapters)        

class AdapterRegistry:
    def __init__(self):
        # GObject typename -> adapter instance
        self._adapters = {}

        for adapter in Adapter.get_adapters():
            self.register_adapter(adapter)
             
    def _add_adapter(self, name, adapter):
        self._adapters[name] = adapter

    def register_adapter(self, adapter):
        adict = adapter.__dict__
        # Do not register abstract adapters
        if adict.has_key('object_type'):
            object_type = adict.get('object_type')
            if type(object_type) != tuple:
                object_type = object_type,
 
            for klass in object_type:
                self._add_adapter(gobject.type_name(klass), adapter)
        elif adict.has_key('object_name'):
            self._add_adapter(adict.get('object_name'), adapter)
            
    def get_adapter(self, gobj, build=None):
        orig = gobj
        while True:
            name = gobject.type_name(gobj)
            adapter = self._adapters.get(name)
            if adapter:
                return adapter(build)

            gobj = gobject.type_parent(gobj)
        
class GObjectAdapter(Adapter):
    object_type = gobject.GObject
    child_names = []
    def construct(self, name, gtype, properties):
        # Due to a bug in gobject.new() we only send in construct
        # only properties here, the rest are set normally
        gobj = gobject.new(gtype, **properties)
        return gobj
    
    def get_properties(self, gtype, obj_id, properties):
        return self._getproperties(gtype, obj_id, properties)
        
    def set_properties(self, gobj, properties):
        prop_names = []
        for name, value in properties:
            #print '%s.%s = %r' % (gobject.type_name(gobj), name, value)
            func_name = 'prop_set_%s' % name.replace('-', '_')
            func = getattr(self, func_name, None)
            if func:
                func(gobj, value)
            else:
                gobj.set_property(name, value)

            prop_names.append(name)

        gobj.set_data('gobject.changed_properties', prop_names)
    
    def _getproperties(self, gtype, obj_id, properties, child=False):
        if child:
            get_pspec = get_child_pspec_from_name
        else:
            get_pspec = get_pspec_from_name
            
        construct = {}
        normal = []
        parent_name = gobject.type_name(gtype)
        for prop in properties:
            propname = prop.name.replace('_', '-')
            #full = '%s::%s' % (parent_name, propname)
            if hasattr(self, 'prop_set_%s' % prop.name):
                normal.append((prop.name, prop.data))
                continue
            
            pspec = get_pspec(gtype, propname)
            if not pspec:
                print ('Unknown property: %s:%s (id %s)' %
                       (gobject.type_name(gtype),
                        prop.name,
                        obj_id))
                continue

            try:
                value = self._valuefromstring(obj_id, pspec, prop.data)
            except ValueError:
                print ("Convertion failed for %s:%s (id %s), "
                       "expected %s but found %r" %
                       (gobject.type_name(gtype),
                        prop.name,
                        obj_id,
                        gobject.type_name(pspec.value_type),
                        prop.data))
                continue
            
            # Could not
            if value is None:
                continue
            
            if pspec.flags & gobject.PARAM_CONSTRUCT_ONLY != 0:
                construct[pspec.name] = value
            else:
                normal.append((pspec.name, value))

        if child:
            assert not construct
            return normal
        
        return construct, normal

    def _valuefromstring(self, obj_id, pspec, string):
        # This is almost a 1:1 copy of glade_xml_set_value_from_string from
        # libglade. 
        prop_type = pspec.value_type
        if prop_type in (gobject.TYPE_CHAR, gobject.TYPE_UCHAR):
            value = string[0]
        elif prop_type == gobject.TYPE_BOOLEAN:
            value = str2bool(string)
        elif prop_type in (gobject.TYPE_INT, gobject.TYPE_UINT):
            if gobject.type_name(pspec) == 'GParamUnichar':
                value = unicode(string and string[0] or "")
            else:
                value = int(string)
        elif prop_type in (gobject.TYPE_LONG, gobject.TYPE_ULONG):
            value = long(string)
        elif gobject.type_is_a(prop_type, gobject.TYPE_ENUM):
            value = enumfromstring(string, pspec)
        elif gobject.type_is_a(prop_type, gobject.TYPE_FLAGS):
            value = flagsfromstring(string, pspec)
        elif prop_type in (gobject.TYPE_FLOAT, gobject.TYPE_DOUBLE):
            value = float(string)
        elif prop_type == gobject.TYPE_STRING:
            value = string
        elif gobject.type_is_a(prop_type, gobject.TYPE_PYOBJECT):
            value = string
        elif gobject.type_is_a(prop_type, gobject.GBoxed):
            print 'TODO: boxed'
            value = None
        elif gobject.type_is_a(prop_type, gobject.GObject):
            if gobject.type_is_a(prop_type, gtk.Adjustment):
                value = gtk.Adjustment(0, 0, 100, 1, 10, 10)
                (value.value, value.lower, value.upper,
                 value.step_increment, value.page_increment,
                 value.page_size) = map(float, string.split(' '))
            elif gobject.type_is_a(prop_type, gdk.Pixbuf):
                filename = self._build.find_resource(string)
                value = None
                if filename:
                    # XXX: Handle GError exceptions.
                    value = gdk.pixbuf_new_from_file(filename);
            elif (gobject.type_is_a(gtk.Widget, prop_type) or
                  gobject.type_is_a(prop_type, gtk.Widget)):
                value = self._build.get_widget(string)
                if value is None:
                    self._build.add_delayed_property(obj_id, pspec, string)
            else:
                value = None
        else:
            raise AssertionError("type %r is unknown" % prop_type)

        return value

    def add(self, parent, child, properties):
        raise NotImplementedError
    
    def find_internal_child(self, gobj, name):
        if name in self.child_names:
            return getattr(gobj, name)

    def get_internal_child_name(self, gobj, child):
        for child_name in self.child_names:
            if getattr(gobj, child_name) == child:
                return child_name
            
class UIManagerAdapter(GObjectAdapter):
    object_type = gtk.UIManager
    def add(self, parent, child, properties):
        parent.insert_action_group(child, 0)

class WidgetAdapter(GObjectAdapter):
    object_type = gtk.Widget
    def construct(self, name, gtype, properties):
        widget = GObjectAdapter.construct(self, name, gtype, properties)
        widget.set_name(name)
        return widget
    
    def prop_set_has_default(self, widget, value):
        value = str2bool(value)
        if value:
            self._build._default_widget = widget

    def prop_set_tooltip(self, widget, value):
        if isinstance(widget, gtk.ToolItem):
            # XXX: factor to separate Adapter
            widget.set_tooltip(self._build._tooltips, value, None)
        else:
            self._build._tooltips.set_tip(widget, value, None)

    def prop_set_visible(self, widget, value):
        value = str2bool(value)
        widget.set_data('gazpacho::visible', value)
        widget.set_property('visible', value)

    def prop_set_has_focus(self, widget, value):
        value = str2bool(value)
        if value:
            self._build._focus_widget = widget
        widget.set_data('gazpacho::has-focus', value)
    
    def prop_set_is_focus(self, widget, value):
        value = str2bool(value)
        widget.set_data('gazpacho::is-focus', value)
        
class PythonWidgetAdapter(WidgetAdapter):
    def construct(self, name, gtype, properties):
        obj = self.object_type()
        obj.set_name(name)
        return obj

class ContainerAdapter(WidgetAdapter):
    object_type = gtk.Container
    def add(self, container, child, properties):
        container.add(child)
        self._set_child_properties(container, child, properties)
        
    def _set_child_properties(self, container, child, properties):
        properties = self._getproperties(type(container),
                                         child.get_name(),
                                         properties,
                                         child=True)
        
        for name, value in properties:
            #print '%s.%s = %r (of %s)' % (child.get_name(), name, value,
            #                              gobj.get_name())
            container.child_set_property(child, name, value)

class ActionGroupAdapter(GObjectAdapter):
    object_type = gtk.ActionGroup
    def construct(self, name, gtype, properties):
        if not properties.has_key('name'):
            properties['name'] = name
        return GObjectAdapter.construct(self, name, gtype, properties)

    def add(self, parent, child, properties):
        accel_key = child.get_data('accel_key')
        if accel_key:
            accel_path = "<Actions>/%s/%s" % (parent.get_property('name'),
                                              child.get_name())
            accel_mod = child.get_data('accel_mod')
            gtk.accel_map_add_entry(accel_path, accel_key, accel_mod)
            child.set_accel_path(accel_path)
            child.set_accel_group(self._build.ensure_accel())
        parent.add_action(child)
            
class ActionAdapter(GObjectAdapter):
    object_type = gtk.Action
    def construct(self, name, gtype, properties):
        # Gazpacho doesn't save the name for actions
        # So we have set it manually.
        if not properties.has_key('name'):
            properties['name'] = name

        return GObjectAdapter.construct(self, name, gtype, properties)
        
    def prop_set_accelerator(self, action, value):
        stock_id = action.get_property('stock-id')
        accel_key = None
        if value:
            accel_key, accel_mod = gtk.accelerator_parse(value)
        elif stock_id:
            stock_item = gtk.stock_lookup(stock_id)
            accel_key = stock_item[3]
            accel_mod = stock_item[2]
            
        if not accel_key:
            return

        action.set_data('accel_key', accel_key)
        action.set_data('accel_mod', accel_mod)

    # This is for backwards compatibility
    def prop_set_callback(self, action, value):
        if value:
            self._build.add_signal(action, 'activate', value)
        
class PixmapAdapter(WidgetAdapter):
    object_type = gtk.Pixmap
    def prop_set_build_insensitive(self, pixmap, value):
        pixmap.set_build_insensitive(str2bool(value))

    def prop_set_filename(self, pixmap, value):
        filename = self._build.find_resource(value);
        if not filename:
            print 'No such a file or directory: %s' % value
            return
        
        try:
            pb = gdk.pixbuf_new_from_file(filename)
        except gobject.GError, e:
            print 'Error loading pixmap: %s' % e.message
            return
        except TypeError, e:
            print 'Error loading pixmap: %s' % e
            return

        cmap = pixmap.get_colormap()
        pix, bit = pb.render_pixmap_and_mask(127)
        pixmap.set(pix, bit)

class ProgressAdapter(WidgetAdapter):
    object_type = gtk.Progress
    def prop_set_format(self, progress, value):
        progress.set_format_string(value)

class ButtonAdapter(ContainerAdapter):
    object_type = gtk.Button
    def prop_set_response_id(self, button, value):
        button.set_data('response_id', int(value))

class OptionMenuAdapter(ButtonAdapter):
    object_type = gtk.OptionMenu
    def add(self, parent, child, properties):
        if not isinstance(child, gtk.Menu):
	    print ("warning: the child of the option menu '%s' was "
                   "not a GtkMenu"  % (child.get_name()))
            return
        
        parent.set_menu(child)
        self._set_child_properties(parent, child, properties)

    def prop_set_history(self, optionmenu, value):
        optionmenu.set_history(int(value))
        
class EntryAdapter(WidgetAdapter):
    object_type = gtk.Entry
    def prop_set_invisible_char(self, entry, value):
        entry.set_invisible_char(value[0])

class TextViewAdapter(ButtonAdapter):
    object_type = gtk.TextView
    def prop_set_text(self, textview, value):
        buffer = gtk.TextBuffer()
        buffer.set_text(value)
        textview.set_buffer(buffer)

class CalendarAdapter(WidgetAdapter):
    object_type = gtk.Calendar
    def prop_set_display_options(self, calendar, value):
        options = flagsfromstring(value, flags=gtk.CalendarDisplayOptions)
        calendar.display_options(options)

class WindowAdapter(ContainerAdapter):
    object_type = gtk.Window
    def prop_set_wmclass_name(self, window, value):
        window.set_wmclass(value, window.wmclass_class)
        
    def prop_set_wmclass_name(self, window, value):
        window.set_wmclass(value, window.wmclass_name)
   
    def prop_set_type_hint(self, window, value):
        window.set_data('gazpacho::type-hint', 
                        enumfromstring(value, enum=gdk.WindowTypeHint))

class NotebookAdapter(ContainerAdapter):
    object_type = gtk.Notebook
    def add(self, notebook, child, properties):
        tab_item = False
        for propinfo in properties[:]:
            if (propinfo.name == 'type' and
                propinfo.data == 'tab'):
                tab_item = True
                properties.remove(propinfo)
                break

	if tab_item:
            children = notebook.get_children()
	    body = notebook.get_nth_page(len(children) - 1)
	    notebook.set_tab_label(body, child)
        else:
            notebook.append_page(child)
 
        self._set_child_properties(notebook, child, properties)

class ExpanderAdapter(ContainerAdapter):
    object_type = gtk.Expander, gtk.Frame
    def add(self, expander, child, properties):
        label_item = False
        for propinfo in properties[:]:
            if (propinfo.name == 'type' and
                propinfo.data == 'label_item'):
                label_item = True
                properties.remove(propinfo)
                break

        if label_item:
	    expander.set_label_widget(child)
	else:
            expander.add(child)
            
        self._set_child_properties(expander, child, properties)

class MenuItemAdapter(ContainerAdapter):
    object_type = gtk.MenuItem
    def add(self, menuitem, child, properties):
        if isinstance(child, gtk.Menu):
            menuitem.set_submenu(child)
        else:
            print 'FIXME: Adding a %s to a %s' % (gobject.type_name(child),
                        gobject.type_name(self.object_type))
            # GtkWarning: Attempting to add a widget with type GtkImage to a GtkImageMenuItem, but as a GtkBin subclass a GtkImageMenuItem can only contain one widget at a time; it already contains a widget of type GtkAccelLabel'
            #menuitem.add(child)
            
        self._set_child_properties(menuitem, child, properties)

    def prop_set_label(self, menuitem, value):
        child = menuitem.child

        if not child:
            child = gtk.AccelLabel("")
            child.set_alignment(0.0, 0.5)
            menuitem.add(child)
            child.set_accel_widget(menuitem)
            child.show()

        if isinstance(child, gtk.Label):
            child.set_text(value)
        
    def prop_set_use_underline(self, menuitem, value):
        child = menuitem.child

        if not child:
            child = gtk.AccelLabel("")
            child.set_alignment(0.0, 0.5)
            menuitem.add(child)
            child.set_accel_widget(menuitem)
            child.show()

        if isinstance(child, gtk.Label):
            child.set_use_underline(str2bool(value))

    def prop_set_use_stock(self, menuitem, value):
        child = menuitem.child

        if not child:
            child = gtk.AccelLabel("")
            child.set_alignment(0.0, 0.5)
            menuitem.add(child)
            child.set_accel_widget(menuitem)
            child.show()

        value = str2bool(value)
        if not isinstance(child, gtk.Label) or not value:
            return

	stock_id = child.get_label()

        retval = gtk.stock_lookup(stock_id)
        if retval:
            name, label, modifier, keyval, _ = retval
	    # put in the stock image next to the text.  Done before
            # messing with the label child, so that stock_id doesn't
            # become invalid.
            if isinstance(menuitem, gtk.ImageMenuItem):
		image = gtk.image_new_from_stock(stock_id, gtk.ICON_SIZE_MENU)
                menuitem.set_image(image)
                image.show()

            child.set_text(label)
            child.set_use_underline(True)
            
            if keyval:
                # This triggers a segfault on exit (pachi.glade), weird
                accel_group = gtk.AccelGroup()
                menuitem.add_accelerator('activate',
                                         self._build.ensure_accel(),
                                         keyval, modifier,
                                         gtk.ACCEL_VISIBLE)
        else:
	    print "warning: could not look up stock id '%s'" % stock_id

class CheckMenuItemAdapter(MenuItemAdapter):
    object_type = gtk.CheckMenuItem
    def prop_set_always_show_toggle(self, check, value):
        check.set_show_toggle(value)

class RadioMenuItemAdapter(MenuItemAdapter):
    object_type = gtk.RadioMenuItem
    def prop_set_group(self, radio, value):
        group = self._build.get_widget(value)
        if not group:
            print "warning: Radio button group %s could not be found" % value
            return
        
        if group == radio:
            print "Group is self, skipping."
            return

        radio.set_group(group.get_group()[0])

class ImageMenuItemAdapter(MenuItemAdapter):
    object_type = gtk.ImageMenuItem
    def find_internal_child(self, menuitem, childname):
        if childname == 'image':
            pl = menuitem.get_image()
            if not pl:
                pl = gtk.Image()
                menuitem.set_image(pl)
            return pl
        return MenuItemAdapter.find_internal_child(self, menuitem, childname)
    
    def get_internal_child_name(self, parent, child):
        if parent.get_image() == child:
            return 'image'
        return MenuItemAdapter.get_internal_child_name(self, parent, child)
        
class ToolbarAdapter(ContainerAdapter):
    object_type = gtk.Toolbar
    def prop_set_tooltips(self, toolbar, value):
        toolbar.set_tooltips(str2bool(value))

class StatusbarAdapter(ContainerAdapter):
    object_type = gtk.Statusbar
    def prop_set_has_resize_grip(self, status, value):
        status.set_has_resize_grip(str2bool(value))

class RulerAdapter(WidgetAdapter):
    object_type = gtk.Ruler
    def prop_set_metric(self, ruler, value):
        ruler.set_metric(enumfromstring(value,
                                        enum=gtk.MetricType))

class ToolButtonAdapter(ContainerAdapter):
    object_type = gtk.ToolButton
    def prop_set_icon(self, toolbutton, value):
        filename = self._build.find_resource(value)
        pb = gdk.pixbuf_new_from_file(filename)
        if not pb:
            print "warning: Couldn't find image file: %s" %  value
            return

        image = gtk.image_new_from_pixbuf(pb)
        image.show()
        toolbutton.set_icon_widget(image)

class ToggleToolButtonAdapter(ToolButtonAdapter):
    object_type = gtk.ToggleToolButton
    def prop_set_active(self, toolbutton, value):
        toolbutton.set_active(str2bool(value))

class ComboBoxAdapter(ContainerAdapter):
    # FIXME: Internal child: entry -> get_child()
    object_type = gtk.ComboBox, gtk.ComboBoxEntry
    def prop_set_items(self, combobox, value):
        # If the "items" property is set, we create a simple model with just
        # one column of text.
        store = gtk.ListStore(str)
        combobox.set_model(store)

        # GtkComboBoxEntry creates the cell renderer itself, but we have to set
        # the column containing the text.
        if isinstance(combobox, gtk.ComboBoxEntry):
            if combobox.get_text_column() == -1:
                combobox.set_text_column(0)
        else:
            cell = gtk.CellRendererText()
            combobox.pack_start(cell, True)
            combobox.set_attributes(cell, text=0)

        for part in value.split('\n'):
            store.append([part])

# FIXME: PyGTK does not expose vscrollbar and hscrollbar.
#
#class ScrolledWindowAdapter(WindowAdapter):
#    child_names = ['vscrollbar', 'hscrollbar']
#    object_type = gtk.ScrolledWindow
#    def get_internal_child_name(self, parent, child):
#        if parent.vscrollbar == child:
#            return 'vscrollbar'
#        elif parent.hscrollbar == child:
#            return 'hscrollbar'
#        return WindowAdapter.get_internal_child_name(self, parent, child)
    
class DialogAdapter(WindowAdapter):
    child_names = ['vbox', 'action_area']
    object_type = gtk.Dialog
    def get_internal_child_name(self, parent, child):
        if parent.vbox == child:
            return 'vbox'
        elif parent.action_area == child:
            return 'action_area'
        return WindowAdapter.get_internal_child_name(self, parent, child)
    
class ColorSelectionDialogAdapter(DialogAdapter):
    child_names = DialogAdapter.child_names + ['ok_button',
                                               'cancel_button',
                                               'help_button',
                                               'colorsel']
    object_type = gtk.ColorSelectionDialog
    def find_internal_child(self, gobj, name):
        if name == 'color_selection':
            return gobj.colorsel
        
        return DialogAdapter.find_internal_child(self, gobj, name)

    def get_internal_child_name(self, parent, child):
        if parent.colorsel == child:
            return 'color_selection'
        return DialogAdapter.get_internal_child_name(self, parent, child)

class FontSelectionDialogAdapter(DialogAdapter):
    object_type = gtk.FontSelectionDialog
    child_names = DialogAdapter.child_names + ['ok_button',
                                               'cancel_button',
                                               'apply_button',
                                               'fontsel']
    def find_internal_child(self, gobj, name):
        if name == 'font_selection':
            return gobj.fontsel
        
        return DialogAdapter.find_internal_child(self, gobj, name)

    def get_internal_child_name(self, parent, child):
        if parent.fontsel == child:
            return 'font_selection'
        return DialogAdapter.get_internal_child_name(self, parent, child)
    
class TreeViewAdapter(ContainerAdapter):
    object_type = gtk.TreeView
    def add(self, treeview, child, properties):
        if not isinstance(child, gtk.TreeViewColumn):
            raise TypeError("Children of GtkTreeView must be a "
                            "GtkTreeViewColumns, not %r" % child)

        treeview.append_column(child)

        # Don't chain to Container add since children are not widgets
        
class TreeViewColumnAdapter(GObjectAdapter):
    object_type = gtk.TreeViewColumn
    
    def add(self, column, child, properties):
        if not isinstance(child, gtk.CellRenderer):
            raise TypeError("Children of GtkTreeViewColumn must be a "
                            "GtkCellRenderers, not %r" % child)

        expand = True
        pack_start = True
        for propinfo in properties[:]:
            name = propinfo.name
            if name == 'expand':
                expand = str2bool(propinfo.data)
                properties.remove(propinfo)
            elif name == 'pack_start':
                pack_start = str2bool(propinfo.data)
                properties.remove(propinfo)
            else:
                raise AssertionError("Unknown property for "
                                     "GtkTreeViewColumn: %s" % name)
        if pack_start:
            column.pack_start(child, expand)
        else:
            column.pack_end(child, expand)

# Gross hack to make it possible to use FileChooserDialog on win32.
# See bug http://bugzilla.gnome.org/show_bug.cgi?id=314527
class FileChooserDialogAdapter(DialogAdapter):
    object_type = type('FileChooserDialogHack',
                       (gtk.FileChooserDialog,),
                       {'get_children': lambda self: []})
    gobject.type_register(object_type)
    
# Global registry
adapter_registry = AdapterRegistry()


if __name__ == '__main__':
    import sys
    ob = ObjectBuilder(filename=sys.argv[1])
    for toplevel in ob.toplevels:
        if not isinstance(toplevel, gtk.Window):
            continue
        toplevel.connect('delete-event', gtk.main_quit)
        toplevel.show_all()
        
    gtk.main()
