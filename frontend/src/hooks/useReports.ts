import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { post, get } from '../lib/api';
import type { Report, ReportCreate, ReportFilters } from '../types';

const REPORTS_KEY = 'reports';
const MY_REPORTS_KEY = 'my-reports';

export function useReports(filters?: ReportFilters) {
  return useQuery({
    queryKey: [REPORTS_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.priority) params.append('priority', filters.priority);
      if (filters?.building_id) params.append('building_id', filters.building_id);
      if (filters?.apartment_id) params.append('apartment_id', filters.apartment_id);
      if (filters?.reporter_id) params.append('reporter_id', filters.reporter_id);
      
      const queryString = params.toString() ? `?${params.toString()}` : '';
      const response = await get<Report[]>(`/reports${queryString}`);
      return response;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useMyReports() {
  return useQuery({
    queryKey: [MY_REPORTS_KEY],
    queryFn: async () => {
      const response = await get<Report[]>('/reports?reporter_id=me');
      return response;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ReportCreate) => {
      const response = await post<Report>('/reports', data);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REPORTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [MY_REPORTS_KEY] });
    },
  });
}
