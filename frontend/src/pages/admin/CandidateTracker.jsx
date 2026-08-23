import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Eye, MoreVertical } from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Badge from '../../components/ui/Badge';
import { adminApi, candidateStatus } from '../../lib/adminApi';

export default function CandidateTracker() {
  const [search, setSearch] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadCandidates() {
      try {
        const data = await adminApi.getCandidates();
        setCandidates(data || []);
      } catch (err) {
        console.error('Failed to fetch candidates:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCandidates();
  }, []);

  const handleDownloadReport = async (candidateId) => {
    try {
      await adminApi.downloadReport(candidateId);
    } catch (err) {
      console.error('Failed to download report:', err);
      alert('Failed to download report: ' + err.message);
    }
  };

  const getStatusBadge = (status) => {
    switch(status) {
      case 'completed': return <Badge variant="success" showDot>Completed</Badge>;
      case 'in_progress': return <Badge variant="warning" showDot>In Progress</Badge>;
      default: return <Badge variant="neutral" showDot>Not Started</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-50">Candidate Tracker</h1>
          <p className="text-slate-400 mt-1">Monitor candidate progress and results</p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Button variant="secondary">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="secondary">
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      <Card className="p-0">
        <div className="p-4 border-b border-slate-800 bg-slate-900/50">
          <Input 
            icon={Search} 
            placeholder="Search candidates by name or email..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-md"
          />
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/50 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4 font-medium">Candidate</th>
                <th className="px-6 py-4 font-medium">Package</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Progress</th>
                <th className="px-6 py-4 font-medium">Score</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {candidates
                .filter(c => c.full_name.toLowerCase().includes(search.toLowerCase()) || c.email.toLowerCase().includes(search.toLowerCase()))
                .map((candidate) => {
                  const status = candidateStatus(candidate);
                  const progress = `${candidate.completed_assessments}/${candidate.total_assessments}`;
                  const score = candidate.avg_score != null ? `${candidate.avg_score}%` : '-';
                  return (
                  <tr key={candidate.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-100">{candidate.full_name}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{candidate.email}</div>
                    </td>
                    <td className="px-6 py-4">{candidate.package_title}</td>
                    <td className="px-6 py-4">
                      {getStatusBadge(status)}
                    </td>
                    <td className="px-6 py-4 text-slate-400">{progress} Tests</td>
                    <td className="px-6 py-4 font-medium text-slate-100">{score}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        {status === 'completed' && (
                          <button 
                            onClick={() => handleDownloadReport(candidate.id)}
                            className="p-1.5 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-md transition-colors cursor-pointer" 
                            title="Download Report"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                        <button className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md transition-colors" title="View Details">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 text-slate-500 hover:text-slate-300 hover:bg-slate-800 rounded-md transition-colors">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
