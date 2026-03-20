import axios from 'axios';

const BASE_URL = (import.meta.env.VITE_DUTCH_API_URL as string) || 'http://localhost:8010/api/dutch';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300000, // 300s (5m) — LLM agents can be very slow
  headers: {
    'zrok-skip-browser-verify-warning': 'true',
  },
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message;
    console.error(`[DutchAPI] ${err.config?.method?.toUpperCase()} ${err.config?.url}: ${msg}`);
    return Promise.reject(err);
  }
);

export const getExercise = (category: string, theme: string) =>
  api.get(`/exercise/${category}`, { params: { theme } });

export const getHistory = (limit: number = 20) =>
  api.get('/history', { params: { limit } });

export const evaluateWriting = (data: any) =>
  api.post('/evaluate/writing', data);

export const improveWriting = (data: any) =>
  api.post('/evaluate/writing/improve', data);

export const evaluateSpeaking = (formData: FormData) =>
  api.post('/evaluate/speaking', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const generateTheme = (currentTheme: string) =>
  api.get('/generate-theme', { params: { current_theme: currentTheme } });

export const getTTS = (text: string) =>
  api.get('/tts', { params: { text }, responseType: 'blob' });

export default api;
