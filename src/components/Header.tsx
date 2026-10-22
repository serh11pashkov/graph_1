import React from 'react';
import { Layers, Activity } from 'lucide-react';

interface HeaderProps {
  activeTab: 'interactive' | 'matrix';
  onTabChange: (tab: 'interactive' | 'matrix') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  return (
    <header className="bg-white/90 backdrop-blur-md rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-slate-200/80 shadow-sm">
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Апроксимація функцій: Лагранж та МНК
          </h1>
          <span className="text-xs font-mono font-semibold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
            Варіант 20
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1 font-normal">
          Лабораторна робота №1 • Числові методи інтерполяції та статистичного згладжування
        </p>
      </div>

      <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
        <button
          onClick={() => onTabChange('interactive')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 ${
            activeTab === 'interactive'
              ? 'bg-white text-slate-900 shadow-sm font-semibold'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          <Activity className="w-3.5 h-3.5 text-sky-600" />
          <span>Інтерактивний аналіз</span>
        </button>

        <button
          onClick={() => onTabChange('matrix')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 ${
            activeTab === 'matrix'
              ? 'bg-white text-slate-900 shadow-sm font-semibold'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          <Layers className="w-3.5 h-3.5 text-indigo-600" />
          <span>Матриця 6 графіків</span>
        </button>
      </div>
    </header>
  );
};
