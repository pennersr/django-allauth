import { Link, useLocation } from 'react-router-dom'
import { pathForFlow } from '../auth'
import { Flows } from '../lib/allauth'

const flowLabels = {}
flowLabels[Flows.REAUTHENTICATE] = 'Use your password'
flowLabels[Flows.MFA_REAUTHENTICATE] = 'Use your authenticator app'

export default function ReauthenticateFlow (props) {
  const location = useLocation()
  const flows = location.state.reauth.data.flows

  return (
    <div>
      <h1> Confirm Access</h1>
      <p>
        Please reauthenticate to safeguard your account.
      </p>
      {props.children}

      {flows.length > 1
        ? <><h2>Alternative Options</h2>
          <ul>
            {flows.filter(flow => flow.id !== props.flow).map(flow => {
              return (
                <li key={flow.id}>
                  <Link replace state={location.state} to={pathForFlow(flow.id) + location.search}>{flowLabels[flow.id] || flow.id}</Link>
                </li>
              )
            })}
          </ul>
        </>
        : null}
    </div>

  )
}
