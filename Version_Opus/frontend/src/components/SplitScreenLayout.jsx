import InteractionForm from './InteractionForm/InteractionForm'
import ChatPanel from './ChatPanel/ChatPanel'
import './SplitScreenLayout.css'

function SplitScreenLayout() {
  return (
    <div className="split-screen">
      <div className="split-screen__left">
        <InteractionForm />
      </div>
      <div className="split-screen__divider" />
      <div className="split-screen__right">
        <ChatPanel />
      </div>
    </div>
  )
}

export default SplitScreenLayout
