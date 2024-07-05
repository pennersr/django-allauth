import { useState } from 'react'
import { AuthenticatorType, getWebAuthnRequestOptionsForAuthentication, authenticateUsingWebAuthn } from '../lib/allauth'
import Button from '../components/Button'
import {
  parseRequestOptionsFromJSON,
  get
} from '@github/webauthn-json/browser-ponyfill'
import AuthenticateFlow from './AuthenticateFlow'

export default function AuthenticateWebAuthn (props) {
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function submit () {
    setResponse({ ...response, fetching: true })
    try {
      const optResp = await getWebAuthnRequestOptionsForAuthentication()
      const jsonOptions = optResp.data.request_options
      const options = parseRequestOptionsFromJSON(jsonOptions)
      const credential = await get(options)
      const reauthResp = await authenticateUsingWebAuthn(credential)
      setResponse((r) => { return { ...r, content: reauthResp } })
    } catch (e) {
      console.error(e)
      window.alert(e)
    }
    setResponse((r) => { return { ...r, fetching: false } })
  }

  return (
    <AuthenticateFlow authenticatorType={AuthenticatorType.WEBAUTHN}>
      <Button disabled={response.fetching} onClick={() => submit()}>Use security key</Button>
    </AuthenticateFlow>
  )
}
