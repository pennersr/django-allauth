export default function Button (props) {
  return <button className='btn btn-primary' {...props}>{props.children}</button>
}
