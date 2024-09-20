import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { confirmLoginCode, Flows } from '../lib/allauth'
import { Navigate } from 'react-router-dom'
import Button from '../components/Button'
import { useAuthStatus } from '../auth'
import * as allauth from '../lib/allauth'
import {
  create,
  parseCreationOptionsFromJSON
} from '@github/webauthn-json/browser-ponyfill'

export default function ConfirmLoginCode () {
  const [, authInfo] = useAuthStatus()
  const [name, setName] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function submit () {
    setResponse({ ...response, fetching: true })
    try {
      const optResp = await allauth.getWebAuthnCreateOptionsAtSignup(true)
      if (optResp.status === 200) {
        const jsonOptions = optResp.data.creation_options
        const options = parseCreationOptionsFromJSON(jsonOptions)
        const credential = await create(options)
        const signupResp = await allauth.signupWebAuthnCredential(name, credential)
        setResponse((r) => { return { ...r, content: signupResp } })
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
    alert('OK')
    // FIXME
  }

  if (response.content?.status === 409 || authInfo.pendingFlow?.id !== Flows.MFA_WEBAUTHN_SIGNUP) {
    return <Navigate to='/account/signup/passkey' />
  }
  return (
    <div>
      <h1>Create Passkey</h1>
      <p>
        The code expires shortly, so please enter it soon.
      </p>

      <FormErrors errors={response.content?.errors} />

      <div><label>Name <input value={name} onChange={(e) => setName(e.target.value)} type='text' required /></label>
        <FormErrors param='code' errors={response.content?.errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Create</Button>
    </div>
  )
}
