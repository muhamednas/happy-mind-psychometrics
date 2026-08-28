import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, Users, CheckCircle, TrendingUp, Plus, Search, Copy, Eye, Edit } from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Input from '../../components/ui/Input';
import { adminApi } from '../../lib/adminApi';

export default function Dashboard() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [packages, setPackages] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [pkgs, cands] = await Promise.all([
          adminApi.getPackages(),
          adminApi.getCandidates(),
        ]);
        setPackages(pkgs || []);
        setCandidates(cands || []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const totalPackages = packages.length;
  const activeCandidates = candidates.filter(c => c.logged_in_at).length;
  
  // Calculate completed (let's assume candidates who logged in and have all completed)
  // For display, we show actual counts
  const stats = [
    { name: 'Total Packages', value: totalPackages, icon: Package, change: 'Total created' },
    { name: 'Active Candidates', value: activeCandidates, icon: Users, change: 'Candidates logged in' },
    { name: 'Total Registered', value: candidates.length, icon: CheckCircle, change: 'Registered candidates' },
    { name: 'Completion Rate', value: candidates.length > 0 ? `${Math.round((activeCandidates / candidates.length) * 100)}%` : '0%', icon: TrendingUp, change: 'Logins / Registrations' },
  ];

  const handleCopyCode = (code) => {
    navigator.clipboard.writeText(code);
    alert('Code copied: ' + code);
  };

  return (
    <div className="space-y-6">
      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.name} className="flex flex-col">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-slate-50">{stat.value}</p>
              </div>
              <div className="p-3 bg-indigo-500/10 rounded-xl">
                <stat.icon className="w-5 h-5 text-indigo-400" />
              </div>
            </div>
            <div className="mt-4 text-sm text-slate-400">
              <span className="text-emerald-400">{stat.change.split(' ')[0]}</span>
              {' ' + stat.change.split(' ').slice(1).join(' ')}
            </div>
          </Card>
        ))}
      </div>

      {/* Packages Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mt-8">
        <h2 className="text-lg font-semibold text-slate-50">Recent Packages</h2>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Input 
            icon={Search} 
            placeholder="Search packages..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full sm:w-64"
          />
          <Button onClick={() => navigate('/admin/packages/create')} className="shrink-0">
            <Plus className="w-4 h-4 mr-2" />
            Create Package
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {packages
          .filter(pkg => pkg.title.toLowerCase().includes(search.toLowerCase()) || pkg.access_code.toLowerCase().includes(search.toLowerCase()))
          .map((pkg) => {
            const status = pkg.is_active ? 'active' : 'archived';
            return (
              <Card key={pkg.id} variant="elevated" className="flex flex-col">
                <div className="flex justify-between items-start mb-4">
                  <Badge variant={status === 'active' ? 'success' : 'neutral'}>
                    {status === 'active' ? 'Active' : 'Archived'}
                  </Badge>
                  <div className="flex items-center gap-1">
                    <button className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-md transition-colors" title="View">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-md transition-colors" title="Edit">
                      <Edit className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-slate-50 mb-1">{pkg.title}</h3>
                <p className="text-sm text-slate-400 line-clamp-2 mb-4">{pkg.description}</p>
                
                <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-800">
                  <div className="flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-700">
                    <span className="text-sm font-mono text-indigo-300">{pkg.access_code}</span>
                    <button 
                      onClick={() => handleCopyCode(pkg.access_code)}
                      className="text-slate-400 hover:text-slate-50 transition-colors"
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="flex items-center text-sm text-slate-400">
                    <Users className="w-4 h-4 mr-1" />
                    {pkg.candidate_count ?? 0}
                  </div>
                </div>
              </Card>
            );
          })}
      </div>
      {packages.length === 0 && !isLoading && (
        <div className="text-center py-12 text-slate-500 italic">
          No assessment packages found. Click "Create Package" to make one!
        </div>
      )}
      {isLoading && (
        <div className="text-center py-12 text-slate-500">
          Loading assessment packages...
        </div>
      )}
    </div>
  );
}
