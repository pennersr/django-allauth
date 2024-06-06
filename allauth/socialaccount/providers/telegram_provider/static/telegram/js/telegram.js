/* global document, window */
(function () {
  'use strict'
  const f = document.createElement('form')
  f.method = 'POST'
  f.action = ''

  const fragment = window.location.hash.substr(1)
  const fragmentParams = new URLSearchParams(fragment)
  for (const param of fragmentParams) {
    const d = document.createElement('input')
    d.type = 'hidden'
    d.name = param[0]
    d.value = param[1]
    f.appendChild(d)
  }
  document.body.appendChild(f)
  f.submit()
})()
