/* global document, window, metamask */
(async function () {
  'use strict'

  const settings = JSON.parse(document.getElementById('allauth-metamask-settings').textContent)
  let initialized = false

  async function init () {
    try {
      alert('aQ')
      await ethereum.request({
        method: 'wallet_addEthereumChain',
        params: [
          {
            chainId: settings.chainId,
            chainName: settings.chainName,
            rpcUrls: [settings.rpcURL]
          }
        ]
      })
      initialized = true
    } catch (e) {
      console.error(e)
    // FIXME: proper error handling
    }
  }

  async function loginwithtoken (token, account, next, process) {
    try {
      const from = account
      const message = token
      const sign = await ethereum.request({
        method: 'personal_sign',
        params: [message, from, '']
      })
      var res = sign
    } catch (err) {
      // FIXME: proper error handling
      console.error(err)
    }

    fetch('/accounts/metamask/login/', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': settings.csrfToken
      },
      body: JSON.stringify({
        account: account,
        login_token: res,
        next: next,
        process: 'verify'
      })
    })
      .then(function (response) {
        // The API call was successful!
        return response.text()
      }).then(function (html) {
        // Rewrite the page with fetch response
        document.querySelector('html').innerHTML = html
      }).catch(function (err) {
        // There was an error
        console.warn('Something went wrong.', err)
      })
  // window.location.href = next;
  }

  async function getAccount (next, process = 'login') {
    if (typeof window.ethereum === 'undefined' || !initialized) {
      alertMissing()
      return
    }
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' })
    const account = accounts[0]
    fetch('/accounts/metamask/login/', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': settings.csrfToken
      },
      body: JSON.stringify({
        account: account,
        next: next,
        process: 'token'
      })
    })
      .then((response) => response.json())
      .then((responseJson) => {
        loginwithtoken(responseJson.data, account, next, process)
      })
  }

  function alertMissing () {
    // TODO: i18n, more detailed description.
    alert('MetaMask is not installed')
  }

  const allauth = window.allauth = window.allauth || {}
  allauth.metamask = {
    login: getAccount
  }
  init()
})()
