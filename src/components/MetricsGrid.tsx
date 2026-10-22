import React from 'react';
import { Metrics } from '../types';

interface MetricsGridProps {
  metrics: Metrics;
}

export const MetricsGrid: React.FC<MetricsGridProps> = ({ metrics }) => {
  const items = [
    {
      label: 'Середньоквадратична похибка (MSE)',
      value: metrics.mse.toFixed(4),
      subtext: 'Похибка МНК на вузлах',
      indicator: 'text-slate-800',
    },
    {
      label: 'Коефіцієнт детермінації (R²)',
      value: metrics.r2.toFixed(4),
      subtext: 'Частка поясненої дисперсії',
      indicator: 'text-emerald-700 font-bold',
    },
    {
      label: 'Корінь похибки (RMSE)',
      value: metrics.rmse.toFixed(4),
      subtext: 'У масштабі цільової величини',
      indicator: 'text-slate-800',
    },
    {
      label: 'Максимальний залишок |r|',
      value: metrics.maxResidual.toFixed(4),
      subtext: 'Найбільше точкове відхилення',
      indicator: 'text-rose-600',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {items.map((item, idx) => (
        <div
          key={idx}
          className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm transition-colors"
        >
          <div className="text-[11px] font-semibold text-slate-500">
            {item.label}
          </div>
          <div className={`mt-2 text-2xl font-mono font-bold tracking-tight ${item.indicator}`}>
            {item.value}
          </div>
          <div className="mt-1 text-[11px] text-slate-400 font-normal">
            {item.subtext}
          </div>
        </div>
      ))}
    </div>
  );
};
