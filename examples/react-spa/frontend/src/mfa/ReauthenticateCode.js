import { useState } from 'react'
import FormErrors from '../components/FormErrors'
import { mfaReauthenticate } from '../lib/allauth'
import ReauthenticateFlow from '../account/ReauthenticateFlow'
import Button from '../components/Button'

export default function ReauthenticateCode (props) {
  const [code, setCode] = useState('')
  const [response, setResponse] = useState({ fetching: false, content: null })

  function submit () {
    setResponse({ ...response, fetching: true })
    mfaReauthenticate(code).then((content) => {
      setResponse((r) => { return { ...r, content } })
    }).catch((e) => {
      console.error(e)
      window.alert(e)
    }).then(() => {
      setResponse((r) => { return { ...r, fetching: false } })
    })
  }
  return (
    <ReauthenticateFlow>
      {props.children}

      <FormErrors errors={response.content?.errors} />

      <div><label>Code: <input value={code} onChange={(e) => setCode(e.target.value)} type='text' required /></label>
        <FormErrors param='code' errors={response.content?.errors} />
      </div>
      <Button disabled={response.fetching} onClick={() => submit()}>Confirm</Button>
    </ReauthenticateFlow>
  )
}
