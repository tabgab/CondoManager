// @ts-nocheck
import { useState } from 'react';
import { useAuthStore } from '../store/auth';
import { Navbar } from '../components/Navbar';
import { ReportForm } from '../components/reports/ReportForm';
import { ReportDetailModal } from '../components/reports/ReportDetailModal';
import { useMyReports, useReportDetail, useReportMessages, useAddMessage, useDeleteReport } from '../hooks/useReports';
import { useBuildings } from '../hooks/useQueries';
import type { Report } from '../types';

export function OwnerDashboard() {
  const { user, logout } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'reports' | 'submit'>('reports');
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  
  const { data: reports = [], isLoading: reportsLoading, refetch } = useMyReports();
  const { data: buildings = [], isLoading: buildingsLoading } = useBuildings();
  const { data: reportDetail } = useReportDetail(selectedReportId);
  const { data: reportMessages = [] } = useReportMessages(selectedReportId);
  const { mutateAsync: addMessage } = useAddMessage();
  const { mutateAsync: deleteReport } = useDeleteReport();

  const pendingCount = reports.filter(r => r.status === 'pending').length;
  const resolvedCount = reports.filter(r => r.status === 'resolved' || r.status === 'rejected').length;

  // Mock apartments - would come from user profile in real implementation
  const mockApartments = user?.owned_apartments || user?.rented_apartments || [];

  const handleReportSuccess = () => {
    setActiveTab('reports');
    refetch();
  };

  const handleReportClick = (report: Report) => {
    setSelectedReport(report);
    setSelectedReportId(report.id);
  };

  const handleCloseModal = () => {
    setSelectedReportId(null);
    setSelectedReport(null);
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedReportId) return;
    await addMessage({ reportId: selectedReportId, content });
  };

  const handleDeleteReport = async (reportId: string) => {
    if (!confirm('Are you sure you want to delete this report?')) return;
    await deleteReport(reportId);
    handleCloseModal();
    refetch();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    acknowledged: 'bg-blue-100 text-blue-800',
    task_created: 'bg-purple-100 text-purple-800',
    rejected: 'bg-red-100 text-red-800',
    resolved: 'bg-green-100 text-green-800',
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} onLogout={logout} />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            Owner Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Welcome, {user?.first_name || user?.email}!
          </p>

          {/* Stats Cards */}
          <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Reports</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{reports.length}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{pendingCount}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Resolved</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{resolvedCount}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-8">
            <div className="sm:hidden">
              <label htmlFor="tabs" className="sr-only">Select a tab</label>
              <select
                id="tabs"
                name="tabs"
                className="block w-full focus:ring-blue-500 focus:border-blue-500 border-gray-300 rounded-md"
                value={activeTab}
                onChange={(e) => setActiveTab(e.target.value as 'reports' | 'submit')}
              >
                <option value="reports">My Reports</option>
                <option value="submit">Submit Report</option>
              </select>
            </div>
            <div className="hidden sm:block">
              <nav className="flex space-x-4" aria-label="Tabs">
                <button
                  onClick={() => setActiveTab('reports')}
                  className={`${
                    activeTab === 'reports'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  } px-3 py-2 font-medium text-sm rounded-md`}
                >
                  My Reports
                </button>
                <button
                  onClick={() => setActiveTab('submit')}
                  className={`${
                    activeTab === 'submit'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-500 hover:text-gray-700'
                  } px-3 py-2 font-medium text-sm rounded-md`}
                >
                  Submit Report
                </button>
              </nav>
            </div>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {activeTab === 'reports' && (
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
                  <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      My Reports
                    </h3>
                    <p className="mt-1 max-w-2xl text-sm text-gray-500">
                      Track the status of your reported issues.
                    </p>
                  </div>
                  <button
                    onClick={() => setActiveTab('submit')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    New Report
                  </button>
                </div>
                <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                  {reportsLoading ? (
                    <div className="py-8 text-center">
                      <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
                      <p className="mt-2 text-gray-500">Loading reports...</p>
                    </div>
                  ) : reports.length === 0 ? (
                    <div className="py-8 text-center text-gray-500">
                      <p>No reports submitted yet.</p>
                      <button
                        onClick={() => setActiveTab('submit')}
                        className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Submit a new report
                      </button>
                    </div>
                  ) : (
                    <ul className="divide-y divide-gray-200">
                      {reports.map((report) => (
                        <li 
                          key={report.id} 
                          className="px-4 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                          onClick={() => handleReportClick(report)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {report.title}
                              </p>
                              <p className="text-sm text-gray-500">
                                {report.building?.name || 'Building'} - Unit {report.apartment?.unit_number || 'N/A'}
                              </p>
                              <p className="text-xs text-gray-400 mt-1">
                                Submitted {formatDate(report.created_at)}
                              </p>
                            </div>
                            <div className="ml-4 flex items-center gap-2">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                statusColors[report.status]
                              }`}>
                                {report.status.replace('_', ' ')}
                              </span>
                              <button
                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleReportClick(report);
                                }}
                              >
                                View Details →
                              </button>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'submit' && (
              <div className="bg-white shadow sm:rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Submit New Report
                  </h3>
                  {buildingsLoading ? (
                    <div className="py-4 text-center">
                      <div className="inline-block animate-spin h-6 w-6 border-4 border-blue-600 border-t-transparent rounded-full" />
                      <p className="mt-2 text-gray-500">Loading buildings...</p>
                    </div>
                  ) : (
                    <ReportForm
                      buildings={buildings}
                      apartments={mockApartments}
                      onSuccess={handleReportSuccess}
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Report Detail Modal */}
      <ReportDetailModal
        report={reportDetail || selectedReport || undefined}
        messages={reportMessages}
        isOpen={!!selectedReportId}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default OwnerDashboard;
