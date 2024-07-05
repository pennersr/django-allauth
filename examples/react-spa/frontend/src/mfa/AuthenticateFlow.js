import { Link, Navigate } from 'react-router-dom'
import { pathForFlow } from '../auth'
import { Flows, AuthenticatorType } from '../lib/allauth'
import { useAuthInfo } from '../auth/hooks'

const labels = {}
labels[AuthenticatorType.TOTP] = 'Use your authenticator app'
labels[AuthenticatorType.RECOVERY_CODES] = 'Use a recovery code'
labels[AuthenticatorType.WEBAUTHN] = 'Use security key'

export default function AuthenticateFlow (props) {
  const authInfo = useAuthInfo()

  if (authInfo?.pendingFlow?.id !== Flows.MFA_AUTHENTICATE) {
    return <Navigate to='/' />
  }
  const flow = authInfo.pendingFlow

  return (
    <section>
      <h1>Two-Factor Authentication</h1>
      <p>
        Your account is protected by two-factor authentication.
      </p>
      {props.children}

      {flow.types.length > 1
        ? <><h2>Alternative Options</h2>
          <ul>
            {flow.types.map(typ => {
              return (
                <li key={typ}>
                  <Link replace to={pathForFlow(flow, typ)}>{labels[typ]}</Link>
                </li>
              )
            })}
          </ul>
        </>
        : null}
    </section>

  )
}
