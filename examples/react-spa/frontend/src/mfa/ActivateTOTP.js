import { useState } from 'react'
import * as allauth from '../lib/allauth'
import { Navigate, useLoaderData } from 'react-router-dom'
import FormErrors from '../FormErrors'

export async function loader ({ params }) {
  const resp = await allauth.getTOTPAuthenticator()
  return { totp: resp }
}

export default function ActivateTOTP (props) {
  const { totp } = useLoaderData()
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.activateTOTPAuthenticator(code).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (totp.status === 200 || response?.data?.status === 200) {
    return <Navigate to='/account/2fa' />
  }
  return (
    <section>
      <h1>Activate TOTP</h1>

      <div>
        <label>
          Authenticator secret:
          <input disabled type='text' value={totp.data.secret} />
          <span>You can store this secret and use it to reinstall your authenticator app at a later time.</span>
        </label>
      </div>
      <div>
        <label>
          Authenticator code:
          <input type='text' value={code} onChange={(e) => setCode(e.target.value)} />
        </label>
        <FormErrors errors={response.data?.error?.detail?.code} />
      </div>
      <button onClick={() => submit()}>Activate</button>
    </section>
  )
}
