import axios from 'axios';
import type { NewsItem } from '~/components/thenews/NewsCard';

const BASE_URL = (import.meta.env.VITE_NEWS_API_URL as string) || 'http://localhost:8010/api/v1/';

export const MEDIA_BASE = (import.meta.env.VITE_NEWS_MEDIA_URL as string) || 'http://localhost:8010';

const api = axios.create({ baseURL: BASE_URL, timeout: 120000 });

export const newsApi = {
  getNewsItems: async (): Promise<NewsItem[]> => {
    const res = await api.get('news-items');
    return res.data;
  },
  getNewsItem: async (id: number): Promise<NewsItem> => {
    const res = await api.get(`news-items/${id}`);
    return res.data;
  },
  generateContent: async (): Promise<{ status: string; message: string }> => {
    const res = await api.post('generate');
    return res.data;
  },
};
