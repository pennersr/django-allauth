(function () {
  const allauth = window.allauth = window.allauth || {}

  function uint8ArrayToBase64 (buffer) {
    const byteView = new Uint8Array(buffer)
    let str = ''
    for (const charCode of byteView) {
      str += String.fromCharCode(charCode)
    }
    return btoa(str)
  }

function base64ToUint8Array(base64) {
    var binaryString = atob(base64);
    var bytes = new Uint8Array(binaryString.length);
    for (var i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}
  async function createCredentials (credentials, passwordless) {
    credentials = JSON.parse(JSON.stringify(credentials))
    credentials.publicKey.challenge = base64ToUint8Array(credentials.publicKey.challenge)
    credentials.publicKey.user.id = base64ToUint8Array(credentials.publicKey.user.id)
    credentials.publicKey.userVerification = passwordless ? 'required' : 'discouraged'
    const data = await navigator.credentials.create(credentials)
    const authenticatorData = {
      id: data.id,
      response: {
        attestationObject: uint8ArrayToBase64(data.response.attestationObject),
        clientDataJSON: uint8ArrayToBase64(data.response.clientDataJSON)
      },
      type: data.type
    }
    return authenticatorData
  }

  async function getCredentials (credentials) {
    credentials = JSON.parse(JSON.stringify(credentials))
    credentials.publicKey.challenge = base64ToUint8Array(credentials.publicKey.challenge)
    credentials.publicKey.allowCredentials.forEach(c => {
      c.id= base64ToUint8Array(c.id)
    })
    const data = await navigator.credentials.get(credentials)
    const authenticatorData = {
      id: data.id,
      response: {
        attestationObject: uint8ArrayToBase64(data.response.attestationObject),
        clientDataJSON: uint8ArrayToBase64(data.response.clientDataJSON),
        authenticatorData: uint8ArrayToBase64(data.response.authenticatorData),
        signature: uint8ArrayToBase64(data.response.signature)
      },
      type: data.type
    }
    return authenticatorData
  }

  function addForm (o) {
    const addBtn = document.getElementById(o.ids.add)
    const passwordlessCb = document.getElementById(o.ids.passwordless)
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest("form")
    addBtn.addEventListener('click', async function () {
      const passwordless = passwordlessCb.checked
      const credential = await createCredentials(o.data.credentials, passwordless)
      credentialInput.value = JSON.stringify(credential)
      form.submit()
    })
  }

  function authenticateForm (o) {
    const authenticateBtn = document.getElementById(o.ids.authenticate)
    const credentialInput = document.getElementById(o.ids.credential)
    const form = credentialInput.closest("form")
    authenticateBtn.addEventListener('click', async function () {
      const credential = await getCredentials(o.data.credentials)
      credentialInput.value = JSON.stringify(credential)
      form.submit()
    })
  }

  allauth.webauthn = {
    forms: {
      addForm: addForm,
      authenticateForm: authenticateForm
    }
  }
})()
