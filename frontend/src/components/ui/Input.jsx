import React, { forwardRef } from 'react';

const Input = forwardRef(({ label, error, icon: Icon, className = '', ...props }, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-slate-300 mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-slate-500" />
          </div>
        )}
        <input
          ref={ref}
          className={`
            block w-full rounded-lg bg-slate-900 border text-slate-50 text-sm
            focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all
            ${Icon ? 'pl-10' : 'pl-4'} pr-4 py-2.5
            ${error ? 'border-rose-500' : 'border-slate-700 hover:border-slate-600'}
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1.5 text-sm text-rose-400">{error}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
