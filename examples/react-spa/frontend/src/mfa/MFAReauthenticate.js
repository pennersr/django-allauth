import { useState } from 'react'
import FormErrors from '../FormErrors'
import { mfaReauthenticate, Flows } from '../lib/allauth'
import ReauthenticateFlow from '../account/ReauthenticateFlow'

export default function MFAReauthenticate () {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    mfaReauthenticate(code).then((data) => {
      setResponse((r) => { return { ...r, data } })
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

      <FormErrors errors={response.data?.form?.errors} />

      <div><label>Code: <input value={code} onChange={(e) => setCode(e.target.value)} type='text' required /></label>
        <FormErrors errors={response.data?.error?.detail?.code} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Confirm</button>
    </ReauthenticateFlow>
  )
}
