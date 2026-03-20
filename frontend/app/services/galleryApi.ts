import axios from 'axios';

const BASE_URL = import.meta.env.VITE_MEDIA_LIBRARY_URL || 'http://localhost:8010/api/media_library';
export const MEDIA_BASE = import.meta.env.VITE_MEDIA_BASE_URL || 'http://localhost:8010';

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
