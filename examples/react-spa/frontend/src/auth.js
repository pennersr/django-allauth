import {
  Navigate
} from 'react-router-dom'
import { useUser } from './UserSession'

export function AuthenticatedRoute ({ children }) {
  const user = useUser()

  if (!user) {
    return <Navigate to='/login' replace />
  }

  return children
}

export function AnonymousRoute ({ children }) {
  const user = useUser()

  if (user) {
    return <Navigate to='/dashboard' replace />
  }

  return children
}
