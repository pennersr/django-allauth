import { useState } from 'react'
import AuthenticateCode from './AuthenticateCode'
import { AuthenticatorType } from '../lib/allauth'
import { useAuthInfo } from '../auth/hooks'
import * as allauth from '../lib/allauth'
import { Navigate } from 'react-router-dom'
import Button from'../components/Button'

export default function Trust (props) {
  const [response, setResponse] = useState({ fetching: false, content: null })
  const authInfo = useAuthInfo()

  if (authInfo?.pendingFlow?.id !== allauth.Flows.MFA_TRUST) {
    return <Navigate to='/' />
  }

  function submit (trust) {
    setResponse({ ...response, fetching: true })
    allauth.mfaTrust(trust).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
      <section>
      <h1>Trust this Browser?</h1>
      <p>If you choose to trust this browser, you will not be asked for a verification code the next time you sign in.</p>
      <Button onClick={() => submit(false)}>Don't Trust</Button>
      <Button onClick={() => submit(true)}>Trust</Button>
    </section>
  )
}
