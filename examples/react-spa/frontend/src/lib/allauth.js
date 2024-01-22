import { getCSRFToken } from './django'

const BASE_URL = '/accounts'
const ACCEPT_JSON = {
  accept: 'application/json'
}

export const URLs = Object.freeze({
  CONFIRM_EMAIL: BASE_URL + '/confirm-email/',
  LOGIN: BASE_URL + '/login/',
  LOGOUT: BASE_URL + '/logout/',
  SIGNUP: BASE_URL + '/signup/',
  RESET_PASSWORD: BASE_URL + '/password/reset/',
  RESET_PASSWORD_DONE: BASE_URL + '/password/reset/done/',
  RESET_PASSWORD_FROM_KEY: BASE_URL + '/password/reset/key/',
  PROFILE: BASE_URL + '/profile/',
  EMAIL: BASE_URL + '/email/'
})

async function fetchFormPost (path, data) {
  const formData = new FormData()
  Object.keys(data).forEach(k => {
    formData.append(k, data[k])
  })
  formData.append('csrfmiddlewaretoken', getCSRFToken())

  const resp = await fetch(path, {
    method: 'POST',
    headers: {
      ...ACCEPT_JSON,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams(formData).toString()
  })
  if (!resp.ok && ![400, 404].includes(resp.status)) {
    throw new Error('error submitting data')
  }
  return await resp.json()
}

export async function postLogin (data) {
  return await fetchFormPost(URLs.LOGIN, data)
}

export async function postLogout () {
  return await fetchFormPost(URLs.LOGOUT, {})
}

export async function postSignUp (data) {
  return await fetchFormPost(URLs.SIGNUP, data)
}

export async function postResetPassword (email) {
  return await fetchFormPost(URLs.RESET_PASSWORD, { email })
}

export async function getEmailConfirmation (key) {
  return await fetch(`${URLs.CONFIRM_EMAIL}${encodeURIComponent(key)}/`,
    {
      headers: ACCEPT_JSON
    }).then(resp => resp.json())
}

export async function getEmailAddresses () {
  return await fetch(URLs.EMAIL,
    {
      headers: ACCEPT_JSON
    }).then(resp => resp.json())
}

export async function postAddEmail (email) {
  return await fetchFormPost(URLs.EMAIL, { action_add: '', email })
}

export async function postEmailConfirmation (key) {
  return await fetchFormPost(`${URLs.CONFIRM_EMAIL}${encodeURIComponent(key)}/`, {})
}

export async function getPasswordReset (key) {
  return await fetch(`${URLs.RESET_PASSWORD_FROM_KEY}${encodeURIComponent(key)}/`,
    {
      headers: ACCEPT_JSON
    }).then(resp => resp.json())
}

export async function postPasswordReset (key, data) {
  return await fetchFormPost(`${URLs.RESET_PASSWORD_FROM_KEY}${encodeURIComponent(key)}/`, data)
}
