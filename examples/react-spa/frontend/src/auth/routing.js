import {
  Navigate,
  useLocation
} from 'react-router-dom'
import { useUser, useAuth, useAuthChanged } from './hooks'
import { Flows } from '../lib/allauth'

const flow2path = {}
flow2path[Flows.LOGIN] = '/account/login'
flow2path[Flows.SIGNUP] = '/account/signup'
flow2path[Flows.VERIFY_EMAIL] = '/account/verify-email'
flow2path[Flows.PROVIDER_SIGNUP] = '/account/provider/signup'
flow2path[Flows.MFA_AUTHENTICATE] = '/account/2fa/authenticate'

function route401 (auth, location, children, pickPending) {
  const pendingFlows = auth.data.flows.filter(flow => flow.is_pending)
  let flow = Flows.LOGIN
  if (pendingFlows.length > 0) {
    flow = pendingFlows[0].id
    console.log(`Pending flow: ${flow}`)
  }
  const path = flow2path[flow]
  if (!path) {
    console.error(`Unknown path for flow: ${flow}`)
  }
  if (!pickPending) {
    const okPaths = auth.data.flows.map(flow => flow2path[flow.id])
    okPaths.push('/account/password/reset')
    if (okPaths.some(p => location.pathname.startsWith(p))) {
      return children
    }
  }
  return <Navigate to={path} replace />
}

export function AuthenticatedRoute ({ children }) {
  const user = useUser()
  const [auth, authChanged] = useAuthChanged()
  const location = useLocation()
  if (auth.status === 401 && user && authChanged) {
    return <Navigate to={`/account/reauthenticate?next=${encodeURIComponent(location.pathname + location.search)}`} />
  } else if (auth.status === 401 && !user) {
    return route401(auth, location, children)
  } else if (!user) {
    console.error('unexpected status')
    return null
  }
  return children
}

export function AnonymousRoute ({ children }) {
  const user = useUser()
  const [auth, authChanged] = useAuthChanged()
  const location = useLocation()
  if (user) {
    return <Navigate to='/dashboard' replace />
  } else if (auth.status !== 401) {
    console.error('unexpected status')
    return null
  }
  return route401(auth, location, children, authChanged)
}

export function CallbackRoute () {
  const auth = useAuth()
  const location = useLocation()
  // FIXME: Redirect to connect depending on process
  if (auth.status === 200) {
    return <Navigate to='/dashboard' replace />
  }
  return route401(auth, location, null, true)
}
