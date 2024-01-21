import UserSession from './UserSession'
import {
  Outlet,
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom'
import Dashboard from './Dashboard'
import Login from './Login'
import Logout from './Logout'
import SignUp from './SignUp'
import Home from './Home'
import ChangeEmail from './ChangeEmail'
import ConfirmEmail, { loader as confirmEmailLoader } from './ConfirmEmail'
import ConfirmationEmailSent from './ConfirmationEmailSent'
import ResetPassword from './ResetPassword'
import NavBar from './NavBar'
import ResetPasswordFromKey, { loader as resetPasswordFromKeyLoader } from './ResetPasswordFromKey'
import { AnonymousRoute, AuthenticatedRoute } from './auth'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: '/',
        element: <Home />
      },
      {
        path: '/dashboard',
        element: <AuthenticatedRoute><Dashboard /></AuthenticatedRoute>
      },
      {
        path: '/login',
        element: <AnonymousRoute><Login /></AnonymousRoute>
      },
      {
        path: '/email',
        element: <AuthenticatedRoute><ChangeEmail /></AuthenticatedRoute>
      },
      {
        path: '/logout',
        element: <Logout />
      },
      {
        path: '/signup',
        element: <AnonymousRoute><SignUp /></AnonymousRoute>
      },
      {
        path: '/confirm-email',
        element: <ConfirmationEmailSent />
      },
      {
        path: '/confirm-email/:key',
        element: <ConfirmEmail />,
        loader: confirmEmailLoader
      },
      {
        path: '/password/reset',
        element: <ResetPassword />
      },
      {
        path: '/password/reset/key/:key',
        element: <ResetPasswordFromKey />,
        loader: resetPasswordFromKeyLoader
      }
    ]
  }
])

function Root () {
  return (
    <div>
      <NavBar />
      <Outlet />
    </div>
  )
}

function App () {
  return (
    <UserSession>
      <RouterProvider router={router} />
    </UserSession>
  )
}

export default App
