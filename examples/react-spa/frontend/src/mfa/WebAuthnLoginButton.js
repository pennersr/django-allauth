import Button from '../components/Button'
import { useState } from 'react'
import { getWebAuthnRequestOptionsForLogin, loginUsingWebAuthn } from '../lib/allauth'
import {
  parseRequestOptionsFromJSON,
  get
} from '@github/webauthn-json/browser-ponyfill'

export default function WebAuthnLoginButton (props) {
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function submit (e) {
    e.preventDefault()
    setResponse({ ...response, fetching: true })
    try {
      const optResp = await getWebAuthnRequestOptionsForLogin()
      const jsonOptions = optResp.data.request_options
      const options = parseRequestOptionsFromJSON(jsonOptions)
      const credential = await get(options)
      const loginResp = await loginUsingWebAuthn(credential)
      setResponse((r) => { return { ...r, content: loginResp } })
    } catch (e) {
      console.error(e)
      window.alert(e)
    }
    setResponse((r) => { return { ...r, fetching: false } })
  }
  return <Button onClick={submit}>{props.children}</Button>
}
