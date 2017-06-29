/**
 * Created by khoroshenkikh on 29.06.17.
 */

var DropboxStorage = new BaseStorage();

DropboxStorage.name = "Dropbox";
DropboxStorage._dbx = new Dropbox({ clientId: 'gs3i8fg9vy0t6p0' });

DropboxStorage.accessStorage = function () {
    var self = this;
    console.log(self._dbx.getAuthenticationUrl('http://127.0.0.1:5000/'));
};