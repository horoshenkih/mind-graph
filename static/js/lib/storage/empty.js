/**
 * Created by khoroshenkikh on 29.06.17.
 */

var EmptyFile = new BaseFile(undefined, "ko .is framework\nko {http://knockoutjs.com/}");
// var RootDirectory = new BaseDirectory('/', undefined);

var EmptyStorage = new BaseStorage();
EmptyStorage.accessStorage = undefined;
EmptyStorage.createDirectory = undefined;
EmptyStorage.listDirectory = undefined;
EmptyStorage.createFile = undefined;