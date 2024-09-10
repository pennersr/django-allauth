/* global document, window, FB */
(function () {
  'use strict'

  function postForm (action, data) {
    const f = document.createElement('form')
    f.method = 'POST'
    f.action = action

    for (const key in data) {
      const d = document.createElement('input')
      d.type = 'hidden'
      d.name = key
      d.value = data[key]
      f.appendChild(d)
    }
    document.body.appendChild(f)
    f.submit()
  }

  function setLocationHref (url) {
    if (typeof (url) === 'function') {
      // Deprecated -- instead, override
      // allauth.facebook.onLoginError et al directly.
      url()
    } else {
      window.location.href = url
    }
  }

  const allauth = window.allauth = window.allauth || {}
  const fbSettings = JSON.parse(document.getElementById('allauth-facebook-settings').textContent)
  let fbInitialized = false

  allauth.facebook = {

    init: function (opts) {
      this.opts = opts

      window.fbAsyncInit = function () {
        FB.init(opts.initParams)
        fbInitialized = true
        allauth.facebook.onInit()
      };

      (function (d) {
        const id = 'facebook-jssdk'
        if (d.getElementById(id)) { return }
        const js = d.createElement('script'); js.id = id; js.async = true
        js.src = opts.sdkUrl
        d.getElementsByTagName('head')[0].appendChild(js)
      }(document))
    },

    onInit: function () {
    },

    login: function (nextUrl, action, process, scope) {
      const self = this
      if (!fbInitialized) {
        const url = this.opts.loginUrl + '?next=' + encodeURIComponent(nextUrl) + '&action=' + encodeURIComponent(action) + '&process=' + encodeURIComponent(process) + '&scope=' + encodeURIComponent(scope)
        setLocationHref(url)
        return
      }
      if (action === 'reauthenticate' || action === 'rerequest') {
        this.opts.loginOptions.auth_type = action
      }
      if (scope !== '') {
        this.opts.loginOptions.scope = scope
      }

      FB.login(function (response) {
        if (response.authResponse) {
          self.onLoginSuccess(response, nextUrl, process)
        } else if (response && response.status && ['not_authorized', 'unknown'].indexOf(response.status) > -1) {
          self.onLoginCanceled(response)
        } else {
          self.onLoginError(response)
        }
      }, self.opts.loginOptions)
    },

    onLoginCanceled: function (/* response */) {
      setLocationHref(this.opts.cancelUrl)
    },

    onLoginError: function (/* response */) {
      setLocationHref(this.opts.errorUrl)
    },

    onLoginSuccess: function (response, nextUrl, process) {
      const data = {
        next: nextUrl || '',
        process,
        access_token: response.authResponse.accessToken,
        expires_in: response.authResponse.expiresIn,
        csrfmiddlewaretoken: this.opts.csrfToken
      }

      postForm(this.opts.loginByTokenUrl, data)
    },

    logout: function (nextUrl) {
      const self = this
      if (!fbInitialized) {
        return
      }
      FB.logout(function (response) {
        self.onLogoutSuccess(response, nextUrl)
      })
    },

    onLogoutSuccess: function (response, nextUrl) {
      const data = {
        next: nextUrl || '',
        csrfmiddlewaretoken: this.opts.csrfToken
      }

      postForm(this.opts.logoutUrl, data)
    }
  }

  allauth.facebook.init(fbSettings)
})()
