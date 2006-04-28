import time, os, sys

from twisted.internet import task
from twisted.python import log, util

from nevow import athena, loaders, static, appserver,inevow,  tags as T

from model import Model, BaseSingleModelObserver, BaseMultiModelObserver,\
                  ModelGroup
from exampleschema import AddressDefinition

# Creates a model class
Address = Model.__model_from_definition__(AddressDefinition)
from persistency import IniFileObserver, load_model_from_ini
import attrtypes as types

class Widget(athena.LiveFragment):


    docFactory = loaders.xmlstr('''\
<div xmlns:nevow="http://nevow.com/ns/nevow/0.1"
     xmlns:athena="http://divmod.org/ns/athena/0.7"
     nevow:render="liveFragment">
     <div nevow:render="label" />
     <div nevow:render="widget">
     </div>
</div>
''')

    def set_model_attr(self, attr):
        self._model_attr = attr

    def set_changed_callback(self, cb):
        self._changed_callback = cb

    def set_value(self, value):
        self.callRemote('setValue', value).addErrback(self._oops)

    def value_changed(self, value):
        self._changed_callback(self._model_attr, value)
    athena.expose(value_changed)

    def render_label(self, ctx, data):
        if self.label:
            return T.div(class_="model-widget-label")[self.label]
        else:
            return ctx.tag

    def _oops(self, err):
        log.err(err)

class Entry(Widget):

    jsClass = u'WidgetDemo.Entry'

    def render_widget(self, ctx, data):
        return ctx.tag[
                T.input(type='text', class_='model-entry')[
                    athena.handler(event='onkeydown', handler='changed')
                ]
                ]

class CheckBox(Widget):

    jsClass = u'WidgetDemo.CheckBox'
    
    def render_widget(self, ctx, data):
        return ctx.tag[
                T.input(type='checkbox', class_='model-checkbox')[
                    athena.handler(event='onclick', handler='changed')
                ]
                ]

class OptionList(Widget):

    jsClass = u'WidgetDemo.OptionList'
    
    def render_widget(self, ctx, data):
        radios = []
        def _radios():
            for choice in data.rtype.choices:
                yield T.label(for_=choice)[choice]
                yield T.input(type='radio', name='model-radio-%s' % hash(self),
                        value=choice, class_='model-radio')[
                        athena.handler(event='onclick', handler='changed')
                              ]
                yield T.br
        return ctx.tag[_radios()]

class Label(Widget):

    jsClass = u'WidgetDemo.Label'
    label = ''

    def render_widget(self, ctx, data):
        return T.div(id=data, class_='tree-label')['loading...']

class List(Widget):

    jsClass = u'WidgetDemo.List'

    def __init__(self):
        super(List, self).__init__()
        self._items = []
        self._models = []
        self._labels = {}
        self.label = 'Select a person'

    def add_item(self, item):
        k = unicode(str(hash(item)), 'ascii')
        self._models.append(item)
        self._labels[k] = Label(k)
        self._labels[k].page = self.page
        i = T.span(id=u'_%s' % k, style='{cursor: pointer}')[
                athena.handler(event='onclick', handler='changed'),
                self._labels[k]]
        self._items.append(i)

    def render_widget(self, ctx, data):
        yield ctx.tag[self._items]
        for model in self._models:
            model.__model_notify__()

    def set_label(self, model, value):
        k = unicode(str(hash(model)), 'ascii')
        self._labels[k].set_value(u'%s' % value)

def get_widget_for_type(attr):
    rtype = attr.rtype
    if rtype is types.boolean:
        return CheckBox()
    elif rtype.__name__ == 'stringlist':
        return OptionList(attr)
    else:
        return Entry()

class WidgetPage(athena.LivePage):
    docFactory = loaders.xmlstr("""\
<html xmlns:nevow="http://nevow.com/ns/nevow/0.1">
    <head>
        <nevow:invisible nevow:render="liveglue" />
    </head>
    <body style="{width: 600px;}">
        <div nevow:render="entry">
            First Clock
        </div>
        <div nevow:render="debug" />
    </body>
</html>
""")

    addSlash = True

    def __init__(self, *a, **kw):
        super(WidgetPage, self).__init__(*a, **kw)
        self.jsModules.mapping[u'WidgetDemo'] = util.sibpath(__file__, 'widgets.js')

    def childFactory(self, ctx, name):
        ch = super(WidgetPage, self).childFactory(ctx, name)
        if ch is None:
            p = util.sibpath(__file__, name)
            if os.path.exists(p):
                ch = static.File(file(p))
        return ch

    def render_entry(self, ctx, data):
        e = Entry()
        e.page = self
        return ctx.tag[e]

    def render_debug(self, ctx, data):
        f = athena.IntrospectionFragment()
        f.setFragmentParent(self)
        return ctx.tag[f]

