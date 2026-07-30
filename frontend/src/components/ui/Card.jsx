import React from 'react';

export default function Card({ children, className = '', variant = 'default', padding = 'p-6', ...props }) {
  const variants = {
    default: "bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl",
    elevated: "bg-slate-800/80 backdrop-blur-xl border border-slate-700 shadow-2xl",
    interactive: "bg-slate-900/60 backdrop-blur-xl border border-slate-800 shadow-xl hover:border-indigo-500/50 hover:shadow-indigo-500/10 transition-all duration-300 cursor-pointer hover:-translate-y-1"
  };

  return (
    <div className={`rounded-2xl overflow-hidden ${variants[variant]} ${padding} ${className}`} {...props}>
      {children}
    </div>
  );
}
