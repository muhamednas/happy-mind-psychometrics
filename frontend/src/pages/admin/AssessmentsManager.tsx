import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Brain, Plus, Trash2, Edit, Save, PlusCircle, CheckCircle, 
  HelpCircle, Clock, LayoutGrid, FileText, ArrowRight, ShieldAlert, Sparkles
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Modal from '../../components/ui/Modal';
import Badge from '../../components/ui/Badge';
import { api } from '../../api/client';

interface Question {
  id: string;
  text: string;
  type: string; // mcq, text, scale
  options: string[];
  correct_answer?: string;
}

interface Assessment {
  id: string;
  title: string;
  description?: string;
  type: string; // cognitive, personality, operational, technical
  time_limit_minutes: number;
  questions: Question[];
  created_at: string;
  updated_at: string;
}

export default function AssessmentsManager() {
  const queryClient = useQueryClient();
  
  // Navigation & filtering tabs
  const [activeTab, setActiveTab] = useState<string>('all');
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null);
  
  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('cognitive');
  const [timeLimit, setTimeLimit] = useState<number>(30);
  const [questions, setQuestions] = useState<Question[]>([]);

  // Fetch assessments
  const { data: assessments = [], isLoading } = useQuery<Assessment[]>({
    queryKey: ['assessments'],
    queryFn: api.admin.getAssessments
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: api.admin.createAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
      handleCloseModal();
    },
    onError: (err: any) => {
      alert('Error creating assessment: ' + err.message);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.admin.updateAssessment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
      handleCloseModal();
    },
    onError: (err: any) => {
      alert('Error updating assessment: ' + err.message);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: api.admin.deleteAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
    },
    onError: (err: any) => {
      alert('Error deleting assessment: ' + err.message);
    }
  });

  const handleOpenCreateModal = () => {
    setSelectedAssessment(null);
    setTitle('');
    setDescription('');
    setType('cognitive');
    setTimeLimit(30);
    setQuestions([]);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (assessment: Assessment) => {
    setSelectedAssessment(assessment);
    setTitle(assessment.title);
    setDescription(assessment.description || '');
    setType(assessment.type);
    setTimeLimit(assessment.time_limit_minutes);
    setQuestions(assessment.questions || []);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedAssessment(null);
  };

  // Questions Builder Logic
  const addQuestion = () => {
    const newQ: Question = {
      id: `q-${Date.now()}`,
      text: '',
      type: 'mcq',
      options: [''],
      correct_answer: ''
    };
    setQuestions([...questions, newQ]);
  };

  const removeQuestion = (qIndex: number) => {
    setQuestions(questions.filter((_, idx) => idx !== qIndex));
  };

  const handleQuestionTextChange = (qIndex: number, text: string) => {
    const updated = [...questions];
    updated[qIndex].text = text;
    setQuestions(updated);
  };

  const handleQuestionTypeChange = (qIndex: number, qType: string) => {
    const updated = [...questions];
    updated[qIndex].type = qType;
    if (qType !== 'mcq') {
      updated[qIndex].options = [];
      updated[qIndex].correct_answer = '';
    } else if (updated[qIndex].options.length === 0) {
      updated[qIndex].options = [''];
    }
    setQuestions(updated);
  };

  const addOption = (qIndex: number) => {
    const updated = [...questions];
    updated[qIndex].options = [...updated[qIndex].options, ''];
    setQuestions(updated);
  };

  const removeOption = (qIndex: number, optIndex: number) => {
    const updated = [...questions];
    const options = updated[qIndex].options.filter((_, oIdx) => oIdx !== optIndex);
    updated[qIndex].options = options;
    
    // reset correct answer if it was deleted
    if (updated[qIndex].correct_answer === updated[qIndex].options[optIndex]) {
      updated[qIndex].correct_answer = '';
    }
    setQuestions(updated);
  };

  const handleOptionChange = (qIndex: number, optIndex: number, val: string) => {
    const updated = [...questions];
    updated[qIndex].options[optIndex] = val;
    setQuestions(updated);
  };

  const handleCorrectAnswerChange = (qIndex: number, val: string) => {
    const updated = [...questions];
    updated[qIndex].correct_answer = val;
    setQuestions(updated);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !type) return;

    // Validate questions payload structure
    const cleanedQuestions = questions.map((q, idx) => ({
      id: q.id || `q-${idx}-${Date.now()}`,
      text: q.text,
      type: q.type,
      options: q.type === 'mcq' ? q.options.filter(o => o.trim() !== '') : [],
      correct_answer: q.type === 'mcq' ? q.correct_answer : undefined
    }));

    const payload = {
      title,
      description: description.trim() || undefined,
      type,
      time_limit_minutes: Number(timeLimit),
      questions: cleanedQuestions
    };

    if (selectedAssessment) {
      updateMutation.mutate({ id: selectedAssessment.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this master assessment template?')) {
      deleteMutation.mutate(id);
    }
  };

  // Filtered list
  const filteredAssessments = assessments.filter(
    a => activeTab === 'all' || a.type === activeTab
  );

  const categories = [
    { key: 'all', label: 'All Modules', icon: LayoutGrid },
    { key: 'cognitive', label: 'Cognitive Aptitude', icon: Brain },
    { key: 'personality', label: 'Personality Assessment', icon: Sparkles },
    { key: 'operational', label: 'Operational Performance', icon: Clock },
    { key: 'technical', label: 'Technical Aptitude', icon: FileText },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-50">Master Assessment Library</h2>
          <p className="text-sm text-slate-400 mt-1">
            Build and refine standard assessment modules to package and bundle for corporate clients.
          </p>
        </div>
        <Button onClick={handleOpenCreateModal} className="shrink-0">
          <Plus className="w-4 h-4 mr-2" />
          Create Assessment Module
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-px">
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isActive = activeTab === cat.key;
          return (
            <button
              key={cat.key}
              onClick={() => setActiveTab(cat.key)}
              className={`
                flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-all
                ${isActive 
                  ? 'border-indigo-500 text-indigo-400 font-semibold bg-indigo-500/5' 
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              {cat.label}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">Loading master assessments...</div>
      ) : filteredAssessments.length === 0 ? (
        <Card className="flex flex-col items-center justify-center text-center p-12 bg-slate-900 border-slate-800">
          <Brain className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-200">No assessments found</h3>
          <p className="text-slate-400 max-w-sm mt-2">
            No templates registered under this category. Create an assessment module to add it to the library.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssessments.map((assessment) => {
            const typeBadgeColors = {
              cognitive: 'info',
              personality: 'success',
              operational: 'warning',
              technical: 'neutral'
            } as const;

            const categoryName = categories.find(c => c.key === assessment.type)?.label || assessment.type;
            const badgeVariant = typeBadgeColors[assessment.type as keyof typeof typeBadgeColors] || 'neutral';

            return (
              <Card key={assessment.id} className="relative flex flex-col justify-between border-slate-800 bg-slate-900 hover:border-slate-700 transition-all">
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <Badge variant={badgeVariant} className="capitalize">
                      {categoryName.split(' ')[0]}
                    </Badge>
                    <div className="flex items-center gap-1 text-slate-400 text-xs">
                      <Clock className="w-3.5 h-3.5 mr-1" />
                      {assessment.time_limit_minutes}m
                    </div>
                  </div>

                  <h3 className="text-base font-semibold text-slate-100 mb-1.5 line-clamp-1">{assessment.title}</h3>
                  <p className="text-xs text-slate-400 line-clamp-3 mb-6 leading-relaxed">
                    {assessment.description || 'No description provided.'}
                  </p>

                  <div className="flex items-center gap-2 bg-slate-950 px-3 py-2 rounded-lg border border-slate-850">
                    <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0" />
                    <span className="text-xs text-slate-300 font-medium">
                      {assessment.questions?.length || 0} Questions configured
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 mt-6 pt-4 border-t border-slate-800">
                  <button 
                    onClick={() => handleOpenEditModal(assessment)}
                    className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-md transition-colors"
                    title="Edit assessment questions"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDelete(assessment.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-md transition-colors"
                    title="Delete assessment"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Assessment Builder Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={selectedAssessment ? 'Edit Assessment Module' : 'Create Assessment Module'}
        actions={
          <div className="flex justify-end gap-3 w-full">
            <Button variant="secondary" onClick={handleCloseModal}>Cancel</Button>
            <Button 
              variant="primary" 
              onClick={handleSave}
              isLoading={createMutation.isPending || updateMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Module
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
          <Input 
            label="Module Title" 
            placeholder="e.g. Logical Reasoning (Standard)" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Module Type</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                className="w-full rounded-lg bg-slate-900 border border-slate-700 text-slate-50 text-sm focus:ring-2 focus:ring-indigo-500/50 p-2.5"
              >
                <option value="cognitive">Cognitive Aptitude</option>
                <option value="personality">Personality Assessment</option>
                <option value="operational">Operational Performance</option>
                <option value="technical">Technical Aptitude</option>
              </select>
            </div>
            <div>
              <Input 
                type="number"
                label="Time Limit (Minutes)" 
                placeholder="e.g. 30" 
                value={timeLimit}
                onChange={(e) => setTimeLimit(Math.max(1, parseInt(e.target.value) || 30))}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">Module Description</label>
            <textarea
              className="w-full rounded-lg bg-slate-900 border border-slate-700 text-slate-50 text-sm focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 p-2.5 h-20 resize-none"
              placeholder="Describe what skills/metrics this module evaluates..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* Questions Section */}
          <div className="border-t border-slate-800 pt-4 space-y-4">
            <div className="flex justify-between items-center">
              <h4 className="text-sm font-semibold text-slate-200">Assessment Questions</h4>
              <button
                type="button"
                onClick={addQuestion}
                className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-semibold"
              >
                <PlusCircle className="w-4 h-4" />
                Add Question
              </button>
            </div>

            {questions.length === 0 ? (
              <div className="text-center py-6 text-slate-500 border border-dashed border-slate-800 rounded-lg text-xs">
                No questions added. Click "Add Question" to start building your test content.
              </div>
            ) : (
              <div className="space-y-4">
                {questions.map((q, qIdx) => (
                  <div key={q.id || qIdx} className="bg-slate-950 p-4 rounded-lg border border-slate-850 space-y-3">
                    <div className="flex justify-between items-center gap-2">
                      <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Question #{qIdx + 1}</span>
                      <button
                        type="button"
                        onClick={() => removeQuestion(qIdx)}
                        className="text-rose-400 hover:text-rose-350 p-1 rounded hover:bg-slate-900 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <Input 
                      placeholder="Enter question prompt..."
                      value={q.text}
                      onChange={(e) => handleQuestionTextChange(qIdx, e.target.value)}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-[11px] font-medium text-slate-400 mb-1">Answer Input Type</label>
                        <select
                          value={q.type}
                          onChange={(e) => handleQuestionTypeChange(qIdx, e.target.value)}
                          className="w-full rounded-md bg-slate-900 border border-slate-850 text-slate-50 text-xs focus:ring-1 focus:ring-indigo-500 p-2"
                        >
                          <option value="mcq">Multiple Choice Question (MCQ)</option>
                          <option value="text">Open-text Answer</option>
                          <option value="scale">Rating Scale</option>
                        </select>
                      </div>

                      {q.type === 'mcq' && (
                        <div>
                          <label className="block text-[11px] font-medium text-slate-400 mb-1">Correct Option Answer</label>
                          <select
                            value={q.correct_answer || ''}
                            onChange={(e) => handleCorrectAnswerChange(qIdx, e.target.value)}
                            className="w-full rounded-md bg-slate-900 border border-slate-850 text-slate-50 text-xs focus:ring-1 focus:ring-indigo-500 p-2"
                          >
                            <option value="">Select correct option...</option>
                            {q.options.map((opt, oIdx) => (
                              <option key={oIdx} value={opt}>{opt || `Option ${oIdx + 1}`}</option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>

                    {/* MCQ Options list */}
                    {q.type === 'mcq' && (
                      <div className="space-y-2 pt-2">
                        <div className="flex justify-between items-center">
                          <label className="block text-[11px] font-medium text-slate-400">Options choices</label>
                          <button
                            type="button"
                            onClick={() => addOption(qIdx)}
                            className="text-[10px] text-indigo-400 hover:text-indigo-350 transition-colors font-medium"
                          >
                            + Add option choice
                          </button>
                        </div>
                        {q.options.map((opt, optIdx) => (
                          <div key={optIdx} className="flex gap-2 items-center">
                            <input 
                              type="text"
                              className="flex-1 min-w-0 rounded-md bg-slate-900 border border-slate-850 text-slate-50 text-xs focus:ring-1 focus:ring-indigo-500 p-2"
                              placeholder={`Option choice ${optIdx + 1}`}
                              value={opt}
                              onChange={(e) => handleOptionChange(qIdx, optIdx, e.target.value)}
                            />
                            {q.options.length > 1 && (
                              <button
                                type="button"
                                onClick={() => removeOption(qIdx, optIdx)}
                                className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </form>
      </Modal>
    </div>
  );
}
