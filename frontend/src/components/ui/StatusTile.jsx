import React from 'react';
import Card from './Card';
import Badge from './Badge';
import { ArrowRight, CheckCircle, Clock, FileText } from 'lucide-react';

export default function StatusTile({ title, description, status, onClick }) {
  const isCompleted = status === 'completed';
  const isInProgress = status === 'in_progress';
  
  const getStatusIcon = () => {
    if (isCompleted) return <CheckCircle className="w-8 h-8 text-emerald-400" />;
    if (isInProgress) return <Clock className="w-8 h-8 text-amber-400" />;
    return <FileText className="w-8 h-8 text-slate-500" />;
  };

  const getStatusBadge = () => {
    if (isCompleted) return <Badge variant="success" showDot>Completed</Badge>;
    if (isInProgress) return <Badge variant="warning" showDot>In Progress</Badge>;
    return <Badge variant="neutral" showDot>Not Started</Badge>;
  };

  return (
    <Card 
      variant={isCompleted ? 'default' : 'interactive'} 
      className={`relative overflow-hidden ${isInProgress ? 'ring-1 ring-amber-500/30' : ''}`}
      onClick={!isCompleted ? onClick : undefined}
    >
      {isInProgress && (
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-500 to-amber-300 opacity-50" />
      )}
      <div className="flex items-start justify-between">
        <div className="p-3 bg-slate-800 rounded-xl">
          {getStatusIcon()}
        </div>
        {getStatusBadge()}
      </div>
      
      <div className="mt-5">
        <h3 className="text-lg font-semibold text-slate-50">{title}</h3>
        <p className="mt-2 text-sm text-slate-400 line-clamp-2">{description}</p>
      </div>

      {!isCompleted && (
        <div className="mt-6 flex items-center text-sm font-medium text-indigo-400 group-hover:text-indigo-300">
          {isInProgress ? 'Continue Test' : 'Start Test'}
          <ArrowRight className="w-4 h-4 ml-1 transform group-hover:translate-x-1 transition-transform" />
        </div>
      )}
    </Card>
  );
}