class ElementObserver(BaseSingleModelObserver):

    def set_parent_page(self, page):
        self.page = page

    def setup_with_model(self, model):
        self._widgets = []
        self._model_widgets = {}
        for group, doc, label, stock_id, attrs in model.__model_groups__:
            self.add_group(label, doc)
            for attrkey in attrs:
                attr = model.__model_attrs_map__[attrkey]
                widget = get_widget_for_type(attr)
                self.add_widget(attrkey, widget, attr.label)
            self._widgets.append(T.hr)

    def add_group(self, label, doc):
        self._widgets.append(T.h2[label])
        self._widgets.append(T.h4[doc])

    def add_widget(self, attr, widget, label):
        self._widgets.append(widget)
        widget.page = self.page
        widget.set_changed_callback(self.cb_widget_changed)
        widget.set_model_attr(attr)
        widget.label = label
        self._model_widgets.setdefault(attr, set()).add(widget)

    def cb_widget_changed(self, attr, value):
        self.update_model(attr, value)

    def __model_notify__(self, model, attr, value):
        for widget in self._model_widgets[attr]:
            if isinstance(value, str):
                value = unicode(value, 'ascii')
            widget.set_value(value)

    def render(self):
        for widget in self._widgets:
            yield widget

class TreeObserver(BaseMultiModelObserver):

    def __init__(self, *a, **kw):
        super(TreeObserver, self).__init__(*a, **kw)
        self.tree = List()
        self.tree.set_changed_callback(self.cb_widget_changed)
        self.tree.set_model_attr('')
        self._models = {}

    def set_parent_page(self, page):
        self.page = page
        self.tree.page = self.page

    def add_model(self, model):
        super(TreeObserver, self).add_model(model)
        self.tree.add_item(model)
        self._models[unicode(str(hash(model)), 'ascii')] = model

    def render(self):
        return self.tree

    def cb_widget_changed(self, attr, value):
        self.current_callback(self._models[value])

    def __model_notify__(self, model, attr, value):
        self.tree.set_label(model, model.__model_markup__)

class PropertyPage(WidgetPage):

    docFactory = loaders.xmlstr("""\
<html xmlns:nevow="http://nevow.com/ns/nevow/0.1">
    <head>
        <nevow:invisible nevow:render="liveglue" />
        <style>
            body {font-family: sans; width: 800px;
                  margin-left: auto; margin-right: auto;}
            td {vertical-align: top}

            #main {position: relative;
                   top: 50px; width 800px;}
            #bar {position: absolute; width: 300px}
            #item {position: absolute; left: 300px}

            .model-widget-label {
                font-size: small;
                font-weight: bold;
                margin-top: 0.7em;
                }

            .tree-label {
                cursor: pointer;
                font-size: 2em;
            }
        </style>
    </head>
    <body>
        <div id="main">
        <div nevow:render="list" />
        <div nevow:render="item" />
        </div>
    </body>
</html>
""")
    def __init__(self, *a, **kw):
        super(PropertyPage, self).__init__(*a, **kw)
        mg = ModelGroup()
        self.mo = mg.create_multi_observer(TreeObserver)
        self.mo.set_parent_page(self)
        rootp = '/tmp/address_a-%s'
        self.a1 = Address()
        self.a2 = Address()
        self.a3 = Address()
        for i, a in enumerate([self.a1, self.a2, self.a3]):
            load_model_from_ini(rootp % i, a)
            mg.add_model(a)
        self.p = mg.create_multi_observer(IniFileObserver)
        self.o = mg.create_single_observer(ElementObserver)
        self.o.set_parent_page(self)
        self.o.setup_with_model(Address())

    def render_list(self, ctx, data):
        yield T.div(id="bar")[self.mo.render()]

    def render_item(self, ctx, data):
        yield T.div(id="item")[self.o.render()]

    def set_model(self, model):
        self.o.set_model(model)

from zope.interface import implements, Interface

class Fake(object):
    pass

if __name__ == '__main__':
    from twisted.application import service, internet
    #application = service.Application('helloworld')
    def propertyResourceFactory(original):
        return PropertyPage()

    from twisted.python.components import registerAdapter
    from twisted.internet import reactor
    registerAdapter(propertyResourceFactory, Fake, inevow.IResource)

    #log.startLogging(sys.stdout)
    site = appserver.NevowSite(Fake())
    reactor.listenTCP(8080, site, interface='')
    reactor.run()

