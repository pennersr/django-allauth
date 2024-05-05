import { AuthContextProvider } from './auth'
import Router from './Router'

function App () {
  return (
    <AuthContextProvider>
      <Router />
    </AuthContextProvider>
  )
}

export default App
