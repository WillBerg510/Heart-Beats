const DataStructure = ({text, structure, setStructure}) => {
  return (
    <button
      onClick={() => setStructure(text)}
    >
      {text}
    </button>
  )
}

export default DataStructure