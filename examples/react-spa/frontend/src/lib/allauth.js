import { getCSRFToken } from './django'

const Client = Object.freeze({
  APP: 'app',
  BROWSER: 'browser'
})

const CLIENT = Client.BROWSER

const BASE_URL = `/_allauth/${CLIENT}/v1`
const ACCEPT_JSON = {
  accept: 'application/json'
}

export const AuthProcess = Object.freeze({
  LOGIN: 'login',
  CONNECT: 'connect'
})

export const Flows = Object.freeze({
  VERIFY_EMAIL: 'verify_email',
  LOGIN: 'login',
  SIGNUP: 'signup',
  PROVIDER_LOGIN: 'provider_login',
  PROVIDER_SIGNUP: 'provider_signup',
  MFA_AUTHENTICATE: 'mfa_authenticate',
  REAUTHENTICATE: 'reauthenticate',
  MFA_REAUTHENTICATE: 'mfa_reauthenticate'
})

export const URLs = Object.freeze({
  // Meta
  CONFIG: BASE_URL + '/config',

  // Account management
  CHANGE_PASSWORD: BASE_URL + '/account/password/change',
  EMAIL: BASE_URL + '/account/email',
  PROVIDERS: BASE_URL + '/account/providers',

  // Account management: 2FA
  AUTHENTICATORS: BASE_URL + '/account/2fa/authenticators',
  RECOVERY_CODES: BASE_URL + '/account/2fa/authenticators/recovery_codes',
  TOTP_AUTHENTICATOR: BASE_URL + '/account/2fa/authenticators/totp',

  // Auth: Basics
  AUTH: BASE_URL + '/auth',
  LOGIN: BASE_URL + '/auth/login',
  LOGOUT: BASE_URL + '/auth/logout',
  REAUTHENTICATE: BASE_URL + '/auth/reauthenticate',
  REQUEST_PASSWORD_RESET: BASE_URL + '/auth/password/request',
  RESET_PASSWORD: BASE_URL + '/auth/password/reset',
  SIGNUP: BASE_URL + '/auth/signup',
  VERIFY_EMAIL: BASE_URL + '/auth/verify_email',

  // Auth: 2FA
  MFA_AUTHENTICATE: BASE_URL + '/auth/2fa/authenticate',
  MFA_REAUTHENTICATE: BASE_URL + '/auth/2fa/reauthenticate',

  // Auth: Social
  PROVIDER_SIGNUP: BASE_URL + '/auth/provider/signup',
  REDIRECT_TO_PROVIDER: BASE_URL + '/auth/provider/redirect',

  // Auth: Sessions
  SESSIONS: BASE_URL + '/auth/sessions'
})

export const AuthenticatorType = Object.freeze({
  TOTP: 'totp',
  RECOVERY_CODES: 'recovery_codes'
})

function postForm (action, data) {
  const f = document.createElement('form')
  f.method = 'POST'
  f.action = action

  for (const key in data) {
    const d = document.createElement('input')
    d.type = 'hidden'
    d.name = key
    d.value = data[key]
    f.appendChild(d)
  }
  document.body.appendChild(f)
  f.submit()
}

const tokenStorage = sessionStorage

async function request (method, path, data) {
  const options = {
    method,
    headers: {
      ...ACCEPT_JSON
    }
  }
  // Don't pass along authentication related headers to the config endpoint.
  if (path !== URLs.CONFIG) {
    if (CLIENT === Client.BROWSER) {
      options.headers['X-CSRFToken'] = getCSRFToken()
    } else if (CLIENT === Client.APP) {
      // IMPORTANT!: Do NOT use `Client.APP` in a browser context, as you will
      // be vulnerable to CSRF attacks. This logic is only here for
      // development/demonstration/testing purposes...
      options.headers['User-Agent'] = 'django-allauth example app'
      const sessionToken = tokenStorage.getItem('sessionToken')
      if (sessionToken) {
        options.headers['X-Session-Token'] = sessionToken
      }
    }
  }

  if (typeof data !== 'undefined') {
    options.body = JSON.stringify(data)
    options.headers['Content-Type'] = 'application/json'
  }
  const resp = await fetch(path, options)
  const msg = await resp.json()
  if (msg.status === 410) {
    tokenStorage.removeItem('sessionToken')
  }
  if ([401, 410].includes(msg.status) || (msg.status === 200 && msg.meta?.is_authenticated)) {
    if (msg.meta?.session_token) {
      tokenStorage.setItem('sessionToken', msg.meta.session_token)
    }
    const event = new CustomEvent('allauth.auth.change', { detail: msg })
    document.dispatchEvent(event)
  }
  return msg
}

