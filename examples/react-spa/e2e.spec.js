import { test, expect } from '@playwright/test'

const MAILCATCHER_URL = 'http://localhost:1080'
const BASE_URL = 'http://localhost:10000'

function emailFactory () {
  return `test-${Math.round(Math.random() * 100000000000)}@test.allauth.org`
}

function passwordFactory () {
  return `pw!${new Date().valueOf()}`
}

function socialAccountUIDFactory () {
  return '' + Math.round(Math.random() * 100000000)
}

async function clearMailcatcher (page) {
  await page.goto(MAILCATCHER_URL)
  async function acceptDialog (dialog) {
    await dialog.accept()
    page.removeListener('dialog', acceptDialog)
  }
  page.on('dialog', acceptDialog)
  await page.getByTitle('Clear all messages').click()
}

async function getLinkFromMail (page) {
  await page.waitForTimeout(500)
  await page.goto(MAILCATCHER_URL + '/messages/1.plain')
  const txt = await page.content()
  const link = txt.match(/https?:\/\/[^\s]+/)[0]
  return link
}

async function login (page, email, password) {
  await page.goto(BASE_URL + '/account/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password:').fill(password)
  await page.getByRole('button', { name: 'Login' }).click()
  await page.waitForURL(BASE_URL + '/dashboard')
}

async function logout (page) {
  // Logout
  await page.goto(BASE_URL + '/account/logout')
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL)
}

test('complete flow', async ({ page }) => {
  await clearMailcatcher(page)

  // Dashboard redirects to login
  await page.goto(BASE_URL + '/dashboard')
  await page.waitForURL(BASE_URL + '/account/login?next=%2Fdashboard')

  // No account yet, so signup.
  await page.goto(BASE_URL + '/account/signup')
  const email = emailFactory()
  await page.getByLabel('Email').fill(email)
  const password = passwordFactory()
  await page.getByLabel('Password:').fill(password)
  await page.getByLabel('Password (again)').fill(password)
  await page.getByRole('button', { name: 'Sign Up' }).click()

  // Signup requires email verification
  await page.waitForURL(BASE_URL + '/account/verify-email')
  const verifyLink = await getLinkFromMail(page)
  await page.goto(verifyLink)
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/dashboard')

  // Logout
  await logout(page)

  // Password reset
  await clearMailcatcher(page)
  await page.goto(BASE_URL + '/account/password/reset')
  await page.getByLabel('Email').fill(email)
  await page.getByRole('button').click()
  const resetLink = await getLinkFromMail(page)
  await page.goto(resetLink)
  const newPassword = passwordFactory()
  await page.getByLabel('Password:').fill(newPassword)
  await page.getByLabel('Password (again)').fill(newPassword)
  await page.getByRole('button', { name: 'Reset' }).click()
  await page.waitForURL(BASE_URL + '/account/login')

  // Login using new password
  await login(page, email, newPassword)
})

test('complete socialaccount flow', async ({ page }) => {
  await clearMailcatcher(page)

  // Dashboard redirects to login
  await page.goto(BASE_URL + '/dashboard')
  await page.waitForURL(BASE_URL + '/account/login?next=%2Fdashboard')
  await page.getByRole('button', { name: 'Dummy' }).click()

  // Dummy authenticate
  await page.waitForURL(BASE_URL + '/accounts/dummy/authenticate/*')
  const socialId = socialAccountUIDFactory()
  await page.getByLabel('Account ID').fill(socialId)
  await page.getByRole('button', { name: 'Login' }).click()

  // Provider signup
  await page.waitForURL(BASE_URL + '/account/provider/signup')
  const email = emailFactory()
  await page.getByLabel('Email').fill(email)
  await page.getByRole('button', { name: 'Sign Up' }).click()

  // Verify email
  await page.waitForURL(BASE_URL + '/account/verify-email')
  const verifyLink = await getLinkFromMail(page)
  await page.goto(verifyLink)
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/dashboard')

  // Logout
  await logout(page)

  // Login, no more signup needed.
  await page.goto(BASE_URL + '/dashboard')
  await page.waitForURL(BASE_URL + '/account/login?next=%2Fdashboard')
  await page.getByRole('button', { name: 'Dummy' }).click()

  // Dummy authenticate
  await page.waitForURL(BASE_URL + '/accounts/dummy/authenticate/*')
  await page.getByLabel('Account ID').fill(socialId)
  await page.getByRole('button', { name: 'Login' }).click()

  // Set password
  await page.waitForURL(BASE_URL + '/dashboard')
  await page.goto(BASE_URL + '/account/password/change')
  const newPassword = passwordFactory()
  await page.getByLabel('Password:').fill(newPassword)
  await page.getByLabel('Password (again)').fill(newPassword)
  await page.getByRole('button', { name: 'Set' }).click()
  await page.waitForURL(BASE_URL + '/dashboard')

  // Login using password now
  await logout(page)
  await login(page, email, newPassword)
})
