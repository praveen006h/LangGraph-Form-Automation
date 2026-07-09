import { useEffect, useRef } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { clearChat } from '../../store/chatSlice'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import './ChatPanel.css'

function ChatPanel() {
  const { messages, isLoading } = useSelector(state => state.chat)
  const dispatch = useDispatch()
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="chat-panel">
      <div className="chat-panel__header">
        <div className="chat-panel__title-group">
          <span className="chat-panel__icon">✨</span>
          <h2 className="chat-panel__title">AI Assistant</h2>
        </div>
        <button 
          className="btn btn--ghost" 
          onClick={() => dispatch(clearChat())}
          title="Clear Conversation"
        >
          🗑️ Clear
        </button>
      </div>

      <div className="chat-panel__messages">
        {messages.length === 0 ? (
          <div className="chat-panel__empty-state">
            <span className="chat-panel__empty-icon">👋</span>
            <p className="chat-panel__empty-text">
              Hi! I'm your CRM assistant. You can tell me about your HCP interactions, and I'll log the details for you.
            </p>
            <div className="chat-panel__suggestions">
              <span className="chat-panel__suggestion">"I just met with Dr. Sarah Smith to discuss Product X..."</span>
              <span className="chat-panel__suggestion">"Can you show me Dr. John Williams' history?"</span>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble key={index} message={msg} />
          ))
        )}
        
        {isLoading && (
          <div className="chat-panel__loading">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-panel__input-container">
        <ChatInput />
      </div>
    </div>
  )
}

export default ChatPanel
