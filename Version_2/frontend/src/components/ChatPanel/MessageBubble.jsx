function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  const formatTime = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className={`message-bubble message-bubble--${isUser ? 'user' : 'ai'}`}>
      <div className="message-bubble__content">
        {message.content}
      </div>
      <div className="message-bubble__time">
        {formatTime(message.timestamp)}
      </div>
    </div>
  )
}

export default MessageBubble
