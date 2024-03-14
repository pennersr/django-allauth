import { useConfig } from '../auth'
import { redirectToProvider } from '../lib/allauth'

export default function ProviderList (props) {
  const config = useConfig()
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
