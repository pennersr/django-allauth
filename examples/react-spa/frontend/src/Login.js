import { useState } from 'react'
import FormErrors from './FormErrors'
import { URLs } from './lib/allauth'
import { Navigate, Link } from 'react-router-dom'
import { usePostLogin } from './UserSession'

export default function Login () {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })
  const postLogin = usePostLogin()

  function submit () {
    setResponse({ ...response, fetching: true })
    postLogin({ login: email, password }).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response?.data?.location === URLs.CONFIRM_EMAIL) {
    return <Navigate to='/confirm-email' />
  } else if (response?.data?.location === URLs.PROFILE) {
    return <Navigate to='/dashboard' />
  }
  return (
    <div>
      <h1>Login</h1>
      <p>
        No account? <Link to='/signup'>Sign up here.</Link>
      </p>

      <FormErrors errors={response.data?.form?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response.data?.form?.fields?.login?.errors} />
      </div>
      <div><label>Password: <input value={password} onChange={(e) => setPassword(e.target.value)} type='password' required /></label>
        <Link to='/password/reset'>Forgot your password?</Link>
        <FormErrors errors={response.data?.form?.fields?.password?.errors} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Login</button>
    </div>
  )
}
