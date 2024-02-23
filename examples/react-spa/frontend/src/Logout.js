import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { logout } from './lib/allauth'

export default function Logout () {
  const [response, setResponse] = useState({ fetching: false, data: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    logout().then((data) => {
      setResponse((r) => { return { ...r, data } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response?.data) {
    return <Navigate to='/' />
  }
  return (
    <div>
      <h1>Logout</h1>
      <p>
        Are you sure you want to logout?
      </p>

      <button disabled={response.fetching} onClick={() => submit()}>Logout</button>
    </div>
  )
}
