import { useState } from 'react'
import { Navigate, useLoaderData } from 'react-router-dom'

import * as allauth from '../lib/allauth'

export async function loader ({ params }) {
  const resp = await allauth.getRecoveryCodes()
  return { recoveryCodes: resp }
}

export default function GenerateRecoveryCodes () {
  const { recoveryCodes } = useLoaderData()
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    allauth.generateRecoveryCodes().then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response?.data?.status === 200) {
    return <Navigate to='/account/2fa/recovery-codes' />
  }

  const hasCodes = recoveryCodes.status === 200 && recoveryCodes.data.unused_code_count > 0
  return (
    <section>
      <h1>Recovery Codes</h1>

      <p>You are about to generate a new set of recovery codes for your account.
        {hasCodes ? 'This action will invalidate your existing codes.' : ''} Are you sure?
      </p>

      <button onClick={() => submit()}>Generate</button>

    </section>
  )
}
