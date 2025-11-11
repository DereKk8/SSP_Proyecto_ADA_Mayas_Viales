import axios, { AxiosError } from 'axios';
import type { NetworkResponse, PointsResponse, TSPResult } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large computations
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Network loading endpoint
  async loadNetwork(file: File): Promise<NetworkResponse> {
    const formData = new FormData();
    formData.append('osm_file', file);
    
    try {
      const response = await apiClient.post<NetworkResponse>(
        '/api/network/load',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.detail || 'Failed to load network');
      }
      throw error;
    }
  },

  // Points snapping endpoint
  async snapPoints(file: File): Promise<PointsResponse> {
    const formData = new FormData();
    formData.append('points_file', file);
    
    try {
      const response = await apiClient.post<PointsResponse>(
        '/api/points/snap',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.detail || 'Failed to snap points');
      }
      throw error;
    }
  },

  // TSP algorithms
  async solveTSPBruteForce(pointIds: number[], graphData: any): Promise<TSPResult> {
    try {
      const response = await apiClient.post<TSPResult>('/api/tsp/bruteforce', {
        point_ids: pointIds,
        graph_data: graphData,
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.detail || 'Brute-force TSP failed');
      }
      throw error;
    }
  },

  async solveTSPHeldKarp(pointIds: number[], graphData: any): Promise<TSPResult> {
    try {
      const response = await apiClient.post<TSPResult>('/api/tsp/heldkarp', {
        point_ids: pointIds,
        graph_data: graphData,
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.detail || 'Held-Karp TSP failed');
      }
      throw error;
    }
  },

  async solveTSPHeuristic(pointIds: number[], graphData: any): Promise<TSPResult> {
    try {
      const response = await apiClient.post<TSPResult>('/api/tsp/heuristic', {
        point_ids: pointIds,
        graph_data: graphData,
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.detail || 'Heuristic TSP failed');
      }
      throw error;
    }
  },

  // Export endpoints
  async exportGeoJSON(data: any): Promise<Blob> {
    try {
      const response = await apiClient.post('/api/export/geojson', data, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error('Failed to export GeoJSON');
      }
      throw error;
    }
  },

  async exportWKT(data: any): Promise<Blob> {
    try {
      const response = await apiClient.post('/api/export/wkt', data, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error('Failed to export WKT');
      }
      throw error;
    }
  },
};

