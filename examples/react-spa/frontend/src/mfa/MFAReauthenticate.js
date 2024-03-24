import { useState } from 'react'
import FormErrors from '../FormErrors'
import { mfaReauthenticate, Flows } from '../lib/allauth'
import ReauthenticateFlow from '../account/ReauthenticateFlow'

export default function MFAReauthenticate () {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    mfaReauthenticate(code).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
    <ReauthenticateFlow flow={Flows.MFA_REAUTHENTICATE}>
      <p>Enter an authenticator code:</p>

      <FormErrors errors={response.content?.errors} />

      <div><label>Code: <input value={code} onChange={(e) => setCode(e.target.value)} type='text' required /></label>
        <FormErrors param='code' errors={response.content?.errors} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Confirm</button>
    </ReauthenticateFlow>
  )
}
