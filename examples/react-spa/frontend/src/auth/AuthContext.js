import { useEffect, useContext, createContext, useState } from 'react'
import { getAuth } from '../lib/allauth'

const UserContext = createContext(null)

function Loading () {
  return <div>Starting...</div>
}

function LoadingError () {
  return <div>Loading error!</div>
}

export function AuthContext (props) {
  const [auth, setAuth] = useState(undefined)

  useEffect(() => {
    function onAuthChanged (e) {
      console.log('onauthchanged')
      setAuth(e.detail)
    }

    document.addEventListener('allauth.auth.change', onAuthChanged)
    getAuth().then(data => setAuth(data)).catch((e) => {
      console.error(e)
      console.log('onautherrrr')
      setAuth(false)
    })
    return () => {
      document.removeEventListener('allauth.auth.change', onAuthChanged)
    }
  }, [])

  return (
    <UserContext.Provider value={{ auth }}>
      {(typeof auth === 'undefined')
        ? <Loading />
        : (auth === false
            ? <LoadingError />
            : props.children)}
    </UserContext.Provider>
  )
}

export function useAuth () {
  return useContext(UserContext)?.auth
}

export function useUser () {
  const auth = useContext(UserContext)?.auth
  return (auth.status === 200) ? auth.data : null
}
