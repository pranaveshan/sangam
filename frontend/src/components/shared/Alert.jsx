import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';

const Alert = ({ type = 'info', title, message, className = '' }) => {
  const variants = {
    success: {
      container: 'bg-green-50 border-green-200',
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
      title: 'text-green-900',
      message: 'text-green-700',
    },
    error: {
      container: 'bg-red-50 border-red-200',
      icon: <XCircle className="w-5 h-5 text-red-600" />,
      title: 'text-red-900',
      message: 'text-red-700',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: <AlertCircle className="w-5 h-5 text-yellow-600" />,
      title: 'text-yellow-900',
      message: 'text-yellow-700',
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: <Info className="w-5 h-5 text-blue-600" />,
      title: 'text-blue-900',
      message: 'text-blue-700',
    },
  };

  const variant = variants[type];

  return (
    <div className={`border rounded-lg p-4 ${variant.container} ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">{variant.icon}</div>
        <div className="ml-3 flex-1">
          {title && <h3 className={`text-sm font-medium ${variant.title}`}>{title}</h3>}
          {message && <p className={`text-sm ${variant.message} ${title ? 'mt-1' : ''}`}>{message}</p>}
        </div>
      </div>
    </div>
  );
};

export default Alert;
