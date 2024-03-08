import { useEffect, createContext, useState } from 'react'
import { getAuth } from '../lib/allauth'

export const AuthContext = createContext(null)

function Loading () {
  return <div>Starting...</div>
}

function LoadingError () {
  return <div>Loading error!</div>
}

export function AuthContextProvider (props) {
  const [auth, setAuth] = useState(undefined)

  useEffect(() => {
    function onAuthChanged (e) {
      console.log('Authentication status updated')
      setAuth(e.detail)
    }

    document.addEventListener('allauth.auth.change', onAuthChanged)
    getAuth().then(data => setAuth(data)).catch((e) => {
      console.error(e)
      setAuth(false)
    })
    return () => {
      document.removeEventListener('allauth.auth.change', onAuthChanged)
    }
  }, [])

  return (
    <AuthContext.Provider value={{ auth }}>
      {(typeof auth === 'undefined')
        ? <Loading />
        : (auth === false
            ? <LoadingError />
            : props.children)}
    </AuthContext.Provider>
  )
}
