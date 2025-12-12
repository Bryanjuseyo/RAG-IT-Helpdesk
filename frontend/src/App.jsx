import { useEffect, useState } from 'react'

export default function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(setData)
      .catch(err => setData({ error: String(err) }))
  }, [])

  return (
    <div style={{ padding: 16, fontFamily: 'system-ui' }}>
      <h1>Frontend ↔ Backend Check</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
