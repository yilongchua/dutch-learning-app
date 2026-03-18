import axios from 'axios';

const BASE_URL = (import.meta.env.VITE_GRAPHICS_API_URL as string) || 'http://localhost:8000/api/graphics_generation';
export const COMFY_URL = (import.meta.env.VITE_COMFYUI_URL as string) || 'http://localhost:8188';

const api = axios.create({ baseURL: BASE_URL, timeout: 120000 });

export interface GraphicsItem {
  id: number;
  created_at: string;
  original_prompt: string;
  improved_prompt: string;
  media_type: string;
  media_url: string;
}

export const graphicsGenerationApi = {
  enhancePrompt: async (prompt: string): Promise<{ improved_prompt: string }> => {
    const res = await api.post('/enhance-prompt', { prompt });
    return res.data;
  },
  generateMedia: async (original_prompt: string, improved_prompt: string, media_type: string): Promise<GraphicsItem> => {
    const res = await api.post('/generate', { original_prompt, improved_prompt, media_type });
    return res.data;
  },
  getHistory: async (skip: number = 0, limit: number = 20): Promise<GraphicsItem[]> => {
    const res = await api.get('/history', { params: { skip, limit } });
    return res.data;
  },
  deleteItem: async (id: number): Promise<{ status: string }> => {
    const res = await api.delete(`/history/${id}`);
    return res.data;
  },
  checkStatus: async (prompt_id: string): Promise<any> => {
    const res = await api.get(`/status/${prompt_id}`);
    return res.data;
  }
};
