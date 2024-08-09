import { useState, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import * as allauth from '../lib/allauth'
import FormErrors from '../components/FormErrors'
import Button from '../components/Button'
import { useConfig } from '../auth/hooks'

export default function ChangeEmail () {
  const config = useConfig()
  const [email, setEmail] = useState('')
  const [redirectToVerification, setRedirectToVerification] = useState(false)
  const [emailAddresses, setEmailAddresses] = useState([])
  const [response, setResponse] = useState({ fetching: false, content: { status: 200, data: [] } })

  useEffect(() => {
    setResponse((r) => { return { ...r, fetching: true } })
    allauth.getEmailAddresses().then((resp) => {
      if (resp.status === 200) {
        setEmailAddresses(resp.data)
      }
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }, [])

  function requestRedirectToVerification () {
    if (config.data.account.email_verification_by_code_enabled) {
      setRedirectToVerification(true)
    }
  }

  function addEmail () {
    setResponse({ ...response, fetching: true })
    allauth.addEmail(email).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
      if (resp.status === 200) {
        setEmailAddresses(resp.data)
        setEmail('')
        requestRedirectToVerification()
      }
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  function requestEmailVerification (email) {
    setResponse({ ...response, fetching: true })
    allauth.requestEmailVerification(email).then((resp) => {
      if (resp.status === 200) {
        requestRedirectToVerification()
      }
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  function deleteEmail (email) {
    setResponse({ ...response, fetching: true })
    allauth.deleteEmail(email).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
      if (resp.status === 200) {
        setEmailAddresses(resp.data)
      }
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  function markAsPrimary (email) {
    setResponse({ ...response, fetching: true })
    allauth.markEmailAsPrimary(email).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
      if (resp.status === 200) {
        setEmailAddresses(resp.data)
      }
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }

  if (redirectToVerification) {
    return <Navigate to='/account/verify-email' />
  }

  return (
    <div>
      <h1>Change Email</h1>

      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Verified</th>
            <th>Primary</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {emailAddresses.map(ea => {
            return (
              <tr key={ea.email}>
                <td>{ea.email}</td>
                <td>{ea.verified
                  ? '✅'
                  : '❌'}
                </td>
                <td>
                  <input onChange={() => markAsPrimary(ea.email)} type='radio' checked={ea.primary} />
                </td>
                <td>
                  {ea.verified ? '' : <Button onClick={() => requestEmailVerification(ea.email)} disabled={response.fetching}>Resend</Button>}
                  {ea.primary ? '' : <Button onClick={() => deleteEmail(ea.email)} disabled={response.fetching}>Remove</Button>}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <h2>Add Email</h2>

      <FormErrors errors={response.content.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors param='email' errors={response.content?.errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => addEmail()}>Add</Button>

    </div>
  )
}
