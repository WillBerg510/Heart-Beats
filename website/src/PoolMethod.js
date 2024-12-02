const PoolMethod = ({text, method, poolMethod, setPoolMethod}) => {
  return (
    <button
      onClick={() => setPoolMethod(method)}
    >
      {text}
    </button>
  )
}

export default PoolMethod