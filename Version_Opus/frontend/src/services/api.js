import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s timeout for AI responses
});

export const sendChatMessage = async (chatRequest) => {
  const response = await apiClient.post('/api/chat', chatRequest);
  return response.data;
};

export const getMaterials = async () => {
  const response = await apiClient.get('/api/materials');
  return response.data;
};

export const getSamples = async () => {
  const response = await apiClient.get('/api/samples');
  return response.data;
};

export const submitInteraction = async (formState) => {
  const response = await apiClient.post('/api/interactions/submit', formState);
  return response.data;
};
