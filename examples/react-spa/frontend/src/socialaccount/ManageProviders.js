import { useState, useEffect } from 'react'
import * as allauth from '../lib/allauth'
import ProviderList from './ProviderList'
import FormErrors from '../components/FormErrors'
import Button from '../components/Button'

export default function ManageProviders () {
  const [accounts, setAccounts] = useState([])
  const [response, setResponse] = useState({ fetching: false, content: { status: 200, data: [] } })

  useEffect(() => {
    setResponse((r) => { return { ...r, fetching: true } })
    allauth.getProviderAccounts().then((resp) => {
      if (resp.status === 200) {
        setAccounts(resp.data)
      }
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }, [])

  function disconnect (account) {
    setResponse({ ...response, fetching: true })
    allauth.disconnectProviderAccount(account.provider.id, account.uid).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
      if (resp.status === 200) {
        setAccounts(resp.data)
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
      <h1>Providers</h1>

      <table>
        <thead>
          <tr>
            <th>UID</th>
            <th>Account</th>
            <th>Provider</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map(account => {
            return (
              <tr key={account.uid}>
                <td>{account.uid}</td>
                <td>{account.display}</td>
                <td>{account.provider.name}</td>
                <td>
                  <Button onClick={() => disconnect(account)} disabled={response.fetching}>Disconnect</Button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <FormErrors errors={response.content?.errors} />

      <h2>Connect</h2>
      <ProviderList callbackURL='/account/providers' process={allauth.AuthProcess.CONNECT} />
    </div>
  )
}
