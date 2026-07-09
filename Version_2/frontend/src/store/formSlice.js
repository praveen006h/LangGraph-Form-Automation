import { createSlice } from '@reduxjs/toolkit';

const initialFormState = {
  interaction_id: null,
  hcp_name: '',
  interaction_date: '',
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: null,
  outcomes: '',
  follow_up_actions: '',
};

const formSlice = createSlice({
  name: 'form',
  initialState: initialFormState,
  reducers: {
    setFormState: (state, action) => {
      return { ...state, ...action.payload };
    },
    updateFormFields: (state, action) => {
      const updates = action.payload;
      Object.keys(updates).forEach(key => {
        if (updates[key] !== null && updates[key] !== undefined) {
          state[key] = updates[key];
        }
      });
    },
    resetForm: () => initialFormState,
  },
});

export const { setFormState, updateFormFields, resetForm } = formSlice.actions;
export default formSlice.reducer;
