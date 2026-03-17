"use client"

import { useEffect, useState } from "react"

export default function TestPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    console.log("🧪 Testing API...")
    fetch("http://localhost:8000/api/tickets/TKT-219A97A8")
      .then(r => r.json())
      .then(d => {
        console.log("✅ SUCCESS:", d)
        setData(d)
      })
      .catch(err => {
        console.error("❌ ERROR:", err)
        setError(err.message)
      })
  }, [])

  return (
    <div style={{ padding: "40px", color: "white", background: "#030712", minHeight: "100vh" }}>
      <h1>🧪 API Test Page</h1>
      
      {error && (
        <div style={{ background: "red", padding: "20px", borderRadius: "8px", marginBottom: "20px" }}>
          <h2>❌ Error:</h2>
          <pre>{error}</pre>
        </div>
      )}
      
      {data && (
        <div style={{ background: "green", padding: "20px", borderRadius: "8px" }}>
          <h2>✅ API Working!</h2>
          <pre style={{ fontSize: "12px", overflow: "auto" }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
      
      {!data && !error && (
        <p>Loading...</p>
      )}
      
      <div style={{ marginTop: "40px" }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Open browser console (F12)</li>
          <li>Check for logs</li>
          <li>If you see ✅ SUCCESS, API is working</li>
          <li>If you see ❌ ERROR, there's a connection issue</li>
        </ol>
      </div>
    </div>
  )
}
