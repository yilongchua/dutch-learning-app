import axios from 'axios';
import { resolveApiBaseUrl, resolveMediaBaseUrl } from './apiConfig';

const BASE_URL = resolveApiBaseUrl(
  import.meta.env.VITE_MEDIA_LIBRARY_URL as string | undefined,
  '/api/media_library'
);
export const MEDIA_BASE = resolveMediaBaseUrl(import.meta.env.VITE_MEDIA_BASE_URL as string | undefined);

const api = axios.create({ 
  baseURL: BASE_URL, 
  timeout: 30000,
  headers: { 'skip_zrok_interstitial': 'true' }
});

export interface GalleryResponse {
  images: string[];
}

export const galleryApi = {
  getGallery: async (): Promise<GalleryResponse> => {
    const res = await api.get('/');
    return res.data;
  },
};
