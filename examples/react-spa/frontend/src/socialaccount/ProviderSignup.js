import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { providerSignup } from '../lib/allauth'
import { Link } from 'react-router-dom'
import Button from '../components/Button'

export default function ProviderSignup () {
  const [email, setEmail] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    providerSignup({ email }).then((content) => {
      setResponse((r) => { return { ...r, content } })
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

      <FormErrors errors={response.content?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors param='email' errors={response.content?.errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Sign Up</Button>
    </div>
  )
}
