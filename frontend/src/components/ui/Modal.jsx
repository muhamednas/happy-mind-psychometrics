import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import Button from './Button';

export default function Modal({ isOpen, onClose, title, children, actions }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl transform transition-all animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <h3 className="text-xl font-semibold text-slate-50">{title}</h3>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-50 transition-colors p-1 rounded-md hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 text-slate-300">
          {children}
        </div>
        
        {actions && (
          <div className="flex justify-end gap-3 p-6 border-t border-slate-800 bg-slate-900/50 rounded-b-2xl">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
