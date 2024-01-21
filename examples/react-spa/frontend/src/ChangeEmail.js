import { useState, useEffect } from 'react'
import { getEmailAddresses, postAddEmail } from './lib/allauth'
import FormErrors from './FormErrors'

export default function ChangeEmail () {
  const [trigger, setTrigger] = useState(0)
  const [email, setEmail] = useState('')
  const [emailAddresses, setEmailAddresses] = useState([])
  const [response, setResponse] = useState({ fetching: false, data: null })

  useEffect(() => {
    getEmailAddresses().then((d) => {
      setEmailAddresses(d.data)
    })
  }, [trigger])

  function submit () {
    setResponse({ ...response, fetching: true })
    postAddEmail(email).then((data) => {
      setResponse((r) => { return { ...r, data } })
      setTrigger(trigger + 1)
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
          </tr>
        </thead>
        <tbody>
          {emailAddresses.map(ea => {
            return (<tr key={ea.email}><td>{ea.email}</td><td>{ea.verified ? '✅' : '❌'}</td><td>{ea.primary ? '✅' : '❌'}</td></tr>)
          })}
        </tbody>
      </table>

      <h2>Add Email</h2>

      <FormErrors errors={response?.data?.form?.errors} />

      <div><label>Email <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' required /></label>
        <FormErrors errors={response?.data?.form?.fields?.email?.errors} />
      </div>
      <button disabled={response.fetching} onClick={() => submit()}>Add</button>

    </div>
  )
}
