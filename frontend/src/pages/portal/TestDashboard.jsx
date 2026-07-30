import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusTile from '../../components/ui/StatusTile';
import { api } from '../../api/client';

export default function TestDashboard() {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await api.candidate.getDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (isLoading) {
    return <div className="text-center py-12 text-slate-400">Loading your assessments...</div>;
  }

  if (!dashboardData) {
    return <div className="text-center py-12 text-rose-400">Failed to load assessment data. Please check your connection.</div>;
  }

  const { candidate_name, tests } = dashboardData;
  const remainingTests = tests.filter(t => t.status !== 'completed').length;

  return (
    <div className="w-full py-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-slate-50 mb-2">Hello, {candidate_name}</h1>
        <p className="text-lg text-slate-400">
          You have <span className="text-indigo-400 font-medium">{remainingTests} test{remainingTests !== 1 ? 's' : ''}</span> remaining in your assessment package.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tests.map((test) => (
          <StatusTile
            key={test.id}
            title={test.title}
            description={test.description}
            status={test.status}
            onClick={() => navigate(`/portal/test/${test.id}`)}
          />
        ))}
      </div>

      <div className="mt-12 p-6 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl">
        <h3 className="text-indigo-300 font-semibold mb-2">Important Information</h3>
        <ul className="text-sm text-slate-300 space-y-2 list-disc list-inside">
          <li>Ensure you have a stable internet connection before starting a test.</li>
          <li>Find a quiet place where you won't be interrupted.</li>
          <li>Your progress is saved automatically. You can safely close the window and return later.</li>
        </ul>
      </div>
    </div>
  );
}
