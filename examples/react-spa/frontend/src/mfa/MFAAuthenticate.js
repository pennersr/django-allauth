import { useState } from 'react'
import FormErrors from '../FormErrors'
import * as allauth from '../lib/allauth'

export default function MFAAuthenticate () {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.mfaAuthenticate(code).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
    <section>
      <h1>Two-Factor Authentication</h1>
      <p>
        Your account is protected by two-factor authentication. Please enter an authenticator code:
      </p>
      <div>
        <label>
          Authenticator code:
          <input type='text' value={code} onChange={(e) => setCode(e.target.value)} />
        </label>
        <FormErrors errors={response.data?.error?.detail?.code} />
      </div>
      <button onClick={() => submit()}>Sign In</button>

    </section>
  )
}
