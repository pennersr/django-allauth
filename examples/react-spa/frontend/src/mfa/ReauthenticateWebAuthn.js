import { useState } from 'react'
import { Flows, getWebAuthnRequestOptionsForReauthentication, reauthenticateUsingWebAuthn } from '../lib/allauth'
import ReauthenticateFlow from '../account/ReauthenticateFlow'
import Button from '../components/Button'
import {
  parseRequestOptionsFromJSON,
  get
} from '@github/webauthn-json/browser-ponyfill'

export default function ReauthenticateWebAuthn () {
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function submit () {
    setResponse({ ...response, fetching: true })
    try {
      const optResp = await getWebAuthnRequestOptionsForReauthentication()
      const jsonOptions = optResp.data.request_options
      const options = parseRequestOptionsFromJSON(jsonOptions)
      const credential = await get(options)
      const reauthResp = await reauthenticateUsingWebAuthn(credential)
      setResponse((r) => { return { ...r, content: reauthResp } })
    } catch (e) {
      console.error(e)
      window.alert(e)
    }
    setResponse((r) => { return { ...r, fetching: false } })
  }

  return (
    <ReauthenticateFlow flow={Flows.MFA_REAUTHENTICATE}>

      <Button disabled={response.fetching} onClick={() => submit()}>Use security key</Button>
    </ReauthenticateFlow>
  )
}
