import { useState } from 'react'
import FormErrors from './FormErrors'
import { getPasswordChange, changePassword } from './lib/allauth'
import { Navigate, Link, useLoaderData } from 'react-router-dom'

export async function loader ({ params }) {
  const key = params.key
  const resp = await getPasswordChange()
  return { key, changeResponse: resp }
}

export default function ChangePassword () {
  const { key, changeResponse } = useLoaderData()

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [newPassword2Errors, setNewPassword2Errors] = useState([])

  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    if (newPassword !== newPassword2) {
      setNewPassword2Errors(['Password does not match.'])
      return
    }
    setNewPassword2Errors([])
    setResponse({ ...response, fetching: true })
    changePassword({ current_password: currentPassword, new_password: newPassword }).then((resp) => {
      setResponse((r) => { return { ...r, content: resp } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response.content?.status === 200) {
    return <Navigate to='/dashboard' />
  }
  return (
    <div>
      <h1>Change Password</h1>
      <div><label>Current password: <input autoComplete='password' value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} type='password' required /></label>
        <FormErrors errors={response.content?.error?.detail?.current_password} />
      </div>
      <div><label>Password: <input autoComplete='new-password' value={newPassword} onChange={(e) => setNewPassword(e.target.value)} type='password' required /></label>
        <FormErrors errors={response.content?.error?.detail?.new_password} />
      </div>
      <div><label>Password (again): <input value={newPassword2} onChange={(e) => setNewPassword2(e.target.value)} type='password' required /></label>
        <FormErrors errors={newPassword2Errors} />
      </div>

      <button disabled={response.fetching} onClick={() => submit()}>Reset</button>
    </div>
  )
}
