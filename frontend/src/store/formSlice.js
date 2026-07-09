import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hcpName: '',
  date: '',
  sentiment: null,
  topics: '',
  materials: [],
  samples: [],
  outcomes: '',
  followUp: ''
};

export const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    updateForm: (state, action) => {
      // Merges the new data from LangGraph into the form state
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState
  }
});

export const { updateForm, resetForm } = formSlice.actions;
export default formSlice.reducer;
