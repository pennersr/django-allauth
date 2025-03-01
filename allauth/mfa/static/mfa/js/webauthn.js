(function () {
  const allauth = window.allauth = window.allauth || {}
  const webauthnJSON = window.webauthnJSON

  function dispatchError (exception) {
    const event = new CustomEvent('allauth.error', { detail: { tags: ['mfa', 'webauthn'], exception }, cancelable: true })
    document.dispatchEvent(event)
    if (!event.defaultPrevented) {
      console.error(exception)
    }
  }

  async function createCredentials (credentials, passwordless) {
    credentials = JSON.parse(JSON.stringify(credentials))
    const sel = credentials.publicKey.authenticatorSelection
    if (passwordless != null) {
      sel.residentKey = passwordless ? 'required' : 'discouraged'
      sel.requireResidentKey = passwordless
      sel.userVerification = passwordless ? 'required' : 'discouraged'
    }
    return await webauthnJSON.create(credentials)
  }

  function signupForm (o) {
    const signupBtn = document.getElementById(o.ids.signup)
    return addOrSignupForm(o, signupBtn, null)
  }

  function addForm (o) {
    const addBtn = document.getElementById(o.ids.add)
    const passwordlessCb = o.ids.passwordless ? document.getElementById(o.ids.passwordless) : null
    const passwordlessFn = () => passwordlessCb ? passwordlessCb.checked : false
    return addOrSignupForm(o, addBtn, passwordlessFn)
  }

  function getData (o) {
    if (typeof o.ids.data !== 'undefined') {
      return JSON.parse(document.getElementById(o.ids.data).textContent)
    }
    return o.data
  }

  function addOrSignupForm (o, actionBtn, passwordlessFn) {
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest('form')
    actionBtn.addEventListener('click', async function () {
      const passwordless = passwordlessFn ? passwordlessFn() : undefined
      try {
        const credential = await createCredentials(getData(o).creation_options, passwordless)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        dispatchError(e)
      }
    })
  }

  function loginForm (o) {
    const loginBtn = document.getElementById(o.ids.login)
    const form = loginBtn.form
    const credentialInput = document.getElementById(o.ids.credential)
    loginBtn.addEventListener('click', async function (e) {
      e.preventDefault()
      try {
        const response = await fetch(form.action, {
          method: 'GET',
          headers: {
            Accept: 'application/json'
          }
        })
        if (!response.ok) {
          throw new Error('Unable to fetch passkey data from server.')
        }
        const data = await response.json()
        const credential = await webauthnJSON.get(data.request_options)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        dispatchError(e)
      }
    })
  }

  function authenticateForm (o) {
    const authenticateBtn = document.getElementById(o.ids.authenticate)
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest('form')
    authenticateBtn.addEventListener('click', async function (e) {
      e.preventDefault()
      try {
        const credential = await webauthnJSON.get(getData(o).request_options)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        dispatchError(e)
      }
    })
  }

  allauth.webauthn = {
    forms: {
      addForm,
      authenticateForm,
      loginForm,
      signupForm
    }
  }
})()
