/**
 * Created by khoroshenkikh on 01.06.17.
 */

function normalizePath(path) {
    return path.replace(/\/+/g, '/');
}

// prototypes
function BaseFile(path, content) {
    return {
        _type: 'file',
        path: path,
        content: content
    };
}

function BaseDirectory(path, contentNames) {
    return {
        _type: 'directory',
        path: path,
        contentNames: contentNames
    }
}

function BaseStorage() {
    return {
        name: undefined,
        accessStorage: function () {},

        createDirectory: function (directory) {},
        listDirectory: function (directory) {},

        createFile: function (filePath) {},
        readFile: function (filePath) {},
        writeFile: function (filePath) {}
    };
}

// implementations
///////////////////////////////////
var EmptyFile = new BaseFile(undefined, "ko .is framework\nko {http://knockoutjs.com/}");
// var RootDirectory = new BaseDirectory('/', undefined);

var EmptyStorage = new BaseStorage();
EmptyStorage.accessStorage = undefined;
EmptyStorage.createDirectory = undefined;
EmptyStorage.listDirectory = undefined;
EmptyStorage.createFile = undefined;

//////////////////////////////////////
var ExampleStorage = new BaseStorage();
ExampleStorage.name = "Examples";

// data
ExampleStorage._examples = {
    "Basic examples": {
        1: "a, b .is c"
    },
    "Advanced examples": {
        1: "a {\
        # Markdown header\
        }\
        a .is b"
    }
};


ExampleStorage._files = {};  // path -> object
ExampleStorage._accessed = false;

ExampleStorage.accessStorage = function () {
    var self = this;

    var fringe = [[]];

    // traverse
    while(fringe.length) {
        var pathToTraverse = fringe.shift();

        var currentContent = self._examples;
        for (i in pathToTraverse) {
            var key_name = pathToTraverse[i];
            currentContent = currentContent[key_name];
        }

        var pathStr = '/' + pathToTraverse.join('/');
        if (typeof currentContent === 'string') {
            // file
            self._files[pathStr] = new BaseFile(pathStr, currentContent);
        } else if (typeof currentContent === 'object') {
            // directory
            self._files[pathStr] = new BaseDirectory(pathStr, Object.keys(currentContent));
            for (j in currentContent) {
                var currentPath = pathToTraverse.concat([j]);
                var currentPathStr = '/' + currentPath.join('/');
                var value = currentContent[j];

                self._files[currentPathStr] = new BaseDirectory(currentPathStr, value);
                // need to go deeper
                fringe.push(currentPath);
            }
        }
    }
    self._accessed = true;
};

ExampleStorage.listDirectory = function (directoryPath) {
    if (!this._accessed) {
        this.accessStorage();
    }
    directoryPath = normalizePath(directoryPath);
    var storageItem = this._files[directoryPath];
    var content = [];
    if (storageItem && storageItem._type === 'directory') {
        for (i in storageItem.contentNames) {
            var subItem = storageItem.contentNames[i];
            var subItemPath = normalizePath(directoryPath + '/' + subItem);
            var subItemFile = this._files[subItemPath];
            if (subItemFile) {
                content.push(subItemFile);
            }
        }
    }
    return content;
};

ExampleStorage.readFile = function (filePath) {
    if (!this._accessed) {
        this.accessStorage();
    }
    filePath = normalizePath(filePath);
    var storageItem = this._files[filePath];
    if (storageItem && storageItem._type === 'file') {
        return storageItem.content;
    }
};

ExampleStorage.createDirectory = undefined;
ExampleStorage.createFile = undefined;
ExampleStorage.writeFile = undefined;

var storages = [
    ExampleStorage
];