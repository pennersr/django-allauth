import AuthenticateCode from './AuthenticateCode'
import { AuthenticatorType } from '../lib/allauth'

export default function AuthenticateRecoveryCodes (props) {
  return (
    <AuthenticateCode authenticatorType={AuthenticatorType.RECOVERY_CODES}>
      <p>Please enter a recovery code:</p>
    </AuthenticateCode>
  )
}
