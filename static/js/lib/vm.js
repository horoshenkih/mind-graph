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
    self.selectedDirectory = ko.observable({});
    self.selectedFile = ko.observable({});
    self.selectedFileName = ko.observable('');
    self.accessUrl = ko.observable(undefined);

    self.selectStorage = function (data, event) {
        self.selectedStorage(data);
        var st = self.selectedStorage();
        self.selectedDirectory(st.rootDirectory());
        var url = st.accessStorage();
        self.accessUrl(url);
    };

    self.isActiveSaveButton = ko.computed(function () {
        return !(self.selectedStorage().writeFile === undefined);
    });

    self.isActiveSaveAsButton = ko.computed(function () {
        return !(self.selectedStorage().createFile === undefined) && !(self.selectedStorage().writeFile === undefined);
    });

    self.isActiveOpenButton = ko.computed(function () {
        return !(self.selectedStorage().accessStorage === undefined);
    });

    self.listDirectory = ko.observable();  // Storage listDirectory returns Promise
    ko.computed(function () {
        var st = self.selectedStorage();
        if (st.listDirectory) {
            st.listDirectory(self.selectedDirectory())
                .then(function(l) {
                    self.listDirectory(l);
                });
        }
    }, self);

    self.selectInDirectory = function (data, event) {
        if (data._type === 'file') {
            self.selectedFile(data);
            var st = self.selectedStorage();
            if (st.readFile) {
                st.readFile(self.selectedFile().path)
                    .then(function(c) {
                        self.graphText(c);
                    });
            }
        } else if (data._type === 'directory') {
            self.selectedDirectory(data);
        }
    };

    self.selectParentDirectory = function (data, event) {
        self.selectedDirectory(self.parentDirectory());
    };

    self.selectCurrentDirectory = function (data, event) {
        self.selectedDirectory(data);
    };

    self.parentDirectory = ko.computed(function () {
        var st = self.selectedStorage();
        var file = self.selectedFile();
        var dir = self.selectedDirectory();
        return st.getParentDirectory(dir || file);
    });

    self.parentDirectorySequence = ko.computed(function () {
        var st = self.selectedStorage();

        var sequence = [];
        var parentDir = self.parentDirectory();
        while ((typeof parentDir !== 'undefined') && sequence.length < 128) {
            sequence.unshift(parentDir);
            parentDir = st.getParentDirectory(parentDir);
        }
        return sequence;
    });

    self.saveFile = function (data, event) {
        var st = self.selectedStorage();
        if (st.writeFile) {
            st.writeFile(self.selectedFile().path, self.graphText())
                .then(function(m) {
                    console.log(m);
                });
        }
    };

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