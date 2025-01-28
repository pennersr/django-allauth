import { setup } from './lib/allauth'

export function init () {
  if (document.location.hostname === 'app.react.demo.allauth.org') {
    setup('app', 'https://api.react.demo.allauth.org/_allauth/app/v1', false)
  } else if (document.location.hostname === 'react.demo.allauth.org') {
    setup('browser', 'https://api.react.demo.allauth.org/_allauth/browser/v1', true)
  }
}
