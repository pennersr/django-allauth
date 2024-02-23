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
  page.on('dialog', async dialog => {
    await dialog.accept()
  })
  await page.getByTitle('Clear all messages').click()
}

async function getLinkFromMail (page) {
  await page.goto(MAILCATCHER_URL + '/messages/1.plain')
  const txt = await page.content()
  const link = txt.match(/https?:\/\/[^\s]+/)[0]
  return link
}

test('complete flow', async ({ page }) => {
  await clearMailcatcher(page)

  await page.goto(BASE_URL + '/dashboard')
  await page.waitForURL(BASE_URL + '/account/login')

  await page.goto(BASE_URL + '/account/signup')
  const email = emailFactory()
  await page.getByLabel('Email').fill(email)
  const password = passwordFactory()
  await page.getByLabel('Password:').fill(password)
  await page.getByLabel('Password (again)').fill(password)
  await page.getByRole('button').click()

  await page.waitForURL(BASE_URL + '/account/verify-email')
  const verifyLink = await getLinkFromMail(page)
  await page.goto(verifyLink)
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL + '/dashboard')

  await page.goto(BASE_URL + '/account/logout')
  await page.getByRole('button').click()
  await page.waitForURL(BASE_URL)
})
