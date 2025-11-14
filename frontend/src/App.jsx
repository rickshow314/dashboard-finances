import { useEffect, useState } from 'react'

function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/ping')
      .then(res => res.json())
      .then(setData)
  }, [])

  return (
    <div>
      <h1>Finanzas Personales Dashboard</h1>
      <p>{data ? data.message : "Cargando..."}</p>
    </div>
  )
}

export default App
  
