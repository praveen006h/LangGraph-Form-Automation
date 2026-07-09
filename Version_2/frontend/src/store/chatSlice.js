import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendChatMessage } from '../services/api';
import { setFormState } from './formSlice';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { getState, dispatch }) => {
    const state = getState();
    const response = await sendChatMessage({
      message,
      conversation_history: state.chat.messages
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .map(m => ({
          role: m.role,
          content: m.content,
        })),
      current_form_state: state.form,
    });
    
    // Update form state from backend response
    if (response.updated_form_state) {
      dispatch(setFormState(response.updated_form_state));
    }
    
    return response;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    isLoading: false,
    error: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push({
          role: 'assistant',
          content: action.payload.ai_message,
          timestamp: new Date().toISOString(),
          tool_calls: action.payload.tool_calls_made || [],
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message;
        state.messages.push({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true,
        });
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
