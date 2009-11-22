(function() {
var setCookie = function(name, value, days) {
    var date = new Date();
    date.setTime(date.getTime() + days*24*3600*1000);
    var expires = "; expires=" + date.toUTCString();
    document.cookie = [name, "=", encodeURIComponent(value), expires, "; path=/"].join('');
};

var getCookie = function(name) {
    if (!document.cookie || document.cookie == '') {
        return undefined;
    }

    var nameEQ = name + '=';
    var cookies = document.cookie.split(';');
    for (var i = 0, item; item = cookies[i]; i++) {
        item = item.replace(/^ +/, '');
        if (item.indexOf(nameEQ) == 0) {
            return window.decodeURIComponent(item.substring(nameEQ.length));
        }
    }
    return undefined;
}

// Don't overwrite the tz value if user wants it to be preserved.
var tz = getCookie('tz');
if (!/p$/.test(tz)) {
    tz = new Date().getTimezoneOffset();
}
setCookie('tz', tz, 365);
})();
