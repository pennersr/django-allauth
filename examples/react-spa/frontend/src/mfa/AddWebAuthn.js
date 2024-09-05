import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import FormErrors from '../components/FormErrors'
import Button from '../components/Button'
import * as allauth from '../lib/allauth'
import {
  create,
  parseCreationOptionsFromJSON
} from '@github/webauthn-json/browser-ponyfill'

export default function AddWebAuthn (props) {
  const [passwordless, setPasswordless] = useState(false)
  const [name, setName] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function submit () {
    setResponse({ ...response, fetching: true })
    try {
      const optResp = await allauth.getWebAuthnCreateOptions(passwordless)
      if (optResp.status === 200) {
        const jsonOptions = optResp.data.creation_options
        const options = parseCreationOptionsFromJSON(jsonOptions)
        const credential = await create(options)
        const addResp = await allauth.addWebAuthnCredential(name, credential)
        setResponse((r) => { return { ...r, content: addResp } })
      } else {
        setResponse((r) => { return { ...r, content: optResp } })
      }
    } catch (e) {
      console.error(e)
      window.alert(e)
    }
    setResponse((r) => { return { ...r, fetching: false } })
  }

  if (response.content?.status === 200) {
    return <Navigate to={response.content.meta.recovery_codes_generated ? '/account/2fa/recovery-codes' : '/account/2fa/webauthn'} />
  }
  return (
    <section>
      <h1>Add Security Key</h1>

      <div>
        <label>
          Name:
          <input value={name} onChange={(e) => setName(e.target.value)} />
          <FormErrors param='name' errors={response.content?.errors} />
          <FormErrors errors={response.content?.errors} />
        </label>
      </div>
      <div>
        <label>
          Passwordless
          <input type='checkbox' onChange={(e) => setPasswordless(e.target.checked)} checked={passwordless} />
        </label>
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Add key</Button>
    </section>
  )
}
