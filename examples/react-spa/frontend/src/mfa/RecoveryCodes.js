import { useLoaderData } from 'react-router-dom'

import * as allauth from '../lib/allauth'

export async function loader ({ params }) {
  const resp = await allauth.getRecoveryCodes()
  return { recoveryCodes: resp }
}

export default function RecoveryCodes (props) {
  const { recoveryCodes } = useLoaderData()
  return (
    <section>
      <h1>Recovery Codes</h1>

      {recoveryCodes.status === 200
        ? <>
          <p>There are {recoveryCodes.data.unused_code_count} out of {recoveryCodes.data.total_code_count} recovery codes available.</p>
          <pre>{recoveryCodes.data.unused_codes.join('\n')}</pre>
          </>
        : <><p>No recovery codes set up.</p></>}
    </section>
  )
}
