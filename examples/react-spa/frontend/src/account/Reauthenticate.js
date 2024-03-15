import { useState } from 'react'
import FormErrors from '../FormErrors'
import { reauthenticate } from '../lib/allauth'
import { Navigate } from 'react-router-dom'

export default function Reauthenticate () {
  const [password, setPassword] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    reauthenticate({ password }).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response.data?.status === 200) {
    return <Navigate to='/' />
  }
  return (
    <div>
      <h1> Confirm Access</h1>
      <p>
        Please reauthenticate to safeguard your account.
      </p>

      <p>Enter your password:</p>

      <FormErrors errors={response.data?.form?.errors} />

      <div><label>Password: <input value={password} onChange={(e) => setPassword(e.target.value)} type='password' required /></label>
        <FormErrors errors={response.data?.error?.detail?.password} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Confirm</button>
    </div>
  )
}
