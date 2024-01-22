export default function FormErrors (props) {
  if (!props.errors || !props.errors.length) {
    return null
  }
  return <ul style={{ color: 'darkred' }}>{props.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
}
