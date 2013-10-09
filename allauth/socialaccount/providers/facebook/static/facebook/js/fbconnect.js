(function() {
    "use strict";

    var allauth = window.allauth = window.allauth || {};

    var init = function(opts) {

        function postForm(action, data) {
            var f = document.createElement('form');
            f.method = 'POST';
            f.action = action;
            var i = 0;
            data.push(['csrfmiddlewaretoken', opts.csrfToken]);
            for (i = 0; i < data.length; i++) {
                var d = document.createElement('input');
                d.type = 'hidden';
                d.name = data[i][0];
                d.value = data[i][1];
                f.appendChild(d);
            }
            document.body.appendChild(f);
            f.submit();
        }

        allauth.facebook = { login: function() {}, logout: function() {} };
        window.fbAsyncInit = function() {
            FB.init({
                appId      : opts.appId,
                channelUrl : opts.channelUrl,
                status     : true,
                cookie     : true,
                oauth      : true,
                xfbml      : true
            });
            allauth.facebook.login = function(nextUrl, action, process) {
        if (action == 'reauthenticate') {
            opts.loginOptions.auth_type = action;
        }
                FB.login(function(response) {
                    if (response.authResponse) {
                        postForm(opts.loginByTokenUrl,
                                 [['next', nextUrl || ''],
                                  ['process', process],
                                  ['access_token', response.authResponse.accessToken],
                                  ['expires_in', response.authResponse.expiresIn]]);
                    } else {
                        var next;
                        if (response && response.status && ["not_authorized", "unknown"].indexOf(response.status) > -1) {
                            next = opts.cancelUrl;
                        } else {
                            next = opts.errorUrl;
                        }

                        if (typeof(next) == "function") {
                            next();
                        } else {
                            window.location.href = next;
                        }
                    }
                }, opts.loginOptions);
            };
            allauth.facebook.logout = function(nextUrl) {
                FB.logout(function() {
                    var data = [];
                    if (nextUrl) {
                        data.push(['next', nextUrl]);
                    }
                    postForm(opts.loginByTokenUrl, data);
                });
            };
        };
        (function(d){
            var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
            js = d.createElement('script'); js.id = id; js.async = true;
            js.src = "//connect.facebook.net/"+opts.locale+"/all.js";
            d.getElementsByTagName('head')[0].appendChild(js);
        }(document));
    };

    allauth.facebook = { init: init };
})();
