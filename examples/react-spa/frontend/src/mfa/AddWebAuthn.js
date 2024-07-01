import { useState } from 'react'
import { Navigate, useLoaderData } from 'react-router-dom'
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

  async function submit () {
    // FIXME: error handling
    const resp = await allauth.getWebAuthnCreateOptions(passwordless)
    const jsonOptions = resp.data.creation_options
    const options = parseCreationOptionsFromJSON(jsonOptions)
    const credential = await create(options)
    await allauth.addWebAuthnCredential(name, credential)
  }

  return (
    <section>
      <h1>Add Security Key</h1>

      <div>
        <label>
          Name:
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
      </div>
      <div>
        <label>
          Passwordless
          <input type='checkbox' onChange={(e) => setPasswordless(e.target.checked)} checked={passwordless} />
        </label>
      </div>
      <Button onClick={() => submit()}>Add key</Button>
    </section>
  )
}
