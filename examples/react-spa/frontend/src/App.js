import { AuthContextProvider, CallbackRoute, AnonymousRoute, AuthenticatedRoute } from './auth'
import {
  Outlet,
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom'
import Dashboard from './Dashboard'
import Login from './account/Login'
import Logout from './account/Logout'
import Signup from './account/Signup'
import ProviderSignup from './socialaccount/ProviderSignup'
import Home from './Home'
import ChangeEmail from './account/ChangeEmail'
import ManageProviders from './socialaccount/ManageProviders'
import VerifyEmail, { loader as verifyEmailLoader } from './account/VerifyEmail'
import VerificationEmailSent from './account/VerificationEmailSent'
import RequestPasswordReset from './account/RequestPasswordReset'
import ChangePassword from './account/ChangePassword'
import NavBar from './NavBar'
import MFAOverview, { loader as mfaOverviewLoader } from './mfa/MFAOverview'
import ActivateTOTP, { loader as activateTOTPLoader } from './mfa/ActivateTOTP'
import DeactivateTOTP from './mfa/DeactivateTOTP'
import RecoveryCodes, { loader as recoveryCodesLoader } from './mfa/RecoveryCodes'
import GenerateRecoveryCodes, { loader as generateRecoveryCodesLoader } from './mfa/GenerateRecoveryCodes'
import ResetPassword, { loader as resetPasswordLoader } from './account/ResetPassword'
import MFAAuthenticate from './mfa/MFAAuthenticate'
import Reauthenticate from './account/Reauthenticate'

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
        path: '/account/providers',
        element: <AuthenticatedRoute><ManageProviders /></AuthenticatedRoute>
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
      },
      {
        path: '/account/2fa',
        element: <AuthenticatedRoute><MFAOverview /></AuthenticatedRoute>,
        loader: mfaOverviewLoader
      },
      {
        path: '/account/reauthenticate',
        element: <AuthenticatedRoute><Reauthenticate /></AuthenticatedRoute>
      },
      {
        path: '/account/2fa/authenticate',
        element: <AnonymousRoute><MFAAuthenticate /></AnonymousRoute>
      },
      {
        path: '/account/2fa/totp/activate',
        element: <AuthenticatedRoute><ActivateTOTP /></AuthenticatedRoute>,
        loader: activateTOTPLoader
      },
      {
        path: '/account/2fa/totp/deactivate',
        element: <AuthenticatedRoute><DeactivateTOTP /></AuthenticatedRoute>
      },
      {
        path: '/account/2fa/recovery-codes',
        element: <AuthenticatedRoute><RecoveryCodes /></AuthenticatedRoute>,
        loader: recoveryCodesLoader
      },
      {
        path: '/account/2fa/recovery-codes/generate',
        element: <AuthenticatedRoute><GenerateRecoveryCodes /></AuthenticatedRoute>,
        loader: generateRecoveryCodesLoader
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
