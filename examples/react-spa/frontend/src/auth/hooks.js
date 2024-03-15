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
  return (auth.status === 200 || (auth.status === 401 && auth.meta.is_authenticated)) ? auth.data.user : null
}

export function useAuthChanged () {
  const auth = useAuth()
  const authChangedRef = useRef(undefined)
  const [gen, setGen] = useState(0)
  useEffect(() => {
    setGen(g => g + 1)
    authChangedRef.current = typeof authChangedRef.current !== 'undefined'
  }, [auth])
  const authChanged = authChangedRef.current
  if (authChanged) {
    authChangedRef.current = false
  }
  return [auth, authChanged]
}
