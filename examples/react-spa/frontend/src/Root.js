import NavBar from './NavBar'
import { Outlet } from 'react-router-dom'

export default function Root () {
  return (
    <div>
      <NavBar />
      <Outlet />
    </div>
  )
}
