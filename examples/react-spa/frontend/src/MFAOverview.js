import { useState, useEffect } from 'react'
import { Link, useLoaderData } from 'react-router-dom'

import * as allauth from './lib/allauth'

export async function loader ({ params }) {
  const resp = await allauth.getAuthenticators()
  return { authenticators: resp.data }
}

export default function MFAOverview (props) {
  const { authenticators } = useLoaderData()
  const totp = authenticators.find(authenticator => authenticator.type === allauth.AuthenticatorType.TOTP)
  return (
    <section>
      <h1>Two-Factor Authentication</h1>

      <h2>Authenticator App</h2>

      {totp
        ? <><p>
          Authentication using an authenticator app is active.
            </p>
          <Link to='/account/2fa/totp/deactivate'>Deactivate</Link>
        </>
        : <><p>An authenticator app is not active..</p>
          <Link to='/account/2fa/totp/activate'>Activate</Link>
          </>}

      <h2>Recovery Codes</h2>

      <p>No recovery codes set up.</p>

    </section>
  )
}
