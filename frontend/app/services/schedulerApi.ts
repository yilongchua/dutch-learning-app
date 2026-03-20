import axios from 'axios';

const BASE_URL = import.meta.env.VITE_SCHEDULER_API_URL || 'http://localhost:8010/api/scheduler';

const api = axios.create({ 
  baseURL: BASE_URL, 
  timeout: 30000,
  headers: { 'skip_zrok_interstitial': 'true' }
});

export interface CronJob {
  id?: string;
  task_type: string;
  schedule_time: string;
  input_number: number;
}

export const schedulerApi = {
  getJobs: async (): Promise<CronJob[]> => {
    const res = await api.get('/');
    return res.data;
  },
  createJob: async (job: CronJob): Promise<CronJob> => {
    const res = await api.post('/', job);
    return res.data;
  },
  deleteJob: async (id: string): Promise<{ status: string }> => {
    const res = await api.delete(`/${id}`);
    return res.data;
  },
};
