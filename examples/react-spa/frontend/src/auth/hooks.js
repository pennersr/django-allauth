import { useContext, useRef, useState, useEffect } from 'react'
import { AuthContext } from './AuthContext'

export function useAuth () {
  return useContext(AuthContext)?.auth
}

export function useConfig () {
  return useContext(AuthContext)?.config
}

export function useUser () {
  const auth = useContext(AuthContext)?.auth
  return authInfo(auth).user
}

export function useAuthInfo () {
  const auth = useContext(AuthContext)?.auth
  return authInfo(auth)
}

function authInfo (auth) {
  const isAuthenticated = auth.status === 200 || (auth.status === 401 && auth.meta.is_authenticated)
  const requiresReauthentication = isAuthenticated && auth.status === 401
  const pendingFlow = auth.data?.flows?.find(flow => flow.is_pending)
  return { isAuthenticated, requiresReauthentication, user: isAuthenticated ? auth.data.user : null, pendingFlow }
}

export const AuthChangeEvent = Object.freeze({
  LOGGED_OUT: 'LOGGED_OUT',
  LOGGED_IN: 'LOGGED_IN',
  REAUTHENTICATED: 'REAUTHENTICATED',
  REAUTHENTICATION_REQUIRED: 'REAUTHENTICATION_REQUIRED',
  FLOW_UPDATED: 'FLOW_UPDATED'
})

function determineAuthChangeEvent (fromAuth, toAuth) {
  let fromInfo = authInfo(fromAuth)
  const toInfo = authInfo(toAuth)
  if (toAuth.status === 410) {
    return AuthChangeEvent.LOGGED_OUT
  }
  // Corner case: user ID change. Treat as if we're transitioning from anonymous state.
  if (fromInfo.user && toInfo.user && fromInfo.user?.id !== toInfo.user?.id) {
    fromInfo = { isAuthenticated: false, requiresReauthentication: false, user: null }
  }
  if (!fromInfo.isAuthenticated && toInfo.isAuthenticated) {
    // You typically don't transition from logged out to reauthentication required.
    return AuthChangeEvent.LOGGED_IN
  } else if (fromInfo.isAuthenticated && !toInfo.isAuthenticated) {
    return AuthChangeEvent.LOGGED_OUT
  } else if (fromInfo.isAuthenticated && toInfo.isAuthenticated) {
    if (toInfo.requiresReauthentication) {
      return AuthChangeEvent.REAUTHENTICATION_REQUIRED
    } else if (fromInfo.requiresReauthentication) {
      return AuthChangeEvent.REAUTHENTICATED
    } else if (fromAuth.data.methods.length < toAuth.data.methods.length) {
      // If you do a page reload when on the reauthentication page, both fromAuth
      // and toAuth are authenticated, and it won't see the change when
      // reauthentication without this.
      return AuthChangeEvent.REAUTHENTICATED
    }
  } else if (!fromInfo.isAuthenticated && !toInfo.isAuthenticated) {
    const fromFlow = fromInfo.pendingFlow
    const toFlow = toInfo.pendingFlow
    if (toFlow?.id && fromFlow?.id !== toFlow.id) {
      return AuthChangeEvent.FLOW_UPDATED
    }
  }
  // No change.
  return null
}

export function useAuthChange () {
  const auth = useAuth()
  const ref = useRef({ prevAuth: auth, event: null, didChange: false })
  const [, setForcedUpdate] = useState(0)
  useEffect(() => {
    if (ref.current.prevAuth) {
      ref.current.didChange = true
      const event = determineAuthChangeEvent(ref.current.prevAuth, auth)
      if (event) {
        ref.current.event = event
        setForcedUpdate(gen => gen + 1)
      }
    }
    ref.current.prevAuth = auth
  }, [auth, ref])
  const didChange = ref.current.didChange
  if (didChange) {
    ref.current.didChange = false
  }
  const event = ref.current.event
  if (event) {
    ref.current.event = null
  }

  return [auth, event]
}

export function useAuthStatus () {
  const auth = useAuth()
  return [auth, authInfo(auth)]
}
