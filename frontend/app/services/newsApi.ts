import axios from 'axios';
import type { NewsItem } from '~/components/thenews/NewsCard';
import { resolveApiBaseUrl, resolveMediaBaseUrl } from './apiConfig';

const BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_NEWS_API_URL as string | undefined, '/api/news');

export const MEDIA_BASE = resolveMediaBaseUrl(import.meta.env.VITE_MEDIA_BASE_URL as string | undefined);

const api = axios.create({ 
  baseURL: BASE_URL, 
  timeout: 300000,
  headers: { 'skip_zrok_interstitial': 'true' }
});

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
