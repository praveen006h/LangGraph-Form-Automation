import React from 'react';
import FormPanel from './components/FormPanel';
import ChatPanel from './components/ChatPanel';

function App() {
  return (
    <div className="split-layout">
      <FormPanel />
      <ChatPanel />
    </div>
  );
}

export default App;
