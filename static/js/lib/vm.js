/**
 * Created by khoroshenkikh on 29.05.17.
 */

var applyViewModel = function() {
    var self = this;

    self.storages = [
        ExampleStorage,
        DropboxStorage
    ];

    self.selectedStorage = ko.observable(EmptyStorage);
    self.selectedDirectoryPath = ko.observable('/');
    self.selectedFilePath = ko.observable('');
    self.accessUrl = ko.observable(undefined);

    self.selectStorage = function (data, event) {
        self.selectedStorage(data);
        var url = self.selectedStorage().accessStorage();
        self.accessUrl(url);
    };

    self.isActiveSaveButton = ko.computed(function () {
        return !(self.selectedStorage().createFile === undefined);
    });

    self.isActiveOpenButton = ko.computed(function () {
        return !(self.selectedStorage().accessStorage === undefined);
    });

    self.listDirectory = ko.observable();  // Storage listDirectory returns Promise
    ko.computed(function () {
        var st = self.selectedStorage();
        if (st.listDirectory) {
            st.listDirectory(self.selectedDirectoryPath())
                .then(function(l) {
                    self.listDirectory(l);
                });
        }
    }, self);

    self.selectInDirectory = function (data, event) {
        if (data._type === 'file') {
            self.selectedFilePath(data.path);
            var st = self.selectedStorage();
            if (st.readFile) {
                st.readFile(self.selectedFilePath())
                    .then(function(c) {
                        self.graphText(c);
                    });
            }
        } else if (data._type === 'directory') {
            self.selectedDirectoryPath(data.path);
        }
    };

    self.selectParentDirectory = function (data, event) {
        self.selectedDirectoryPath(self.parentDirectory().path);
    };

    self.selectCurrentDirectory = function (data, event) {
        self.selectedDirectoryPath(data.path);
    };

    self.parentDirectory = ko.computed(function () {
        var st = self.selectedStorage();
        var filePath = self.selectedFilePath();
        var dirPath = self.selectedDirectoryPath();
        return st.getParentDirectory(dirPath || filePath);
    });

    self.parentDirectorySequence = ko.computed(function () {
        var st = self.selectedStorage();

        var sequence = [];
        var parentDir = self.parentDirectory();
        while ((typeof parentDir !== 'undefined') && sequence.length < 128) {
            sequence.unshift(parentDir);
            parentDir = st.getParentDirectory(parentDir.path);
        }
        return sequence;
    });

    self.graphText = ko.observable("");

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