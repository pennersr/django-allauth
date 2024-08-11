import AuthenticateCode from './AuthenticateCode'
import { AuthenticatorType } from '../lib/allauth'

export default function AuthenticateRecoveryCodes (props) {
  return (
    <AuthenticateCode authenticatorType={AuthenticatorType.TOTP}>
      <p>Please enter an authenticator code:</p>
    </AuthenticateCode>
  )
}
