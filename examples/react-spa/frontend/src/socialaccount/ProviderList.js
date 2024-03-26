import { useEffect } from 'react'
import { useConfig } from '../auth'
import { redirectToProvider, authenticateByToken } from '../lib/allauth'
import Button from '../components/Button'

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

      window.google.accounts.id.initialize({
        client_id: provider.client_id,
        callback: handleCredentialResponse
      })
      window.google.accounts.id.prompt()
    }
  }, [config, props.process])

  const providers = config.data.socialaccount.providers
  if (!providers.length) {
    return null
  }
  return (
    <ul>
      {providers.map(provider => {
        return (
          <li key={provider.id}>
            <Button onClick={() => redirectToProvider(provider.id, props.callbackURL, props.process)}>{provider.name}</Button>
          </li>
        )
      })}
    </ul>
  )
}
