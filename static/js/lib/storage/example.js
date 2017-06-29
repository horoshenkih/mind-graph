/**
 * Created by khoroshenkikh on 29.06.17.
 */
function normalizePath(path) {
    if (typeof path === 'undefined') {
        return undefined;
    }
    return path.replace(/\/+/g, '/');
}

var ExampleStorage = new BaseStorage();
ExampleStorage.name = "Examples";

ExampleStorage._examples = {
    "Basic examples": {
        "Terms": "a .is b\nterm One .isRelatedTo term Two",
        "Relations": "a .is b",
        "More examples": {
            "Enumeration of terms": "a, b .is c"
        }
    },
    "Advanced examples": {
        "markdown": "a {\n    # Markdown header\n}\na .is b"
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
    if (!this._accessed) { this.accessStorage(); }
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

ExampleStorage.getParentDirectory = function (path) {
    if (!this._accessed) { this.accessStorage(); }

    path = normalizePath(path);
    if (typeof path === 'undefined' || path === '/') {
        return undefined;
    }

    var items = path.split('/');
    items.pop();

    if (items.length === 1 && items[0] === '') {
        return this._files['/'];
    }

    var parentPath = items.join('/');
    return this._files[parentPath];
};

ExampleStorage.readFile = function (filePath) {
    if (!this._accessed) { this.accessStorage(); }
    filePath = normalizePath(filePath);
    var storageItem = this._files[filePath];
    if (storageItem && storageItem._type === 'file') {
        return storageItem.content;
    }
};

ExampleStorage.createDirectory = undefined;
ExampleStorage.createFile = undefined;
ExampleStorage.writeFile = undefined;