import React from 'react';

const StatCard = ({ title, value, icon, subtitle, trend, isDemoData = false }) => {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
          {trend && (
            <p className={`mt-1 text-sm ${trend.positive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.value}
            </p>
          )}
        </div>
        {icon && <div className="flex-shrink-0 ml-4 text-3xl">{icon}</div>}
      </div>
      {isDemoData && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <span className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
            DEMO DATA
          </span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
