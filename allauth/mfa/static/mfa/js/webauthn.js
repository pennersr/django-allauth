(function () {
  const allauth = window.allauth = window.allauth || {}

  async function createCredentials (credentials, passwordless) {
    credentials = JSON.parse(JSON.stringify(credentials))
    credentials.publicKey.authenticatorSelection.residentKey = passwordless ? 'required' : 'discouraged'
    credentials.publicKey.authenticatorSelection.userVerification = passwordless ? 'required' : 'discouraged'
    return await webauthnJSON.create(credentials)
  }

  async function getCredentials (credentials) {
    return await webauthnJSON.get(credentials)
  }

  function addForm (o) {
    const addBtn = document.getElementById(o.ids.add)
    const passwordlessCb = document.getElementById(o.ids.passwordless)
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest('form')
    addBtn.addEventListener('click', async function () {
      const passwordless = passwordlessCb.checked
      try {
        const credential = await createCredentials(o.data.credentials, passwordless)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        // FIXME: Make this configurable
        window.alert(e.message)
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
          throw new Error('FIXME')
        }
        const data = await response.json()
        const credential = await getCredentials(data.credentials)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        // FIXME: Make this configurable
        window.alert(e.message)
      }
    })
  }

  function authenticateForm (o) {
    const authenticateBtn = document.getElementById(o.ids.authenticate)
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest('form')
    authenticateBtn.addEventListener('click', async function () {
      try {
        const credential = await getCredentials(o.data.credentials)
        credentialInput.value = JSON.stringify(credential)
        form.submit()
      } catch (e) {
        // FIXME: Make this configurable
        window.alert(e.message)
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
