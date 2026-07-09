import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { updateForm } from './formSlice';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { getState, dispatch }) => {
    const { form } = getState();
    
    // In a real app, you'd use a unique session ID
    const sessionId = "session_123";
    
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        current_form_state: form
      })
    });
    
    const data = await response.json();
    
    // Update the form slice with the new mutated state from LangGraph
    if (data.updated_form_state) {
      dispatch(updateForm(data.updated_form_state));
    }
    
    return data;
  }
);

const initialState = {
  messages: [
    { role: 'assistant', content: 'Hello! I am your AI Assistant. Describe your interaction with the HCP, and I will log it for you.' }
  ],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.status = 'loading';
        // Optimistically add user message
        state.messages.push({ role: 'user', content: action.meta.arg });
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.messages.push({ role: 'assistant', content: action.payload.ai_reply });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
        state.messages.push({ role: 'assistant', content: 'Sorry, I encountered an error communicating with the server.' });
      });
  }
});

export const { addMessage } = chatSlice.actions;
export default chatSlice.reducer;
