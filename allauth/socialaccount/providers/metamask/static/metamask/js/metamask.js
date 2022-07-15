/* global document, window, metamask */
(async function () {
  'use strict'

  const settings = JSON.parse(document.getElementById('allauth-metamask-settings').textContent)
  let initialized = false

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

  async function init () {
    try {
      const params = {
        chainId: settings.chainId
      }
      if (settings.chainMethod !== 'wallet_switchEthereumChain') {
        params.chainName = settings.chainName
        params.rpcUrls = [settings.rpcURL]
      }
      await ethereum.request({
        method: settings.chainMethod,
        params: [params]
      })
      initialized = true
    } catch (e) {
      if (e.code === 4902 || (e.data && e.data.orginalError && e.data.orginalError.code === 4902)) {
        try {
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
        } catch (addError) {
          console.error(addError)
        }
      }
    }
  }

  async function verifySignature (token, account, next, process) {
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

    postForm(settings.verifyURL, {
      account: account,
      signature: res,
      next: next,
      process: 'verify'
    })
  }

  async function getAccount (next, process = 'login') {
    if (typeof window.ethereum === 'undefined' || !initialized) {
      alertMissing()
      return
    }
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' })
    const account = accounts[0]
    fetch(settings.nonceURL, {
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
        verifySignature(responseJson.data, account, next, process)
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
