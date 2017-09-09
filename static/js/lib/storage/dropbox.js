/**
 * Created by khoroshenkikh on 29.06.17.
 */

var DropboxStorage = new BaseStorage();
function DropboxFile(dbxEntry) {
    return {
        _type: 'file',
        path: dbxEntry.id,
        name: dbxEntry.name
    }
}

DropboxStorage.name = "Dropbox";
var CLIENT_ID = 'gs3i8fg9vy0t6p0';
DropboxStorage._accessed = false;
DropboxStorage._dbx = new Dropbox({clientId: CLIENT_ID});

DropboxStorage.accessStorage = function () {
    var self = this;
    if (self._accessed) {
        return undefined;
    }

    var accessToken = utils.parseQueryString(window.location.hash).access_token;
    if (accessToken) {
        self._dbx = new Dropbox({accessToken: accessToken});
        self._accessed = true;
        return undefined;
    }

    return self._dbx.getAuthenticationUrl(window.location.origin+'/');
};

DropboxStorage.listDirectory = function (directoryPath) {
    var self = this;
    if (!self._accessed) { self.accessStorage(); }
    directoryPath = directoryPath.replace(/^\/+/, '');

    return new Promise(function (resolve, reject) {
        var content = [];

        self._dbx.filesListFolder({path: directoryPath})
            .then(function (response) {
                for (e in response.entries) {
                    var entry = response.entries[e];
                    if (entry['.tag'] === 'file') {
                        content.push(new DropboxFile(entry));
                    } else if (entry['.tag'] === 'folder') {
                        content.push(new BaseDirectory(entry.path_display, undefined));
                    }
                }
                resolve(content);
            });
    });
};

DropboxStorage.readFile = function (filePath) {
    var self = this;
    if (!self._accessed) { self.accessStorage(); }
    // console.log(filePath);
    return new Promise(function (resolve, reject) {
        var content = "";
        self._dbx.filesDownload({path: filePath})
            .then(function(data) {
                var blob = data.fileBlob;
                var reader = new FileReader();
                reader.addEventListener("loadend", function () {
                    resolve(reader.result);
                });
                reader.readAsText(blob);
            })
    })
};

(function(window){
    window.utils = {
        parseQueryString: function(str) {
            var ret = Object.create(null);

            if (typeof str !== 'string') {
                return ret;
            }

            str = str.trim().replace(/^(\?|#|&)/, '');

            if (!str) {
                return ret;
            }

            str.split('&').forEach(function (param) {
                var parts = param.replace(/\+/g, ' ').split('=');
                // Firefox (pre 40) decodes `%3D` to `=`
                // https://github.com/sindresorhus/query-string/pull/37
                var key = parts.shift();
                var val = parts.length > 0 ? parts.join('=') : undefined;

                key = decodeURIComponent(key);

                // missing `=` should be `null`:
                // http://w3.org/TR/2012/WD-url-20120524/#collect-url-parameters
                val = val === undefined ? null : decodeURIComponent(val);

                if (ret[key] === undefined) {
                    ret[key] = val;
                } else if (Array.isArray(ret[key])) {
                    ret[key].push(val);
                } else {
                    ret[key] = [ret[key], val];
                }
            });

            return ret;
        }
    };
})(window);