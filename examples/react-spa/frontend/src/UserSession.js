import { useCallback, useEffect, useContext, createContext, useState } from 'react'
import { postLogout, postLogin } from './lib/allauth'

const UserContext = createContext(null)

function Loading () {
  return <div>Starting...</div>
}

function LoadingError () {
  return <div>Loading error!</div>
}

async function fetchUser () {
  const res = await fetch('/accounts/profile/')
  if (res.status === 401) {
    return null
  }
  if (!res.ok) {
    throw new Error('error fetching user')
  }
  return await res.json()
}

export default function UserSession (props) {
  const [user, setUser] = useState(undefined)

  useEffect(() => {
    fetchUser().then(data => setUser(data)).catch((e) => {
      console.error(e)
      setUser(false)
    })
  }, [])

  const loginCb = useCallback((data) => {
    return postLogin(data).then((resp) => {
      return fetchUser().then((fuData) => {
        setUser(fuData)
        return resp
      })
    })
  }, [setUser])

  const logoutCb = useCallback(() => {
    return postLogout().then((resp) => {
      setUser(null)
      return resp
    })
  }, [setUser])

  return (
    <UserContext.Provider value={{ login: loginCb, logout: logoutCb, user }}>
      {(typeof user === 'undefined')
        ? <Loading />
        : (user === false
            ? <LoadingError />
            : props.children)}
    </UserContext.Provider>
  )
}

export function useUser () {
  return useContext(UserContext)?.user
}

export function usePostLogin () {
  return useContext(UserContext)?.login
}

export function usePostLogout () {
  return useContext(UserContext)?.logout
}
