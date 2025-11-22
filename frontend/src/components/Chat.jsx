import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChat, sendAgentChat } from '../api.js';
import { Send, Bot, PlusCircle } from 'lucide-react';

export default function Chat({ disabled }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // send message; if `toAgent` is true, mark the message as sent to the special agent
  async function handleSend(toAgent = false) {
    const text = input.trim();
    if (!text) return;
    setInput('');
    const history = [...messages];
    setMessages([...history, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const data = toAgent? await sendAgentChat(text, history) : await sendChat(text, history);
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: ' + (e.message || 'failed') }]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() { setMessages([]); }

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m,i) => (
            <div key={i} className={`message ${m.role}`}> 
              <div className="bubble">
                <ReactMarkdown>{m.content}</ReactMarkdown>
                {m.sources?.length ? <div className="sources">Sources: {m.sources.join(', ')}</div> : null}
              </div>
            </div>
        ))}
        {loading && (
          <div className="message assistant loading">
            <div className="bubble">
              <span className="loading-dots">
                <span style={{marginLeft:8}}>...</span>
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="input-row">
        <input
          type="text"
          placeholder={loading ? 'Waiting for answer...' : 'Ask a question'}
          value={input}
          disabled={loading || disabled}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
        />
        <button className="icon-button" onClick={() => handleSend(false)} disabled={loading || disabled} title="Send (normal)">
          <Send size={16} aria-hidden />
          <span className="visually-hidden">Send</span>
        </button>
        <button className="icon-button agent" onClick={() => handleSend(true)} disabled={loading || disabled} title="Send to Agent">
          <Bot size={16} aria-hidden />
          <span className="visually-hidden">Send to Agent</span>
        </button>
        <button className="secondary" onClick={clearChat} disabled={loading} title="New Chat">
          <PlusCircle size={16} aria-hidden />
          <span className="visually-hidden">New Chat</span>
        </button>
      </div>
    </div>
  );
}
