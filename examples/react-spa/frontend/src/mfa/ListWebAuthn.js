import { useState } from 'react'
import { Link, useLoaderData, Navigate } from 'react-router-dom'
import Button from '../components/Button'
import * as allauth from '../lib/allauth'

export async function loader ({ params }) {
  const resp = await allauth.getAuthenticators()
  return { authenticators: resp.data }
}

function Authenticator (props) {
  const [name, setName] = useState(props.authenticator.name)
  const { authenticator } = props
  function onSubmit (e) {
    e.preventDefault()
    props.onSave(name)
  }
  return (
    <tr>
      {props.editting
        ? <td>
          <form onSubmit={onSubmit}>
            <input onChange={(e) => setName(e.target.value)} value={name} type='text' />
            <Button type='button' onClick={() => props.onCancel()}>        Cancel</Button>
          </form>
          </td>
        : <td>{authenticator.name} <Button onClick={() => props.onEdit()}>        Edit</Button>
          </td>}
      <td>{typeof authenticator.is_passwordless === 'undefined'
        ? 'Type unspecified'
        : (authenticator.is_passwordless ? 'Passkey' : 'Security key')}
      </td>
      <td>{new Date(authenticator.created_at * 1000).toLocaleString()}</td>
      <td>{authenticator.last_used_at ? new Date(authenticator.last_used_at * 1000).toLocaleString() : 'Unused'}</td>
      <td>
        <Button onClick={() => props.onDelete()}>Delete</Button>
      </td>
    </tr>
  )
}

export default function ListWebAuthn (props) {
  const { authenticators } = useLoaderData()
  const [editId, setEditId] = useState(null)
  const [keys, setKeys] = useState(() => authenticators.filter(authenticator => authenticator.type === allauth.AuthenticatorType.WEBAUTHN))
  const [response, setResponse] = useState({ fetching: false, content: null })

  async function optimisticSetKeys (newKeys, op) {
    setResponse({ ...response, fetching: true })
    const oldKeys = keys
    setEditId(null)
    setKeys(newKeys)
    try {
      const ok = await op()
      if (!ok) {
        setKeys(oldKeys)
      }
    } catch (e) {
      setKeys(oldKeys)
      console.error(e)
      window.alert(e)
    }
    setResponse((r) => { return { ...r, fetching: false } })
  }

  async function deleteKey (key) {
    const newKeys = keys.filter((k) => k.id !== key.id)
    await optimisticSetKeys(newKeys, async () => {
      const resp = await allauth.deleteWebAuthnCredential([key.id])
      return (resp.status === 200)
    })
  }

  async function onSave (key, name) {
    const newKeys = keys.filter((k) => k.id !== key.id)
    newKeys.push({ ...key, name })
    await optimisticSetKeys(newKeys, async () => {
      const resp = await allauth.updateWebAuthnCredential(key.id, { name })
      return (resp.status === 200)
    })
  }

  if (!keys.length && !response.fetching) {
    return <Navigate to='/account/2fa' />
  }

  return (
    <section>
      <h1>Security Keys</h1>

      <table className='table table-striped'>
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Created At</th>
            <th>Last Used At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {keys.map(key => {
            return (
              <Authenticator
                key={key.id}
                editting={key.id === editId} authenticator={key} onCancel={() => setEditId(null)}
                onSave={(name) => onSave(key, name)}
                onEdit={() => setEditId(key.id)} onDelete={() => deleteKey(key)}
              />
            )
          })}
        </tbody>
      </table>
      <Link to='/account/2fa/webauthn/add'>Add</Link>
    </section>
  )
}
