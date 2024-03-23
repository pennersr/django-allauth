import { useEffect } from 'react'
import { useConfig } from '../auth'
import { redirectToProvider, authenticateByToken } from '../lib/allauth'

export default function ProviderList (props) {
  const config = useConfig()
  useEffect(() => {
    const provider = config.data.socialaccount.providers.find(p => p.id === 'google')
    if (provider && window.google) {
      function handleCredentialResponse (token) {
        authenticateByToken(provider.id, {
          id_token: token.credential,
          client_id: provider.client_id
        }, props.process)
      }

      google.accounts.id.initialize({
        client_id: provider.client_id,
        callback: handleCredentialResponse
      })
      google.accounts.id.prompt()
    }
  }, [config])

  const providers = config.data.socialaccount.providers
  if (!providers.length) {
    return null
  }
  return (
    <ul>
      {providers.map(provider => {
        return (
          <li key={provider.id}>
            <button onClick={() => redirectToProvider(provider.id, props.callbackURL, props.process)}>{provider.name}</button>
          </li>
        )
      })}
    </ul>
  )
}
