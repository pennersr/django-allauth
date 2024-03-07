import { getCSRFToken } from './django'

const BASE_URL = '/_allauth/browser/v1'
const ACCEPT_JSON = {
  accept: 'application/json'
}

export const Flows = Object.freeze({
  VERIFY_EMAIL: 'verify_email',
  LOGIN: 'login',
  SIGNUP: 'signup',
  PROVIDER_LOGIN: 'provider_login'
})

export const URLs = Object.freeze({
  LOGIN: BASE_URL + '/auth/login',
  LOGOUT: BASE_URL + '/auth/logout',
  AUTH: BASE_URL + '/auth',
  SIGNUP: BASE_URL + '/auth/signup',
  VERIFY_EMAIL: BASE_URL + '/auth/verify_email',
  REQUEST_PASSWORD_RESET: BASE_URL + '/auth/password/request',
  RESET_PASSWORD: BASE_URL + '/auth/password/reset',
  CHANGE_PASSWORD: BASE_URL + '/account/password/change',
  EMAIL: BASE_URL + '/account/email'
})

async function request (method, path, data) {
  const options = {
    method,
    headers: {
      ...ACCEPT_JSON,
      'X-CSRFToken': getCSRFToken()
    }
  }
  if (typeof data !== 'undefined') {
    options.body = JSON.stringify(data)
    options.headers['Content-Type'] = 'application/json'
  }
  const resp = await fetch(path, options)
  const msg = await resp.json()
  if (msg.status === 401 || (msg.status === 200 && msg.meta?.is_authenticated)) {
    const event = new CustomEvent('allauth.auth.change', { detail: msg })
    document.dispatchEvent(event)
  }
  return msg
}

export async function login (data) {
  return await request('POST', URLs.LOGIN, data)
}

export async function logout () {
  return await request('POST', URLs.LOGOUT)
}

export async function signUp (data) {
  return await request('POST', URLs.SIGNUP, data)
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

export async function getPasswordChange (key) {
  return await request('GET', URLs.CHANGE_PASSWORD)
}

export async function changePassword (data) {
  return await request('POST', URLs.CHANGE_PASSWORD, data)
}

export async function getAuth () {
  return await request('GET', URLs.AUTH)
}
