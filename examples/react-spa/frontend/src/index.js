import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { init } from './init'

init()

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  <App />
)
