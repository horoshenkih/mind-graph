/**
 * Created by khoroshenkikh on 29.05.17.
 */
var applyViewModel = function() {
    var self = this;

    self.graphText = ko.observable("ko .is framework\nko {http://knockoutjs.com/}");

    self.graph = ko.computed(function () {
        var input_text = self.graphText();
        $.getJSON('/get_graph', { input_text: input_text }, function (input_data) {
            self.graph = MindGraph.init(input_data);
        });
    });

    self.computeNetwork = function () {
        if (self.graph) { self.graph.createNetwork('network') }
    };

    self.updateNodeInfo = function () {
        if (self.graph) { document.getElementById('nodeInfo').innerHTML = self.graph.getSelectedNodeInfo() }
    };

    self.storages = storages;
    self.selectedStorage = ko.observable(EmptyStorage);

    self.selectStorage = function (data, event) {
        self.selectedStorage(data);
    };

    self.isActiveSaveButton = ko.computed(function () {
        return !(self.selectedStorage().createFile === undefined);
    });

    self.isActiveOpenButton = ko.computed(function () {
        return !(self.selectedStorage().accessStorage === undefined);
    });
};

ko.applyBindings(new applyViewModel());