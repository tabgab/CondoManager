import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { post, get, del } from '../lib/api';
import type { Report, ReportCreate, ReportFilters, ReportMessage, ReportMessageCreate } from '../types';

const REPORTS_KEY = 'reports';
const MY_REPORTS_KEY = 'my-reports';
const REPORT_DETAIL_KEY = 'report-detail';
const REPORT_MESSAGES_KEY = 'report-messages';

export function useReports(filters?: ReportFilters) {
  return useQuery({
    queryKey: [REPORTS_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.priority) params.append('priority', filters.priority);
      if (filters?.building_id) params.append('building_id', filters.building_id);
      if (filters?.apartment_id) params.append('apartment_id', filters.apartment_id);
      if (filters?.submitted_by_id) params.append('submitted_by_id', filters.submitted_by_id);
      
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
      const response = await get<Report[]>('/reports?submitted_by_id=me');
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

export function useReportDetail(id: string | null) {
  return useQuery({
    queryKey: [REPORT_DETAIL_KEY, id],
    queryFn: async () => {
      if (!id) return null;
      const response = await get<Report>(`/reports/${id}`);
      return response;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useReportMessages(reportId: string | null) {
  return useQuery({
    queryKey: [REPORT_MESSAGES_KEY, reportId],
    queryFn: async () => {
      if (!reportId) return [];
      const response = await get<ReportMessage[]>(`/reports/${reportId}/messages`);
      return response;
    },
    enabled: !!reportId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (reportId: string) => {
      await del(`/reports/${reportId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [REPORTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [MY_REPORTS_KEY] });
      queryClient.invalidateQueries({ queryKey: [REPORT_DETAIL_KEY] });
    },
  });
}

export function useAddMessage() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ reportId, content }: { reportId: string; content: string }) => {
      const data: ReportMessageCreate = { content };
      const response = await post<ReportMessage>(`/reports/${reportId}/messages`, data);
      return response;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [REPORT_MESSAGES_KEY, variables.reportId] });
      queryClient.invalidateQueries({ queryKey: [REPORT_DETAIL_KEY, variables.reportId] });
    },
  });
}
