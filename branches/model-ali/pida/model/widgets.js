
// import Nevow.Athena

var WidgetDemo = {};

WidgetDemo.Entry = Nevow.Athena.Widget.subclass('WidgetDemo.Entry');
WidgetDemo.Entry.methods(
    function changed(self, node, event) {
        var entry = Nevow.Athena.NodeByAttribute(self.node, "class",
                                                            "model-entry");
        /* self.callRemote('change', entry.value); */
        function foo () {
            self.callRemote('value_changed', entry.value);
        }
        MochiKit.Async.callLater(0, foo);
        return true;
    },
    function setValue(self, toWhat) {
        var w = Nevow.Athena.NodeByAttribute(self.node, "class", "model-entry");
        w.value = toWhat;
    });

WidgetDemo.CheckBox = Nevow.Athena.Widget.subclass('WidgetDemo.CheckBox');
WidgetDemo.CheckBox.methods(
    function changed(self, node, event) {
        var check = Nevow.Athena.NodeByAttribute(self.node, "class",
                                                            "model-checkbox");
        /* self.callRemote('change', entry.value); */
        function foo () {
            self.callRemote('value_changed', check.checked);
        }
        MochiKit.Async.callLater(0, foo);
        return true;
    },
    function setValue(self, toWhat) {
        var w = Nevow.Athena.NodeByAttribute(self.node, "class",
        "model-checkbox");
        w.checked = toWhat;
    });


WidgetDemo.OptionList = Nevow.Athena.Widget.subclass('WidgetDemo.OptionList');
WidgetDemo.OptionList.methods(
    function changed(self, node, event) {
        var radios = self.nodesByAttribute("class", "model-radio");
        /* self.callRemote('change', entry.value); */
        for (r in radios) {
            var radio = radios[r];
            function change () {
                MochiKit.Async.callLater(0, change);
            }
            if (radio.checked) {
                self.callRemote('value_changed', radio.value);
                 
            }
        }
        return true;
    },
    function setValue(self, toWhat) {
        var radios = self.nodesByAttribute("class", "model-radio");
        for (r in radios) {
            var radio = radios[r];
            if (radio.value == toWhat) {
                radio.checked = true;
            }
        }
    });



WidgetDemo.List = Nevow.Athena.Widget.subclass('WidgetDemo.List');
WidgetDemo.List.methods(
    function changed(self, node, event) {
        var label = event.target;
        self.callRemote('value_changed', event.target.id);
        self.setValue(event.target.id);
        return true;
    },
    function setValue(self, toWhat) {
        var labels = self.nodesByAttribute("class", "tree-label");
        for (l in labels) {
            var label = labels[l];
            label.style.fontWeight = 'normal';
        }
        var sellabel = self.nodesByAttribute("id", toWhat);
        if (sellabel.length > 0) {
            sellabel[0].style.fontWeight = 'bold';
        }
    });


WidgetDemo.Label = Nevow.Athena.Widget.subclass('WidgetDemo.Label;');
WidgetDemo.Label.methods(
    function setValue(self, toWhat) {
        var label = self.nodesByAttribute("class", "tree-label")[0];
        label.innerHTML = toWhat;
    });
WidgetDemo.Clock = Nevow.Athena.Widget.subclass('WidgetDemo.Clock');
WidgetDemo.Clock.methods(
    function start(self, node, event) {
        self.callRemote('start');
        return false;
    },

    function stop(self, node, event) {
        self.callRemote('stop');
        return false;
    },

    function change(self, node, event) {
        var entry = Nevow.Athena.NodeByAttribute(self.node, "id", "i");
        alert(node)
        /* self.callRemote('change', entry.value); */
        function foo () {
            self.callRemote('change', entry.value);
        }
        MochiKit.Async.callLater(0, foo);
        return true;
    },

    function setTime(self, toWhat) {
        Divmod.debug("clock", "Setting time " + toWhat);
        var time = Nevow.Athena.NodeByAttribute(self.node, "class", "clock-time");
        Divmod.debug("clock", "On " + time);
        time.innerHTML = toWhat;
        Divmod.debug("clock", "Hooray");
    });
