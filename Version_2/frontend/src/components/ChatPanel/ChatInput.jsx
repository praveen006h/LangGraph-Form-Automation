import { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendMessage, addUserMessage } from '../../store/chatSlice'

function ChatInput() {
  const [text, setText] = useState('')
  const dispatch = useDispatch()
  const isLoading = useSelector(state => state.chat.isLoading)
  const textareaRef = useRef(null)

  const adjustHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }

  useEffect(() => {
    adjustHeight()
  }, [text])

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      const message = text.trim()
      setText('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
      dispatch(addUserMessage(message))
      dispatch(sendMessage(message))
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-input">
      <textarea
        ref={textareaRef}
        className="chat-input__field"
        placeholder="Type a message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        rows={1}
      />
      <button 
        className="chat-input__send" 
        onClick={handleSend}
        disabled={!text.trim() || isLoading}
        title="Send message"
      >
        ↑
      </button>
    </div>
  )
}

export default ChatInput
