import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { signUp } from '../lib/allauth'
import { Link } from 'react-router-dom'
import { useConfig } from '../auth'
import ProviderList from '../socialaccount/ProviderList'
import Button from '../components/Button'

export default function Signup () {
  const [email, setEmail] = useState('')
  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')
  const [password2Errors, setPassword2Errors] = useState([])
  const [response, setResponse] = useState({ fetching: false, content: null })
  const config = useConfig()
  const hasProviders = config.data.socialaccount?.providers?.length > 0

  function submit () {
    if (password2 !== password1) {
      setPassword2Errors([{ param: 'password2', message: 'Password does not match.' }])
      return
    }
    setPassword2Errors([])
    setResponse({ ...response, fetching: true })
    signUp({ email, password: password1 }).then((content) => {
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
      <div><label>Password: <input autoComplete='new-password' value={password1} onChange={(e) => setPassword1(e.target.value)} type='password' required /></label>
        <FormErrors param='password' errors={response.content?.errors} />
      </div>
      <div><label>Password (again): <input value={password2} onChange={(e) => setPassword2(e.target.value)} type='password' required /></label>
        <FormErrors param='password2' errors={password2Errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Sign Up</Button>
      <a href='/account/signup/passkey'>Sign up using a passkey</a>

      {hasProviders
        ? <>
          <h2>Or use a third-party</h2>
          <ProviderList callbackURL='/account/provider/callback' />
        </>
        : null}
    </div>
  )
}
