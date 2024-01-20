import { useState } from 'react'
import FormErrors from './FormErrors'
import { fetchResetPassword, URLs } from './lib/allauth'
import { Link } from 'react-router-dom'

export default function ResetPassword () {
  const [email, setEmail] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    fetchResetPassword(email).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  if (response?.data?.location === URLs.RESET_PASSWORD_DONE) {
    return (
      <div>
        <h1>Reset Password</h1>
        <p>Password reset sent.</p>
      </div>
    )
  }
  return (
    <div>
      <h1>Reset Password</h1>
      <p>
        Remember your password? <Link to='/signup'>Back to login.</Link>
      </p>

      <FormErrors errors={response?.data?.form?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response?.data?.form?.fields?.email?.errors} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Reset</button>
    </div>
  )
}
