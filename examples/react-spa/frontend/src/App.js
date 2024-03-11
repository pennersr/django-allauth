import { AuthContextProvider, CallbackRoute, AnonymousRoute, AuthenticatedRoute } from './auth'
import {
  Outlet,
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom'
import Dashboard from './Dashboard'
import Login from './Login'
import Logout from './Logout'
import Signup from './Signup'
import ProviderSignup from './ProviderSignup'
import Home from './Home'
import ChangeEmail from './ChangeEmail'
import VerifyEmail, { loader as verifyEmailLoader } from './VerifyEmail'
import VerificationEmailSent from './VerificationEmailSent'
import RequestPasswordReset from './RequestPasswordReset'
import ChangePassword from './ChangePassword'
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
        path: '/account/callback',
        element: <CallbackRoute />
      },
      {
        path: '/account/provider/signup',
        element: <AnonymousRoute><ProviderSignup /></AnonymousRoute>
      },
      {
        path: '/account/signup',
        element: <AnonymousRoute><Signup /></AnonymousRoute>
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
        element: <AnonymousRoute><RequestPasswordReset /></AnonymousRoute>
      },
      {
        path: '/account/password/reset/key/:key',
        element: <AnonymousRoute><ResetPassword /></AnonymousRoute>,
        loader: resetPasswordLoader
      },
      {
        path: '/account/password/change',
        element: <AuthenticatedRoute><ChangePassword /></AuthenticatedRoute>
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
    <AuthContextProvider>
      <RouterProvider router={router} />
    </AuthContextProvider>
  )
}

export default App
