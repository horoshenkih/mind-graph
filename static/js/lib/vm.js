/**
 * Created by khoroshenkikh on 29.05.17.
 */
var applyViewModel = function() {
    var self = this;

    self.storages = storages;
    self.selectedStorage = ko.observable(EmptyStorage);
    self.selectedDirectoryPath = ko.observable('/');
    self.selectedFilePath = ko.observable('');

    self.selectStorage = function (data, event) {
        self.selectedStorage(data);
        self.selectedStorage().accessStorage();
    };

    self.isActiveSaveButton = ko.computed(function () {
        return !(self.selectedStorage().createFile === undefined);
    });

    self.isActiveOpenButton = ko.computed(function () {
        return !(self.selectedStorage().accessStorage === undefined);
    });

    self.listDirectory = ko.computed(function () {
        var st = self.selectedStorage();
        if (st.listDirectory) {
            return st.listDirectory(self.selectedDirectoryPath());
        }
    });

    self.selectInDirectory = function (data, event) {
        if (data._type === 'file') {
            self.selectedFilePath(data.path);
        } else if (data._type === 'directory') {
            self.selectedDirectoryPath(data.path);
        }
    };

    // self.graphText = ko.observable("ko .is framework\nko {http://knockoutjs.com/}");
    self.graphText = ko.computed(function () {
        var st = self.selectedStorage();
        if (st.readFile) {
            return st.readFile(self.selectedFilePath());
        }
    });

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
};

ko.applyBindings(new applyViewModel());