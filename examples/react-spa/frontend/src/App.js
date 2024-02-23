import { AuthContext, AnonymousRoute, AuthenticatedRoute } from './auth'
import {
  Outlet,
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom'
import Dashboard from './Dashboard'
import Login from './Login'
import Logout from './Logout'
import SignUp from './SignUp'
import Home from './Home'
import ChangeEmail from './ChangeEmail'
import VerifyEmail, { loader as verifyEmailLoader } from './VerifyEmail'
import VerificationEmailSent from './VerificationEmailSent'
import RequestPasswordReset from './RequestPasswordReset'
import NavBar from './NavBar'
import ResetPassword, { loader as resetPasswordLoader } from './ResetPassword'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: '/',
        element: <Home />
      },
      {
        path: '/dashboard',
        element: <AuthenticatedRoute><Dashboard /></AuthenticatedRoute>
      },
      {
        path: '/account/login',
        element: <AnonymousRoute><Login /></AnonymousRoute>
      },
      {
        path: '/account/email',
        element: <AuthenticatedRoute><ChangeEmail /></AuthenticatedRoute>
      },
      {
        path: '/account/logout',
        element: <Logout />
      },
      {
        path: '/account/signup',
        element: <AnonymousRoute><SignUp /></AnonymousRoute>
      },
      {
        path: '/account/verify-email',
        element: <VerificationEmailSent />
      },
      {
        path: '/account/verify-email/:key',
        element: <AnonymousRoute><VerifyEmail /></AnonymousRoute>,
        loader: verifyEmailLoader
      },
      {
        path: '/account/password/reset',
        element: <RequestPasswordReset />
      },
      {
        path: '/account/password/reset/key/:key',
        element: <ResetPassword />,
        loader: resetPasswordLoader
      }
    ]
  }
])

function Root () {
  return (
    <div>
      <NavBar />
      <Outlet />
    </div>
  )
}

function App () {
  return (
    <AuthContext>
      <RouterProvider router={router} />
    </AuthContext>
  )
}

export default App
