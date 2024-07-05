import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import * as allauth from '../lib/allauth'
import Button from '../components/Button'
import { useAuthInfo } from '../auth/hooks'
import { Navigate } from 'react-router-dom'
import AuthenticateFlow from './AuthenticateFlow'

export default function AuthenticateCode (props) {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })
  const authInfo = useAuthInfo()

  if (authInfo?.pendingFlow?.id !== allauth.Flows.MFA_AUTHENTICATE) {
    return <Navigate to='/' />
  }
  const authenticatorTypes = authInfo.pendingFlow.types
  const hasWebAuthn = authenticatorTypes.includes(allauth.AuthenticatorType.WEBAUTHN)
  const hasTOTP = authenticatorTypes.includes(allauth.AuthenticatorType.TOTP)
  const hasRecoveryCodes = authenticatorTypes.includes(allauth.AuthenticatorType.RECOVERY_CODES)

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.mfaAuthenticate(code).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
    <AuthenticateFlow authenticatorType={props.authenticatorType}>
      {props.children}
      <label>
        Authenticator code:
        <input type='text' value={code} onChange={(e) => setCode(e.target.value)} />
      </label>
      <FormErrors param='code' errors={response.content?.errors} />
      <Button onClick={() => submit()}>Sign In</Button>
    </AuthenticateFlow>
  )
}
