import { useState } from 'react'
import FormErrors from './FormErrors'
import { providerSignup } from './lib/allauth'
import { Link } from 'react-router-dom'

export default function ProviderSignup () {
  const [email, setEmail] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    providerSignup({ email }).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  return (
    <div>
      <h1>Sign Up</h1>
      <p>
        Already have an account? <Link to='/account/login'>Login here.</Link>
      </p>

      <FormErrors errors={response?.data?.error?.__all__?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response?.data?.error?.detail?.email} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Sign Up</button>
    </div>
  )
}
