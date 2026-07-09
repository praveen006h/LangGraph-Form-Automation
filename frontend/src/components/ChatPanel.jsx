import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { sendMessage } from '../store/chatSlice';

const ChatPanel = () => {
  const [input, setInput] = useState('');
  const { messages, status } = useSelector((state) => state.chat);
  const dispatch = useDispatch();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() && status !== 'loading') {
      dispatch(sendMessage(input));
      setInput('');
    }
  };

  return (
    <div className="panel chat-panel">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem' }}>
        <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>🤖</span>
        <h2 style={{ color: 'var(--primary-color)' }}>AI Assistant</h2>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.role === 'assistant' ? <strong>AI: </strong> : <strong>You: </strong>}
            {msg.content}
          </div>
        ))}
        {status === 'loading' && (
          <div className="message assistant" style={{ fontStyle: 'italic', color: '#6b7280' }}>
            Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="chat-input-area">
        <input 
          type="text" 
          className="chat-input" 
          placeholder="Describe interaction or ask to edit..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={status === 'loading'}
        />
        <button type="submit" className="btn-primary" disabled={status === 'loading' || !input.trim()}>
          Log
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
