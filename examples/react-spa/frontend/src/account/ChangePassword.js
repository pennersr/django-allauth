import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { changePassword } from '../lib/allauth'
import { Navigate } from 'react-router-dom'
import { useUser } from '../auth'
import Button from '../components/Button'

export default function ChangePassword () {
  const hasCurrentPassword = useUser().has_usable_password
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [newPassword2Errors, setNewPassword2Errors] = useState([])

  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    if (newPassword !== newPassword2) {
      setNewPassword2Errors([{ param: 'new_password2', message: 'Password does not match.' }])
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
    return <Navigate to='/calculator' />
  }
  return (
    <div>
      <h1>{hasCurrentPassword ? 'Change Password' : 'Set Password'}</h1>

      <p>{hasCurrentPassword ? 'Enter your current password, followed by your new password.' : 'You currently have no password set. Enter your (new) password.'}</p>
      {hasCurrentPassword
        ? <div><label>Current password: <input autoComplete='password' value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} type='password' required /></label>
          <FormErrors param='current_password' errors={response.content?.errors} />
          </div>
        : null}
      <div><label>Password: <input autoComplete='new-password' value={newPassword} onChange={(e) => setNewPassword(e.target.value)} type='password' required /></label>
        <FormErrors param='new_password' errors={response.content?.errors} />
      </div>
      <div><label>Password (again): <input value={newPassword2} onChange={(e) => setNewPassword2(e.target.value)} type='password' required /></label>
        <FormErrors param='new_password2' errors={newPassword2Errors} />
      </div>

      <Button disabled={response.fetching} onClick={() => submit()}>{hasCurrentPassword ? 'Change' : 'Set'}</Button>
    </div>
  )
}
