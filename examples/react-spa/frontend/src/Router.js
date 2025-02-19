import { useState, useEffect } from 'react'
import { AuthChangeRedirector, AnonymousRoute, AuthenticatedRoute } from './auth'
import {
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom'
import Calculator from './Calculator'
import Login from './account/Login'
import RequestLoginCode from './account/RequestLoginCode'
import ConfirmLoginCode from './account/ConfirmLoginCode'
import Logout from './account/Logout'
import Signup from './account/Signup'
import ProviderSignup from './socialaccount/ProviderSignup'
import ProviderCallback from './socialaccount/ProviderCallback'
import Home from './Home'
import ChangeEmail from './account/ChangeEmail'
import ManageProviders from './socialaccount/ManageProviders'
import VerifyEmail, { loader as verifyEmailLoader } from './account/VerifyEmail'
import VerifyEmailByCode from './account/VerifyEmailByCode'
import VerificationEmailSent from './account/VerificationEmailSent'
import RequestPasswordReset from './account/RequestPasswordReset'
import ConfirmPasswordResetCode from './account/ConfirmPasswordResetCode'
import ChangePassword from './account/ChangePassword'
import MFAOverview, { loader as mfaOverviewLoader } from './mfa/MFAOverview'
import ActivateTOTP, { loader as activateTOTPLoader } from './mfa/ActivateTOTP'
import DeactivateTOTP from './mfa/DeactivateTOTP'
import RecoveryCodes, { loader as recoveryCodesLoader } from './mfa/RecoveryCodes'
import AddWebAuthn from './mfa/AddWebAuthn'
import SignupByPasskey from './mfa/SignupByPasskey'
import ReauthenticateWebAuthn from './mfa/ReauthenticateWebAuthn'
import ListWebAuthn, { loader as listWebAuthnLoader } from './mfa/ListWebAuthn'
import GenerateRecoveryCodes, { loader as generateRecoveryCodesLoader } from './mfa/GenerateRecoveryCodes'
import { resetPasswordByLinkLoader, ResetPasswordByCode, ResetPasswordByLink } from './account/ResetPassword'
import AuthenticateTOTP from './mfa/AuthenticateTOTP'
import AuthenticateRecoveryCodes from './mfa/AuthenticateRecoveryCodes'
import AuthenticateWebAuthn from './mfa/AuthenticateWebAuthn'
import ReauthenticateRecoveryCodes from './mfa/ReauthenticateRecoveryCodes'
import ReauthenticateTOTP from './mfa/ReauthenticateTOTP'
import CreateSignupPasskey from './mfa/CreateSignupPasskey'
import Reauthenticate from './account/Reauthenticate'
import Sessions from './usersessions/Sessions'
import Root from './Root'
import { useConfig } from './auth/hooks'

function createRouter (config) {
  return createBrowserRouter([
    {
      path: '/',
      element: <AuthChangeRedirector><Root /></AuthChangeRedirector>,
      children: [
        {
          path: '/',
          element: <Home />
        },
        {
          path: '/calculator',
          element: <Calculator />
        },
        {
          path: '/account/login',
          element: <AnonymousRoute><Login /></AnonymousRoute>
        },
        {
          path: '/account/login/code',
          element: <AnonymousRoute><RequestLoginCode /></AnonymousRoute>
        },
        {
          path: '/account/login/code/confirm',
          element: <AnonymousRoute><ConfirmLoginCode /></AnonymousRoute>
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
          path: '/account/provider/callback',
          element: <ProviderCallback />
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
          path: '/account/signup/passkey',
          element: <AnonymousRoute><SignupByPasskey /></AnonymousRoute>
        },
        {
          path: '/account/signup/passkey/create',
          element: <AnonymousRoute><CreateSignupPasskey /></AnonymousRoute>
        },
        {
          path: '/account/verify-email',
          element: config.data.account.email_verification_by_code_enabled ? <VerifyEmailByCode /> : <VerificationEmailSent />
        },
        {
          path: '/account/verify-email/:key',
          element: <VerifyEmail />,
          loader: verifyEmailLoader
        },
        {
          path: '/account/password/reset',
          element: <AnonymousRoute><RequestPasswordReset /></AnonymousRoute>
        },
        {
          path: '/account/password/reset/confirm',
          element: <AnonymousRoute><ConfirmPasswordResetCode /></AnonymousRoute>
        },
        {
          path: '/account/password/reset/complete',
          element: <AnonymousRoute><ResetPasswordByCode /></AnonymousRoute>
        },
        {
          path: '/account/password/reset/key/:key',
          element: <AnonymousRoute><ResetPasswordByLink /></AnonymousRoute>,
          loader: resetPasswordByLinkLoader
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
          path: '/account/reauthenticate/totp',
          element: <AuthenticatedRoute><ReauthenticateTOTP /></AuthenticatedRoute>
        },
        {
          path: '/account/reauthenticate/recovery-codes',
          element: <AuthenticatedRoute><ReauthenticateRecoveryCodes /></AuthenticatedRoute>
        },
        {
          path: '/account/reauthenticate/webauthn',
          element: <AuthenticatedRoute><ReauthenticateWebAuthn /></AuthenticatedRoute>
        },
        {
          path: '/account/authenticate/totp',
          element: <AnonymousRoute><AuthenticateTOTP /></AnonymousRoute>
        },
        {
          path: '/account/authenticate/recovery-codes',
          element: <AnonymousRoute><AuthenticateRecoveryCodes /></AnonymousRoute>
        },
        {
          path: '/account/authenticate/webauthn',
          element: <AnonymousRoute><AuthenticateWebAuthn /></AnonymousRoute>
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
        },
        {
          path: '/account/2fa/webauthn',
          element: <AuthenticatedRoute><ListWebAuthn /></AuthenticatedRoute>,
          loader: listWebAuthnLoader
        },
        {
          path: '/account/2fa/webauthn/add',
          element: <AuthenticatedRoute><AddWebAuthn /></AuthenticatedRoute>
        },
        {
          path: '/account/sessions',
          element: <AuthenticatedRoute><Sessions /></AuthenticatedRoute>
        }
      ]
    }
  ])
}

export default function Router () {
  // If we create the router globally, the loaders of the routes already trigger
  // even before the <AuthContext/> trigger the initial loading of the auth.
  // state.
  const [router, setRouter] = useState(null)
  const config = useConfig()
  useEffect(() => {
    setRouter(createRouter(config))
  }, [config])
  return router ? <RouterProvider router={router} /> : null
}
