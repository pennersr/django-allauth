import { useState } from 'react'
import FormErrors from './FormErrors'
import { getPasswordReset, resetPassword } from './lib/allauth'
import { Link, useLoaderData } from 'react-router-dom'

export async function loader ({ params }) {
  const key = params.key
  const resp = await getPasswordReset(key)
  return { key, keyResponse: resp }
}

export default function ResetPassword () {
  const { key, keyResponse } = useLoaderData()

  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')
  const [password2Errors, setPassword2Errors] = useState([])

  const [response, setResponse] = useState({ fetching: false, data: keyResponse })

  function submit () {
    if (password2 !== password1) {
      setPassword2Errors(['Password does not match.'])
      return
    }
    setPassword2Errors([])
    setResponse({ ...response, fetching: true })
    resetPassword({ key, password: password1 }).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  let body
  if (response?.data?.error?.detail?.key) {
    body = <FormErrors errors={response?.data?.error?.detail?.key} />
  } else {
    body = (
      <>
        <div><label>Password: <input autoComplete='new-password' value={password1} onChange={(e) => setPassword1(e.target.value)} type='password' required /></label>
          <FormErrors errors={response.data?.error?.detail?.password} />
        </div>
        <div><label>Password (again): <input value={password2} onChange={(e) => setPassword2(e.target.value)} type='password' required /></label>
          <FormErrors errors={password2Errors} />
        </div>

        <button disabled={response.fetching} onClick={() => submit()}>Reset</button>
      </>
    )
  }

  return (
    <div>
      <h1>Reset Password</h1>
      <p>
        Remember your password? <Link to='/login'>Back to login.</Link>
      </p>
      {body}
    </div>
  )
}
