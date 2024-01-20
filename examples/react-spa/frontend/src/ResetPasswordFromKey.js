import { useState } from 'react'
import FormErrors from './FormErrors'
import { getPasswordReset, postPasswordReset } from './lib/allauth'
import { Navigate, Link, useLoaderData } from 'react-router-dom'

export async function loader ({ params }) {
  const key = params.key
  const resp = await getPasswordReset(key)
  return { key, keyResponse: resp }
}

export default function ResetPasswordFromKey () {
  const { key, keyResponse } = useLoaderData()

  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')

  const [response, setResponse] = useState({ fetching: false, data: keyResponse })

  function submit () {
    setResponse({ ...response, fetching: true })
    postPasswordReset(key, { password1, password2 }).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  if (response?.data?.location) {
    return (
      <Navigate to='/login' />
    )
  }
  return (
    <div>
      <h1>Reset Password</h1>
      <p>
        Remember your password? <Link to='/login'>Back to login.</Link>
      </p>

      <FormErrors errors={response?.data?.form?.errors} />

      <div><label>Password: <input autoComplete='new-password' value={password1} onChange={(e) => setPassword1(e.target.value)} type='password' required /></label>
        <FormErrors errors={response.data?.form?.fields?.password1?.errors} />
      </div>
      <div><label>Password (again): <input value={password2} onChange={(e) => setPassword2(e.target.value)} type='password' required /></label>
        <FormErrors errors={response.data?.form?.fields?.password2?.errors} />
      </div>

      <button disabled={response.fetching} onClick={() => submit()}>Reset</button>
    </div>
  )
}
