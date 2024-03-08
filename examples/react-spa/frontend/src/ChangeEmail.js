import { useState, useEffect } from 'react'
import * as allauth from './lib/allauth'
import FormErrors from './FormErrors'

export default function ChangeEmail () {
  const [email, setEmail] = useState('')
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

  function addEmail () {
    setResponse({ ...response, fetching: true })
    allauth.addEmail(email).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
      if (resp.status === 200) {
        setEmailAddresses(resp.data)
        setEmail('')
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
    allauth.requestEmailVerification(email).catch((e) => {
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
                <td>{ea.primary ? '✅' : '❌'}</td>
                <td>
                  {ea.verified ? '' : <button onClick={() => requestEmailVerification(ea.email)} disabled={response.fetching}>Resend</button>}
                  {ea.primary ? '' : <button onClick={() => deleteEmail(ea.email)} disabled={response.fetching}>Remove</button>}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <h2>Add Email</h2>

      <FormErrors errors={response?.content.error?.detail?._all__} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response?.content?.error?.detail?.email} />
      </div>
      <button disabled={response.fetching} onClick={() => addEmail()}>Add</button>

    </div>
  )
}
