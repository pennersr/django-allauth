import { useState } from 'react'
import FormErrors from './FormErrors'
import { login } from './lib/allauth'
import { Link } from 'react-router-dom'
import { useConfig } from './auth'
import ProviderList from './ProviderList'

export default function Login () {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })
  const config = useConfig()
  const hasProviders = config.data.socialaccount?.providers?.length > 0

  function submit () {
    setResponse({ ...response, fetching: true })
    login({ email, password }).then((data) => {
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
      <h1>Login</h1>
      <p>
        No account? <Link to='/account/signup'>Sign up here.</Link>
      </p>

      <FormErrors errors={response.data?.form?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response.data?.error?.detail?.email} />
      </div>
      <div><label>Password: <input value={password} onChange={(e) => setPassword(e.target.value)} type='password' required /></label>
        <Link to='/account/password/reset'>Forgot your password?</Link>
        <FormErrors errors={response.data?.error?.detail?.password} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Login</button>

      {hasProviders
        ? <>
          <h2>Or use a third-party</h2>
          <ProviderList callbackURL='/account/callback' />
        </>
        : null}
    </div>
  )
}
