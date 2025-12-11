import React, { useState, useRef, useEffect } from 'react'

const SYSTEM_PROMPT = `You are a helpful assistant for immigrants and refugees. Provide clear, compassionate, and practical information about laws, rights, and insurance options. Always include a safety/legal disclaimer: you are not a lawyer and users should consult a qualified attorney or accredited organization for legal advice. Prefer linking to public resources and support organizations.`

function mockResponse(userText) {
  const lower = userText.toLowerCase()
  if (lower.includes('asylum') || lower.includes('refugee')) {
    return `General asylum info: asylum processes vary by country and require documentation, deadlines, and interviews. Contact local legal aid or an accredited refugee assistance organization for an intake assessment.`
  }
  if (lower.includes('insurance') || lower.includes('health')) {
    return `Insurance basics: look into local public health programs, community health centers, or low-cost/charity clinics. If eligible, apply for government-supported insurance programs; otherwise consider community health plans.`
  }
  return `Thanks for your question. For complex legal or insurance matters please provide more details (country, visa/status) so I can point to relevant resources, or consult a qualified attorney.`
}

export default function Chat() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello — how can I help with laws or insurance today? Please avoid sharing personal identifiers.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    const text = input.trim()
    if (!text) return
    const userMsg = { sender: 'user', text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    // If a Vite env var VITE_OPENAI_API_KEY is set, try calling OpenAI's chat API from the client (NOT recommended for production)
    const key = import.meta.env.VITE_OPENAI_API_KEY
    if (key) {
      try {
        const resp = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${key}`
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [
              { role: 'system', content: SYSTEM_PROMPT },
              { role: 'user', content: text }
            ],
            max_tokens: 600
          })
        })
        const data = await resp.json()
        const ai = data?.choices?.[0]?.message?.content || 'Sorry, no answer available.'
        setMessages(prev => [...prev, { sender: 'bot', text: ai }])
      } catch (err) {
        setMessages(prev => [...prev, { sender: 'bot', text: 'Error contacting AI service; using fallback guidance.' }])
        setMessages(prev => [...prev, { sender: 'bot', text: mockResponse(text) }])
      } finally {
        setLoading(false)
      }
    } else {
      // Mock helpful reply
      await new Promise(res => setTimeout(res, 800))
      setMessages(prev => [...prev, { sender: 'bot', text: mockResponse(text) }])
      setLoading(false)
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>
            <div className="text">{m.text}</div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-row">
        <textarea
          placeholder="Ask about immigration, asylum, insurance, or rights."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
        />
        <div className="actions">
          <button onClick={sendMessage} disabled={loading || !input.trim()} className="send">{loading ? 'Thinking...' : 'Send'}</button>
        </div>
      </div>

      <aside className="resources">
        <strong>Resources & Next Steps</strong>
        <ul>
          <li>Contact local legal aid or refugee organizations.</li>
          <li>Keep personal documents safe and copies of IDs.</li>
          <li>For urgent legal issues, consult an attorney.</li>
        </ul>
        <p className="disclaimer">This app provides general information and is not legal advice.</p>
      </aside>
    </div>
  )
}