export async function login (data) {
  return await request('POST', URLs.LOGIN, data)
}

export async function reauthenticate (data) {
  return await request('POST', URLs.REAUTHENTICATE, data)
}

export async function logout () {
  return await request('POST', URLs.LOGOUT)
}

export async function signUp (data) {
  return await request('POST', URLs.SIGNUP, data)
}

export async function providerSignup (data) {
  return await request('POST', URLs.PROVIDER_SIGNUP, data)
}

export async function getProviderAccounts () {
  return await request('GET', URLs.PROVIDERS)
}

export async function disconnectProviderAccount (providerId, accountUid) {
  return await request('DELETE', URLs.PROVIDERS, { provider: providerId, account: accountUid })
}

export async function requestPasswordReset (email) {
  return await request('POST', URLs.REQUEST_PASSWORD_RESET, { email })
}

export async function getEmailVerification (key) {
  return await request('GET', `${URLs.VERIFY_EMAIL}?key=${encodeURIComponent(key)}`)
}

export async function getEmailAddresses () {
  return await request('GET', URLs.EMAIL)
}
export async function getSessions () {
  return await request('GET', URLs.SESSIONS)
}

export async function endSessions (ids) {
  return await request('DELETE', URLs.SESSIONS, { sessions: ids })
}

export async function getAuthenticators () {
  return await request('GET', URLs.AUTHENTICATORS)
}

export async function getTOTPAuthenticator () {
  return await request('GET', URLs.TOTP_AUTHENTICATOR)
}

export async function mfaAuthenticate (code) {
  return await request('POST', URLs.MFA_AUTHENTICATE, { code })
}

export async function mfaReauthenticate (code) {
  return await request('POST', URLs.MFA_REAUTHENTICATE, { code })
}

export async function activateTOTPAuthenticator (code) {
  return await request('POST', URLs.TOTP_AUTHENTICATOR, { code })
}

export async function deactivateTOTPAuthenticator () {
  return await request('DELETE', URLs.TOTP_AUTHENTICATOR)
}

export async function getRecoveryCodes () {
  return await request('GET', URLs.RECOVERY_CODES)
}

export async function generateRecoveryCodes () {
  return await request('POST', URLs.RECOVERY_CODES)
}

export async function getConfig () {
  return await request('GET', URLs.CONFIG)
}

export async function addEmail (email) {
  return await request('POST', URLs.EMAIL, { email })
}

export async function deleteEmail (email) {
  return await request('DELETE', URLs.EMAIL, { email })
}

export async function markEmailAsPrimary (email) {
  return await request('PATCH', URLs.EMAIL, { email, primary: true })
}

export async function requestEmailVerification (email) {
  return await request('PUT', URLs.EMAIL, { email })
}

export async function verifyEmail (key) {
  return await request('POST', URLs.VERIFY_EMAIL, { key })
}

export async function getPasswordReset (key) {
  return await request('GET', `${URLs.RESET_PASSWORD}?key=${encodeURIComponent(key)}`)
}

export async function resetPassword (data) {
  return await request('POST', URLs.RESET_PASSWORD, data)
}

export async function changePassword (data) {
  return await request('POST', URLs.CHANGE_PASSWORD, data)
}

export async function getAuth () {
  return await request('GET', URLs.AUTH)
}

export function redirectToProvider (providerId, callbackURL, process = AuthProcess.LOGIN) {
  postForm(URLs.REDIRECT_TO_PROVIDER, {
    provider: providerId,
    process,
    callback_url: callbackURL,
    csrfmiddlewaretoken: getCSRFToken()
  })
}
