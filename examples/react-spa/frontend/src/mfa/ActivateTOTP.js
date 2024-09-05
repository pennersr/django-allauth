import { useState } from 'react'
import * as allauth from '../lib/allauth'
import { Navigate, useLoaderData } from 'react-router-dom'
import FormErrors from '../components/FormErrors'
import Button from '../components/Button'

export async function loader ({ params }) {
  const resp = await allauth.getTOTPAuthenticator()
  return { totp: resp }
}

export default function ActivateTOTP (props) {
  const { totp } = useLoaderData()
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.activateTOTPAuthenticator(code).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (totp.status === 200 || response.content?.status === 200) {
    return <Navigate to='/account/2fa' />
  }
  return (
    <section>
      <h1>Activate TOTP</h1>

      <div>
        <label>
          Authenticator secret:
          <input disabled type='text' value={totp.meta?.secret} />
          <span>You can store this secret and use it to reinstall your authenticator app at a later time.</span>
        </label>
      </div>
      <div>
        <label>
          Authenticator code:
          <input type='text' value={code} onChange={(e) => setCode(e.target.value)} />
        </label>
        <FormErrors param='code' errors={response.content?.errors} />
        <FormErrors errors={totp.errors} />
      </div>
      <Button onClick={() => submit()}>Activate</Button>
    </section>
  )
}
