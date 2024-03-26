import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { reauthenticate, Flows } from '../lib/allauth'
import ReauthenticateFlow from './ReauthenticateFlow'
import Button from '../components/Button'

export default function Reauthenticate () {
  const [password, setPassword] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    reauthenticate({ password }).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
    <ReauthenticateFlow flow={Flows.REAUTHENTICATE}>
      <p>Enter your password:</p>

      <FormErrors errors={response.content?.errors} />

      <div><label>Password: <input value={password} onChange={(e) => setPassword(e.target.value)} type='password' required /></label>
        <FormErrors param='password' errors={response.content?.errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Confirm</Button>
    </ReauthenticateFlow>
  )
}
