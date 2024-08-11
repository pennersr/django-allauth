import { Link, useLocation } from 'react-router-dom'
import { pathForFlow } from '../auth'
import { Flows, AuthenticatorType } from '../lib/allauth'

const flowLabels = {}
flowLabels[Flows.REAUTHENTICATE] = 'Use your password'
flowLabels[`${Flows.MFA_REAUTHENTICATE}:${AuthenticatorType.TOTP}`] = 'Use your authenticator app'
flowLabels[`${Flows.MFA_REAUTHENTICATE}:${AuthenticatorType.RECOVERY_CODES}`] = 'Use a recovery code'
flowLabels[`${Flows.MFA_REAUTHENTICATE}:${AuthenticatorType.WEBAUTHN}`] = 'Use security key'

function flowsToMethods (flows) {
  const methods = []
  flows.forEach(flow => {
    if (flow.id === Flows.MFA_REAUTHENTICATE) {
      flow.types.forEach(typ => {
        methods.push({
          label: flowLabels[`${flow.id}:${typ}`] || flow.id,
          id: flow.id,
          path: pathForFlow(flow, typ)
        })
      })
    } else {
      methods.push({
        label: flowLabels[flow.id] || flow.id,
        id: flow.id,
        path: pathForFlow(flow)
      })
    }
  })
  return methods
}

export default function ReauthenticateFlow (props) {
  const location = useLocation()
  const methods = flowsToMethods(location.state.reauth.data.flows)

  return (
    <div>
      <h1>Confirm Access</h1>
      <p>
        Please reauthenticate to safeguard your account.
      </p>
      {props.children}

      {methods.length > 1
        ? <><h2>Alternative Options</h2>
          <ul>
            {methods.filter(method => method.id !== props.method).map(method => {
              return (
                <li key={method.id}>
                  <Link replace state={location.state} to={method.path + location.search}>{method.label}</Link>
                </li>
              )
            })}
          </ul>
        </>
        : null}
    </div>

  )
}
