import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { logout } from '../lib/allauth'
import Button from '../components/Button'

export default function Logout () {
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    logout().then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  if (response.content) {
    return <Navigate to='/' />
  }
  return (
    <div>
      <h1>Logout</h1>
      <p>
        Are you sure you want to logout?
      </p>

      <Button disabled={response.fetching} onClick={() => submit()}>Logout</Button>
    </div>
  )
}
