import { useUser } from './UserSession'
import { Link } from 'react-router-dom'

export default function NavBar () {
  const user = useUser()
  const anonNav = (
    <>
      {' '}
      <Link to='/login'>🔑 Login</Link>
      {' '}
      <Link to='/signup'>🧑 Signup</Link>
      {' '}
      <Link to='/password/reset'>🔓 Reset password</Link>
    </>
  )
  const authNav = (
    <>
      {' '}
      <Link to='/logout'>👋 Logout</Link>
    </>
  )
  return (
    <nav>
      <strong>React ❤️ django-allauth:</strong>
      {' '}
      <Link to='/'>🏠 Home</Link>

      {user ? authNav : anonNav}
      {' '}
      <Link to='/dashboard'>📈 Dashboard</Link>
      {' '}
      <a href='http://localhost:1080'>✉️ MailCatcher</a>
    </nav>
  )
}
