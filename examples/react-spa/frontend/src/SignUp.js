import { useState } from 'react'
import FormErrors from './FormErrors'
import { postSignUp, URLs } from './lib/allauth'
import { Navigate, Link } from 'react-router-dom'

export default function Login () {
  const [email, setEmail] = useState('')
  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    postSignUp({ email, password1, password2 }).then((data) => {
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
  }
  return (
    <div>
      <h1>Sign Up</h1>
      <p>
        Already have an account? <Link to='/login'>Login here.</Link>
      </p>

      <FormErrors errors={response?.data?.form?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response?.data?.form?.fields?.email?.errors} />
      </div>
      <div><label>Password: <input autoComplete='new-password' value={password1} onChange={(e) => setPassword1(e.target.value)} type='password' required /></label>
        <FormErrors errors={response?.data?.form?.fields?.password1?.errors} />
      </div>
      <div><label>Password (again): <input value={password2} onChange={(e) => setPassword2(e.target.value)} type='password' required /></label>
        <FormErrors errors={response?.data?.form?.fields?.password2?.errors} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Sign Up</button>
    </div>
  )
}
