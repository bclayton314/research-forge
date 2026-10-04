import { useEffect, useState } from 'react'

import { getHealth } from './api/api'

import './App.css'


function App() {
  const [apiStatus, setApiStatus] = useState('Checking...')

  useEffect(() => {
    async function checkApi() {
      try {
        const health = await getHealth()
        setApiStatus(health.status)
      } catch {
        setApiStatus('unavailable')
      }
    }

    checkApi()
  }, [])

  return (
    <main>
      <h1>ResearchForge</h1>

      <p>
        AI-powered research and document analysis.
      </p>

      <section>
        <h2>System Status</h2>

        <p>
          API: <strong>{apiStatus}</strong>
        </p>
      </section>
    </main>
  )
}

export default App