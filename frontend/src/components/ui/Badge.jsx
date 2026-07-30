import React from 'react';

export default function Badge({ children, variant = 'info', showDot = false, className = '' }) {
  const variants = {
    success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
    error: "bg-rose-500/10 text-rose-400 border border-rose-500/20",
    info: "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20",
    neutral: "bg-slate-800 text-slate-300 border border-slate-700"
  };

  const dotColors = {
    success: "bg-emerald-400",
    warning: "bg-amber-400",
    error: "bg-rose-400",
    info: "bg-indigo-400",
    neutral: "bg-slate-400"
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {showDot && (
        <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dotColors[variant]}`} />
      )}
      {children}
    </span>
  );
}
