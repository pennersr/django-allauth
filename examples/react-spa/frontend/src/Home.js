function Service (props) {
  return (
    <div className='col'>
      <img className='img-fluid' src={props.img} />
      <h3>{props.title}</h3>
      <a href={props.link}>{props.linkBody}</a>
    </div>
  )
}

function Channel (props) {
  return (
    <div className='col'>
      <hr className={`aa-channel ${props.rev ? 'aa-channel-rev' : ''}`} />
      <div className='d-none d-lg-block' style={{ fontVariant: 'small-caps' }}>◀ {props.emoji} <span className=''>{props.title}</span> ▶</div>
    </div>
  )
}

export default function Home () {
  return (
    <div>
      <div className='container p-4 my-4 rounded-4 bg-light text-center'>
        <div className='d-flex flex-1 flex-column flex-sm-row align-items-sm-center'>

          <Service img='/img/app.svg' title='Mobile / SPA' link='https://app.react.demo.allauth.org' linkBody={<>app.<i>{'{project.org}'}</i></>} />
          <Channel emoji='🔑' title='tokens' />
          <Service img='/img/allauth.svg' title='Headless' link='https://api.react.demo.allauth.org/_allauth/openapi.html' linkBody={<>api.<i>{'{project.org}'}</i></>} />
          <Channel rev emoji='🍪' title='cookies' />
          <Service img='/img/react.svg' title='Single-Page application' link='https://react.demo.allauth.org' linkBody={<i>{'{project.org}'}</i>} />

        </div>
      </div>

      <h1>Welcome!</h1>

      <p>Welcome to the headless django-allauth demo. It demonstrates:</p>
      <ul>
        <li>A <strong>React</strong> <a target='_blank' href='https://codeberg.org/allauth/django-allauth/src/branch/main/examples/react-spa/frontend' rel='noreferrer'>frontend app</a> interfacing with <code>allauth.headless</code>.</li>
        <li>The use of <strong>session cookies</strong>, as well as <strong>API tokens</strong>.</li>
        <li>A <a href='/calculator'>calculator</a>, allowing <i>authenticated</i> users to add up two numbers, built using an API backed by two implementations: Django REST framework, and Ninja.
        </li>
        <li>The use of headless <strong>tokens</strong> in frameworks such as Django REST framework and Ninja.</li>
      </ul>
    </div>
  )
}
