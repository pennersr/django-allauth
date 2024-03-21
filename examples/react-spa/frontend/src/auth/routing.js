import {
  Navigate,
  useLocation,
  Link
} from 'react-router-dom'
import { useAuthChange, AuthChangeEvent, useAuthStatus } from './hooks'
import { Flows } from '../lib/allauth'

export const URLs = Object.freeze({
  LOGIN_URL: '/account/login',
  LOGIN_REDIRECT_URL: '/dashboard',
  LOGOUT_REDIRECT_URL: '/'
})

const flow2path = {}
flow2path[Flows.LOGIN] = '/account/login'
flow2path[Flows.SIGNUP] = '/account/signup'
flow2path[Flows.VERIFY_EMAIL] = '/account/verify-email'
flow2path[Flows.PROVIDER_SIGNUP] = '/account/provider/signup'
flow2path[Flows.MFA_AUTHENTICATE] = '/account/2fa/authenticate'
flow2path[Flows.REAUTHENTICATE] = '/account/reauthenticate'
flow2path[Flows.MFA_REAUTHENTICATE] = '/account/2fa/reauthenticate'

export function pathForFlow (flowId) {
  const path = flow2path[flowId]
  if (!path) {
    throw new Error(`Unknown path for flow: ${flowId}`)
  }
  return path
}

export function pathForPendingFlow (auth) {
  const flow = auth.data.flows.find(flow => flow.is_pending)
  if (flow) {
    return pathForFlow(flow.id)
  }
  return null
}

function navigateToPendingFlow (auth) {
  const path = pathForFlow(auth)
  if (path) {
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
    return <Navigate to={`${URLs.LOGIN_URL}?${next}`} />
  }
}

export function AnonymousRoute ({ children }) {
  const [, status] = useAuthStatus()
  if (!status.isAuthenticated) {
    return children
  } else {
    return <Navigate to={URLs.LOGIN_REDIRECT_URL} />
  }
}

export function AuthChangeRedirector ({ children }) {
  const [auth, event] = useAuthChange()
  const location = useLocation()
  switch (event) {
    case AuthChangeEvent.LOGGED_OUT:
      return <Navigate to={URLs.LOGOUT_REDIRECT_URL} />
    case AuthChangeEvent.LOGGED_IN:
      return <Navigate to={URLs.LOGIN_REDIRECT_URL} />
    case AuthChangeEvent.REAUTHENTICATED:
    {
      const next = new URLSearchParams(location.search).get('next') || '/'
      return <Navigate to={next} />
    }
    case AuthChangeEvent.REAUTHENTICATION_REQUIRED: {
      const next = `next=${encodeURIComponent(location.pathname + location.search)}`
      const path = pathForFlow(auth.data.flows[0].id)
      return <Navigate to={`${path}?${next}`} state={{ reauth: auth }} />
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
