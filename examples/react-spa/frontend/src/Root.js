import NavBar from './NavBar'
import { Outlet } from 'react-router-dom'

export default function Root () {
  return (
    <>
      <NavBar />
      <main className='flex-shrink-0'>

        <div className='container'>
          <Outlet />
        </div>
      </main>

      <footer className='footer mt-auto py-3 bg-body-tertiary'>
        <div className='container'>
          <span className='text-body-secondary'>⚠️ This sole purpose of this example React app is to demonstrate the use of headless django-allauth. Please do not mind the looks!</span>
        </div>
      </footer>

    </>
  )
}
