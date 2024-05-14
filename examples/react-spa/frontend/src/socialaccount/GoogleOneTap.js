import { useState } from 'react'
import { useConfig } from '../auth'
import { authenticateByToken } from '../lib/allauth'

function installGoogleOneTap (cb) {
  const id = 'google-one-tap'
  const scr = document.getElementById(id)
  if (!scr) {
    const scr = document.createElement('script')
    scr.id = id
    scr.src = '//accounts.google.com/gsi/client'
    scr.async = true
    scr.addEventListener('load', function () {
      cb()
    })
    document.body.appendChild(scr)
  } else {
    cb()
  }
}

export default function GoogleOneTap (props) {
  const config = useConfig()
  const [enabled, setEnabled] = useState(() => window.sessionStorage.getItem('googleOneTapEnabled') === 'yes')
  function onGoogleOneTapInstalled () {
    const provider = config.data.socialaccount.providers.find(p => p.id === 'google')
    if (provider && window.google) {
      function handleCredentialResponse (token) {
        authenticateByToken(provider.id, {
          id_token: token.credential,
          client_id: provider.client_id
        }, props.process)
      }

      window.google.accounts.id.initialize({
        client_id: provider.client_id,
        callback: handleCredentialResponse
      })
      window.google.accounts.id.prompt()
    }
  }

  if (enabled) {
    installGoogleOneTap(onGoogleOneTapInstalled)
    return null
  }
  function enable () {
    window.sessionStorage.setItem('googleOneTapEnabled', 'yes')
    installGoogleOneTap(onGoogleOneTapInstalled)
    setEnabled(true)
  }
  return (
    <div className='alert alert-danger d-flex justify-content-between'>
      <span><strong>Mind your privacy:</strong> Do you want to demo Google One Tap sign-in?</span>
      <button onClick={() => enable()} className='btn btn-sm btn-danger'>Enable</button>
    </div>
  )
}
