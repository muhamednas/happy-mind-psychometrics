import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, CheckCircle2, Cloud } from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { useAutosave } from '../../hooks/useAutosave';
import { api } from '../../api/client';

export default function TestRunner() {
  const { testId } = useParams();
  const navigate = useNavigate();
  
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadTest() {
      try {
        const data = await api.candidate.getTest(testId);
        setQuestions(data.questions || []);
      } catch (err) {
        console.error('Failed to load test questions:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadTest();
  }, [testId]);

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  // Autosave logic
  const saveAnswer = async (currentAnswers) => {
    if (!currentQuestion) return;
    const answer = currentAnswers[currentQuestion.id];
    if (answer === undefined || answer === '') return;
    
    await api.candidate.autosave({
      test_id: testId,
      question_id: currentQuestion.id,
      response: answer
    });
  };

  const { isSaving, lastSaved } = useAutosave(saveAnswer, answers, 2000);

  const handleAnswer = (val) => {
    setAnswers(prev => ({ ...prev, [currentQuestion.id]: val }));
  };

  const handleNext = () => {
    if (isLastQuestion) {
      setShowSubmitModal(true);
    } else {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    setCurrentQuestionIndex(prev => Math.max(0, prev - 1));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await api.candidate.submitTest(testId);
      setShowSubmitModal(false);
      navigate('/portal/dashboard');
    } catch (err) {
      console.error(err);
      alert('Failed to submit test: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderQuestionInput = () => {
    const value = answers[currentQuestion.id] || '';

    switch (currentQuestion.type) {
      case 'mcq':
        return (
          <div className="space-y-3 mt-8">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = value === option;
              return (
                <button
                  key={idx}
                  onClick={() => handleAnswer(option)}
                  className={`
                    w-full text-left p-4 rounded-xl border transition-all duration-200
                    ${isSelected 
                      ? 'bg-indigo-500/20 border-indigo-500 text-indigo-100 ring-1 ring-indigo-500' 
                      : 'bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-800 hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <div className={`
                      w-5 h-5 rounded-full border flex items-center justify-center shrink-0
                      ${isSelected ? 'border-indigo-400 bg-indigo-500' : 'border-slate-500'}
                    `}>
                      {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                    </div>
                    {option}
                  </div>
                </button>
              );
            })}
          </div>
        );
      
      case 'likert':
        return (
          <div className="mt-12">
            <div className="flex justify-between text-sm text-slate-400 mb-4 px-2">
              <span>Strongly Disagree</span>
              <span>Strongly Agree</span>
            </div>
            <div className="flex justify-between items-center gap-2">
              {[1, 2, 3, 4, 5].map((num) => {
                const isSelected = value === num;
                return (
                  <button
                    key={num}
                    onClick={() => handleAnswer(num)}
                    className={`
                      w-12 h-12 rounded-full text-lg font-medium transition-all duration-200
                      ${isSelected 
                        ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/40 scale-110' 
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }
                    `}
                  >
                    {num}
                  </button>
                );
              })}
            </div>
          </div>
        );

      case 'open':
        return (
          <div className="mt-8">
            <textarea
              className="w-full h-48 bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="Type your answer here..."
              value={value}
              onChange={(e) => handleAnswer(e.target.value)}
            />
          </div>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-slate-400 animate-pulse">Loading test questions...</div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <h2 className="text-xl font-bold text-slate-100 mb-2">No Questions Found</h2>
        <p className="text-slate-400 mb-6">This test section doesn't have any questions configured.</p>
        <Button onClick={() => navigate('/portal/dashboard')}>Back to Dashboard</Button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto py-8">
      {/* Top Bar */}
      <div className="flex items-center justify-between mb-8">
        <button 
          onClick={() => navigate('/portal/dashboard')}
          className="text-sm text-slate-400 hover:text-slate-200 flex items-center transition-colors"
        >
          <ChevronLeft className="w-4 h-4 mr-1" /> Back to Dashboard
        </button>
        
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Cloud className="w-4 h-4" />
          {isSaving ? (
            <span className="text-amber-400 animate-pulse">Saving...</span>
          ) : lastSaved ? (
            <span className="text-emerald-400">Saved</span>
          ) : (
            <span>Ready</span>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-slate-400 mb-2">
          <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
          <span>{Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}%</span>
        </div>
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 to-teal-400 transition-all duration-500 ease-out"
            style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <Card className="min-h-[400px] flex flex-col p-8 sm:p-10 animate-in slide-in-from-right-8 duration-300">
        <div className="flex-1">
          <h2 className="text-2xl font-medium text-slate-50 leading-relaxed">
            {currentQuestion.text}
          </h2>
          {renderQuestionInput()}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-12 pt-6 border-t border-slate-800">
          <Button 
            variant="ghost" 
            onClick={handlePrev} 
            disabled={currentQuestionIndex === 0}
          >
            <ChevronLeft className="w-5 h-5 mr-1" /> Previous
          </Button>
          
          <Button 
            onClick={handleNext}
            disabled={!answers[currentQuestion.id] && currentQuestion.type !== 'open'}
          >
            {isLastQuestion ? 'Submit Test' : 'Next Question'}
            {!isLastQuestion && <ChevronRight className="w-5 h-5 ml-1" />}
          </Button>
        </div>
      </Card>

      {/* Submit Modal */}
      <Modal
        isOpen={showSubmitModal}
        onClose={() => setShowSubmitModal(false)}
        title="Submit Test"
        actions={
          <>
            <Button variant="ghost" onClick={() => setShowSubmitModal(false)}>Review Answers</Button>
            <Button onClick={handleSubmit} isLoading={isSubmitting}>Confirm Submit</Button>
          </>
        }
      >
        <div className="flex flex-col items-center py-6 text-center">
          <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mb-4">
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          </div>
          <h3 className="text-lg font-medium text-slate-100 mb-2">Ready to submit?</h3>
          <p className="text-slate-400">
            You have answered all questions. Once submitted, you cannot change your answers.
          </p>
        </div>
      </Modal>
    </div>
  );
}
