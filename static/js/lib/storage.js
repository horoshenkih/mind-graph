/**
 * Created by khoroshenkikh on 01.06.17.
 */

// prototypes
function BaseFile() {
    return {
        name: undefined,
        parentDirectory: undefined,
        content: undefined,
        read: function () {
            return this.content;
        },
        write: function (newContent) {
            this.content = newContent;
        }
    };
}

// var Directory = undefined;
function BaseStorage() {
    return {
        name: undefined,
            accessStorage: function () {},

        createDirectory: function (currentDirectory) {},
        listDirectory: function (currentDirectory) {},

        createFile: function (directory, filename) {}
    };
}

// implementations
var EmptyStorage = new BaseStorage();
EmptyStorage.accessStorage = undefined;
EmptyStorage.createDirectory = undefined;
EmptyStorage.listDirectory = undefined;
EmptyStorage.createFile = undefined;

var ExampleStorage = new BaseStorage();
ExampleStorage.name = "Examples";
ExampleStorage.createDirectory = undefined;
ExampleStorage.listDirectory = function (currentDirectory) {
    if (currentDirectory !== 'examples_directory') {
        return [];
    }
    files = [];
    for (name in this.examples_directory) {
        var f = new BaseFile();
        f.name = name;
        f.parentDirectory = currentDirectory;
        f.content = this.examples_directory[name];
        files.push(f);
    }
    return files;
};
ExampleStorage.createFile = undefined;
ExampleStorage.readFile = undefined;
ExampleStorage.writeFile = undefined;

// data
ExampleStorage.examples_directory = {
    basic: "a, b .is c"
};

var storages = [
    ExampleStorage
];