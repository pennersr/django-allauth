import { useState } from 'react'
import {
  useLoaderData,
  Navigate
} from 'react-router-dom'
import { getEmailVerification, verifyEmail } from '../lib/allauth'
import Button from '../components/Button'

export async function loader ({ params }) {
  const key = params.key
  const resp = await getEmailVerification(key)
  return { key, verification: resp }
}

export default function VerifyEmail () {
  const { key, verification } = useLoaderData()
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    verifyEmail(key).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  if ([200, 401].includes(response.content?.status)) {
    return <Navigate to='/account/email' />
  }

  let body = null
  if (verification.status === 200) {
    body = (
      <>
        <p>Please confirm that <a href={'mailto:' + verification.data.email}>{verification.data.email}</a> is an email address for user {verification.data.user.str}.</p>
        <Button disabled={response.fetching} onClick={() => submit()}>Confirm</Button>
      </>
    )
  } else if (!verification.data?.email) {
    body = <p>Invalid verification link.</p>
  } else {
    body = <p>Unable to confirm email <a href={'mailto:' + verification.data.email}>{verification.data.email}</a> because it is already confirmed.</p>
  }
  return (
    <div>
      <h1>Confirm Email Address</h1>
      {body}
    </div>
  )
}
