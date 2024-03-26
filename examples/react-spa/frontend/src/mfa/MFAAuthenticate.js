import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import * as allauth from '../lib/allauth'
import Button from '../components/Button'

export default function MFAAuthenticate () {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.mfaAuthenticate(code).then((content) => {
      setResponse((r) => { return { ...r, content } })
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
        <FormErrors param='code' errors={response.content?.errors} />
      </div>
      <Button onClick={() => submit()}>Sign In</Button>

    </section>
  )
}
