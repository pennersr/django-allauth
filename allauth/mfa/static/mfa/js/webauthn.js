(function () {
  const allauth = window.allauth = window.allauth || {}

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
    sel.residentKey = passwordless ? 'required' : 'discouraged'
    sel.requireResidentKey = passwordless
    sel.userVerification = passwordless ? 'required' : 'discouraged'
    return await webauthnJSON.create(credentials)
  }

  function addForm (o) {
    const addBtn = document.getElementById(o.ids.add)
    const passwordlessCb = o.ids.passwordless ? document.getElementById(o.ids.passwordless) : null
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest('form')
    addBtn.addEventListener('click', async function () {
      const passwordless = passwordlessCb ? passwordlessCb.checked : false
      try {
        const credential = await createCredentials(o.data.creation_options, passwordless)
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
        const credential = await webauthnJSON.get(o.data.request_options)
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
      loginForm
    }
  }
})()
