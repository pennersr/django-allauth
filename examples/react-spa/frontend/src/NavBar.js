import { useUser } from './auth'
import { Link } from 'react-router-dom'

export default function NavBar () {
  const user = useUser()
  const anonNav = (
    <>
      {' '}
      <Link to='/account/login'>🔑 Login</Link>
      {' '}
      <Link to='/account/signup'>🧑 Signup</Link>
      {' '}
      <Link to='/account/password/reset'>🔓 Reset password</Link>
    </>
  )
  const authNav = (
    <>
      {' '}
      <Link to='/account/logout'>👋 Logout</Link>
      {' '}
      <Link to='/account/email'>📬 Change Email</Link>
      {' '}
      <Link to='/account/password/change'>🔒 Change Password</Link>
      {' '}
      <Link to='/account/providers'>👤 Providers</Link>
      {' '}
      <Link to='/account/2fa'>📱 Two-Factor Authentication</Link>
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
