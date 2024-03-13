import { useContext } from 'react'
import { AuthContext } from './AuthContext'

export function useAuth () {
  return useContext(AuthContext)?.auth
}

export function useConfig () {
  return useContext(AuthContext)?.config
}

export function useUser () {
  const auth = useContext(AuthContext)?.auth
  return (auth.status === 200) ? auth.data.user : null
}
