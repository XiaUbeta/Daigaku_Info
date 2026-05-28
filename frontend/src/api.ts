import axios from 'axios';
import type { University, ProcessedInfo } from './types';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  getUniversities: async (): Promise<University[]> => {
    const response = await apiClient.get<University[]>('/universities/');
    return response.data;
  },

  getNews: async (universityId?: number | null): Promise<ProcessedInfo[]> => {
    const params: { university_id?: number } = {};
    if (universityId) {
      params.university_id = universityId;
    }
    const response = await apiClient.get<ProcessedInfo[]>('/news/', { params });
    return response.data;
  },
};
