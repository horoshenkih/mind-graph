/**
 * Created by khoroshenkikh on 01.06.17.
 */

function baseName(path) {
    if (typeof path === 'undefined') {
        return undefined;
    }
    return path.split('/').pop();
}

// prototypes
function BaseFile(path, content) {
    return {
        _type: 'file',
        path: path,
        content: content,
        name: baseName(path)
    };
}

function BaseDirectory(path, contentNames) {
    return {
        _type: 'directory',
        path: path,
        contentNames: contentNames,
        name: baseName(path)
    }
}

function BaseStorage() {
    return {
        name: undefined,
        rootDirectory: function () { return BaseDirectory(undefined, undefined); },
        accessStorage: function () {},

        createDirectory: function (directory) {},
        listDirectory: function (directory) {},

        getParentDirectory: function(obj) { return undefined; },

        createFile: function (filePath) {},
        readFile: function (filePath) {},
        writeFile: function (filePath) {}
    };
}