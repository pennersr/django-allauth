import { useState } from 'react'
import { useLoaderData } from 'react-router-dom'
import { getEmailConfirmation, postEmailConfirmation } from './lib/allauth'

export async function loader ({ params }) {
  const key = params.key
  const resp = await getEmailConfirmation(key)
  return { key, confirmation: resp.data }
}

export default function ConfirmEmail () {
  const { key, confirmation } = useLoaderData()
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    postEmailConfirmation(key).then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  let body = null
  if (confirmation.can_confirm) {
    body = (
      <>
        <p>Please confirm that <a href={'mailto:' + confirmation.email}>{confirmation.email}</a> is an email address for user {confirmation.user.display}.</p>
        <button disabled={response.fetching} onClick={() => submit()}>Confirm</button>
      </>
    )
  } else if (!confirmation.email) {
    body = <p>Invalid confirmation link.</p>
  } else {
    body = <p>Unable to confirm email <a href={'mailto:' + confirmation.email}>{confirmation.email}</a> because it is already confirmed.</p>
  }
  return (
    <div>
      <h1>Confirm Email Address</h1>
      {body}
    </div>
  )
}
