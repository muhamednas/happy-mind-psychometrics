import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Building2, Plus, Edit2, Trash2, ShieldAlert, CheckCircle, 
  Palette, FileCode, Copy, ExternalLink, RefreshCw 
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Modal from '../../components/ui/Modal';
import Badge from '../../components/ui/Badge';
import { api } from '../../api/client';

interface Corporate {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color?: string;
  quota: number;
  used_quota: number;
  created_at: string;
  updated_at: string;
}

export default function CorporatesManager() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [selectedCorporate, setSelectedCorporate] = useState<Corporate | null>(null);
  
  // Exporter config display
  const [configJson, setConfigJson] = useState<string>('');
  
  // Form State
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#6366f1');
  const [quota, setQuota] = useState<number>(0);

  // Fetch corporates
  const { data: corporates = [], isLoading } = useQuery<Corporate[]>({
    queryKey: ['corporates'],
    queryFn: api.admin.getCorporates
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: api.admin.createCorporate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['corporates'] });
      handleCloseModal();
    },
    onError: (err: any) => {
      alert('Error creating corporate client: ' + err.message);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.admin.updateCorporate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['corporates'] });
      handleCloseModal();
    },
    onError: (err: any) => {
      alert('Error updating corporate client: ' + err.message);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: api.admin.deleteCorporate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['corporates'] });
    },
    onError: (err: any) => {
      alert('Error deleting corporate client: ' + err.message);
    }
  });

  const handleOpenCreateModal = () => {
    setSelectedCorporate(null);
    setName('');
    setSlug('');
    setLogoUrl('');
    setPrimaryColor('#6366f1');
    setQuota(0);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (corp: Corporate) => {
    setSelectedCorporate(corp);
    setName(corp.name);
    setSlug(corp.slug);
    setLogoUrl(corp.logo_url || '');
    setPrimaryColor(corp.primary_color || '#6366f1');
    setQuota(corp.quota);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedCorporate(null);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const payload = {
      name,
      slug: slug.trim() || undefined,
      logo_url: logoUrl.trim() || undefined,
      primary_color: primaryColor,
      quota: Number(quota)
    };

    if (selectedCorporate) {
      updateMutation.mutate({ id: selectedCorporate.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this corporate client? This action cannot be undone.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleExportConfig = async (corp: Corporate) => {
    try {
      const config = await api.admin.getCorporateConfig(corp.id);
      setConfigJson(JSON.stringify(config, null, 2));
      setSelectedCorporate(corp);
      setIsConfigModalOpen(true);
    } catch (err: any) {
      alert('Failed to generate configuration: ' + err.message);
    }
  };

  const handleCopyConfig = () => {
    navigator.clipboard.writeText(configJson);
    alert('Client configuration JSON copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-50">Corporate Clients</h2>
          <p className="text-sm text-slate-400 mt-1">
            Manage corporate subscriptions, quotas, and custom client branding.
          </p>
        </div>
        <Button onClick={handleOpenCreateModal} className="shrink-0">
          <Plus className="w-4 h-4 mr-2" />
          Onboard Corporate
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">Loading corporate clients...</div>
      ) : corporates.length === 0 ? (
        <Card className="flex flex-col items-center justify-center text-center p-12 bg-slate-900 border-slate-800">
          <Building2 className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-200">No corporate clients onboarded yet</h3>
          <p className="text-slate-400 max-w-sm mt-2">
            Click "Onboard Corporate" to register your first corporate client, configure custom branding, and assign assessment limits.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {corporates.map((corp) => {
            const usagePercentage = corp.quota > 0 ? Math.min(100, Math.round((corp.used_quota / corp.quota) * 100)) : 0;
            const quotaStatus = corp.quota === 0 ? 'Unlimited' : `${corp.used_quota} / ${corp.quota}`;
            
            return (
              <Card key={corp.id} className="relative flex flex-col justify-between border-slate-800 bg-slate-900 hover:border-slate-700 transition-all">
                <div>
                  <div className="flex items-start justify-between mb-4">
                    {/* Logo and Name */}
                    <div className="flex items-center gap-3">
                      {corp.logo_url ? (
                        <img 
                          src={corp.logo_url} 
                          alt={`${corp.name} logo`} 
                          className="w-10 h-10 object-contain rounded bg-slate-850 p-1 border border-slate-700" 
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-10 h-10 rounded bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                          {corp.name.slice(0, 2).toUpperCase()}
                        </div>
                      )}
                      <div>
                        <h3 className="text-base font-semibold text-slate-100 line-clamp-1">{corp.name}</h3>
                        <p className="text-xs font-mono text-indigo-400">/{corp.slug}</p>
                      </div>
                    </div>

                    {/* Branding Color Pill */}
                    <div className="flex items-center gap-1.5 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700">
                      <span 
                        className="w-3.5 h-3.5 rounded-full border border-white/10" 
                        style={{ backgroundColor: corp.primary_color || '#6366f1' }}
                      />
                      <span className="text-[10px] font-mono text-slate-300">{corp.primary_color || '#6366f1'}</span>
                    </div>
                  </div>

                  {/* Quota Progress */}
                  <div className="space-y-2 mt-6">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-400 font-medium">Assessment Quota</span>
                      <span className="font-semibold text-slate-200">{quotaStatus}</span>
                    </div>
                    {corp.quota > 0 && (
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden border border-slate-700">
                        <div 
                          className="h-full rounded-full transition-all duration-300"
                          style={{ 
                            width: `${usagePercentage}%`,
                            backgroundColor: corp.primary_color || '#6366f1'
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between gap-3 mt-6 pt-4 border-t border-slate-800">
                  <button 
                    onClick={() => handleExportConfig(corp)}
                    className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
                    title="Export Configuration"
                  >
                    <FileCode className="w-4 h-4" />
                    Export
                  </button>

                  <div className="flex items-center gap-1.5">
                    <button 
                      onClick={() => handleOpenEditModal(corp)}
                      className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-md transition-colors"
                      title="Edit corporate settings"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => handleDelete(corp.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-md transition-colors"
                      title="Delete corporate client"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Onboard / Edit Corporate Modal */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={handleCloseModal}
        title={selectedCorporate ? 'Edit Corporate Client' : 'Onboard Corporate Client'}
        actions={
          <div className="flex justify-end gap-3 w-full">
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button 
              variant="primary" 
              onClick={handleSave}
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              {selectedCorporate ? 'Save Changes' : 'Onboard Client'}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} className="space-y-4">
          <Input 
            label="Corporate Name" 
            placeholder="e.g. Acme Corporation" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input 
            label="Custom URL Slug (Optional)" 
            placeholder="e.g. acme (leaves blank to auto-generate)" 
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
          />
          <Input 
            label="Branding Logo URL (Optional)" 
            placeholder="e.g. https://example.com/logo.png" 
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
          />
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Branding Primary Color</label>
              <div className="flex gap-2">
                <input 
                  type="color" 
                  className="w-10 h-10 rounded border border-slate-700 bg-slate-850 cursor-pointer"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                />
                <input 
                  type="text" 
                  className="flex-1 min-w-0 rounded-lg bg-slate-900 border border-slate-700 text-slate-50 text-sm focus:ring-2 focus:ring-indigo-500/50 p-2.5 font-mono"
                  placeholder="#6366f1"
                  value={primaryColor}
                  onChange={(e) => setPrimaryColor(e.target.value)}
                />
              </div>
            </div>
            <div>
              <Input 
                type="number"
                label="Assessment Quota" 
                placeholder="e.g. 100 (0 for unlimited)" 
                value={quota}
                onChange={(e) => setQuota(Math.max(0, parseInt(e.target.value) || 0))}
              />
            </div>
          </div>
        </form>
      </Modal>

      {/* Config Exporter Modal */}
      <Modal 
        isOpen={isConfigModalOpen} 
        onClose={() => setIsConfigModalOpen(false)}
        title="Client Config & White-label Link"
        actions={
          <div className="flex justify-end gap-3 w-full">
            <Button variant="secondary" onClick={() => setIsConfigModalOpen(false)}>Close</Button>
            <Button variant="primary" onClick={handleCopyConfig}>
              <Copy className="w-4 h-4 mr-2" />
              Copy Configuration
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-400">
            Generate and export white-labeled portal interfaces matching corporate visual designs.
          </p>

          <div>
            <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">White-labeled Portal Link</h4>
            <div className="flex items-center gap-2 bg-slate-950 p-3 rounded-lg border border-slate-850">
              <span className="text-xs font-mono text-indigo-400 break-all select-all">
                {window.location.origin}/portal?org={selectedCorporate?.slug}
              </span>
              <a 
                href={`/portal?org=${selectedCorporate?.slug}`} 
                target="_blank" 
                rel="noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors p-1"
                title="Open client portal"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">Integration Configuration JSON</h4>
            <pre className="p-4 rounded-lg bg-slate-950 border border-slate-850 text-xs font-mono text-emerald-400 overflow-x-auto h-48 scrollbar-thin">
              {configJson}
            </pre>
          </div>
        </div>
      </Modal>
    </div>
  );
}
