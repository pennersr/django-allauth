import { useUser } from './auth'

export default function Dashboard () {
  const user = useUser()
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome user {user.display}!</p>
    </div>
  )
}
