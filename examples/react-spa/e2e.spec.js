import { test, expect } from '@playwright/test'

const MAILCATCHER_URL = 'http://localhost:1080'
const BASE_URL = 'http://localhost:10000'

function emailFactory () {
  return `test-${Math.round(Math.random() * 100000000000)}@test.allauth.org`
}

function passwordFactory () {
  return `pw!${new Date().valueOf()}`
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

test('complete flow', async ({ page }) => {
  await clearMailcatcher(page)

  // Dashboard redirects to login
  await page.goto(BASE_URL + '/dashboard')
  await page.waitForURL(BASE_URL + '/account/login')

  // No account yet, so signup.
  await page.goto(BASE_URL + '/account/signup')
  const email = emailFactory()
  await page.getByLabel('Email').fill(email)
  const password = passwordFactory()
  await page.getByLabel('Password:').fill(password)
  await page.getByLabel('Password (again)').fill(password)
  await page.getByRole('button').click()

  // Signup requires email verification
  await page.waitForURL(BASE_URL + '/account/verify-email')
  const verifyLink = await getLinkFromMail(page)
  await page.goto(verifyLink)
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/dashboard')

  // Logout
  await page.goto(BASE_URL + '/account/logout')
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL)

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
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/account/login')

  // Login using new password
  await page.goto(BASE_URL + '/account/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password:').fill(newPassword)
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/dashboard')
})
