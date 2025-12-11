import React from 'react'
import Chat from './components/Chat'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Dignit AI — Immigration & Insurance Help</h1>
        <p className="subtitle">A friendly assistant to help immigrants and refugees understand laws and insurance options. Not legal advice.</p>
      </header>
      <main>
        <Chat />
      </main>
    </div>
  )
}
