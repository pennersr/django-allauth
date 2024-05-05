import { useState } from 'react'
import * as allauth from '../lib/allauth'
import { Navigate } from 'react-router-dom'
import Button from '../components/Button'

export default function DeactivateTOTP (props) {
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.deactivateTOTPAuthenticator().then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response.content?.status === 200) {
    return <Navigate to='/account/2fa' />
  }
  return (
    <section>
      <h1>Deactivate Authenticator App</h1>

      <p>You are about to deactivate authenticator app based authentication. Are you sure?</p>

      <Button onClick={() => submit()}>Deactivate</Button>
    </section>
  )
}
