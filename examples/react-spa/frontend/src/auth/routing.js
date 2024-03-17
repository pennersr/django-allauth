import {
  Navigate,
  useLocation
} from 'react-router-dom'
import { AuthChangeEvent, useAuthStatus } from './hooks'
import { Flows } from '../lib/allauth'

const LOGIN_URL = '/account/login'
const LOGIN_REDIRECT_URL = '/dashboard'
const LOGOUT_REDIRECT_URL = '/'
const REAUTHENTICATE_URL = '/account/reauthenticate'

const flow2path = {}
flow2path[Flows.LOGIN] = '/account/login'
flow2path[Flows.SIGNUP] = '/account/signup'
flow2path[Flows.VERIFY_EMAIL] = '/account/verify-email'
flow2path[Flows.PROVIDER_SIGNUP] = '/account/provider/signup'
flow2path[Flows.MFA_AUTHENTICATE] = '/account/2fa/authenticate'

function navigateToPendingFlow (auth) {
  const flow = auth.data.flows.find(flow => flow.is_pending)
  if (flow) {
    const path = flow2path[flow.id]
    if (!path) {
      throw new Error(`Unknown path for flow: ${flow.id}`)
    }
    return <Navigate to={path} />
  }
  return null
}

export function AuthenticatedRoute ({ children }) {
  const location = useLocation()
  const [, status] = useAuthStatus()
  const next = `next=${encodeURIComponent(location.pathname + location.search)}`
  if (status.isAuthenticated) {
    return children
  } else {
    return <Navigate to={`${LOGIN_URL}?${next}`} />
  }
}

export function AnonymousRoute ({ children }) {
  const [, status] = useAuthStatus()
  if (!status.isAuthenticated) {
    return children
  } else {
    return <Navigate to={LOGIN_REDIRECT_URL} />
  }
}

export function CallbackRoute () {
  const [auth, status] = useAuthStatus()
  // FIXME: Redirect to connect depending on process
  if (status.isAuthenticated) {
    return <Navigate to={LOGIN_REDIRECT_URL} />
  }
  const pendingFlow = navigateToPendingFlow(auth)
  if (pendingFlow) {
    return pendingFlow
  }
  return <Navigate to={LOGIN_URL} />
}

export function AuthChangeRedirector ({ children }) {
  const [auth, status] = useAuthStatus()
  const location = useLocation()
  switch (status.event) {
    case AuthChangeEvent.LOGGED_OUT:
      return <Navigate to={LOGOUT_REDIRECT_URL} />
    case AuthChangeEvent.LOGGED_IN:
      return <Navigate to={LOGIN_REDIRECT_URL} />
    case AuthChangeEvent.REAUTHENTICATED:
    {
      const next = new URLSearchParams(location.search).get('next') || '/'
      return <Navigate to={next} />
    }
    case AuthChangeEvent.REAUTHENTICATION_REQUIRED: {
      const next = `next=${encodeURIComponent(location.pathname + location.search)}`
      return <Navigate to={`${REAUTHENTICATE_URL}?${next}`} />
    }
    case AuthChangeEvent.FLOW_UPDATED:
      const pendingFlow = navigateToPendingFlow(auth)
      if (!pendingFlow) {
        throw new Error()
      }
      return pendingFlow
    default:
      break
  }
  // ...stay where we are
  return children
}
