import React from 'react';
import { Play, RotateCcw, Pause, Sparkles, TrendingUp } from 'lucide-react';
import { DatasetKey, Point } from '../types';
import { PointsTable } from './PointsTable';

interface ControlSidebarProps {
  datasetKey: DatasetKey;
  onDatasetChange: (key: DatasetKey) => void;
  degree: number;
  onDegreeChange: (deg: number) => void;
  showLagrange: boolean;
  onToggleLagrange: (val: boolean) => void;
  showMNK: boolean;
  onToggleMNK: (val: boolean) => void;
  showResiduals: boolean;
  onToggleResiduals: (val: boolean) => void;
  autoScale: boolean;
  onToggleAutoScale: (val: boolean) => void;
  onStartLagrangeAnim: () => void;
  onStartMNKAnim: () => void;
  onPauseAnim: () => void;
  onResetAnim: () => void;
  isAnimating: boolean;
  points: Point[];
  predictMNK: (x: number) => number;
}

export const ControlSidebar: React.FC<ControlSidebarProps> = ({
  datasetKey,
  onDatasetChange,
  degree,
  onDegreeChange,
  showLagrange,
  onToggleLagrange,
  showMNK,
  onToggleMNK,
  showResiduals,
  onToggleResiduals,
  autoScale,
  onToggleAutoScale,
  onStartLagrangeAnim,
  onStartMNKAnim,
  onPauseAnim,
  onResetAnim,
  isAnimating,
  points,
  predictMNK,
}) => {
  return (
    <aside className="w-full lg:w-80 flex flex-col gap-5">
      {/* 1. Вибір набору даних */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-800">Вибір датасету</span>
          <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md border border-slate-200">
            {points.length} точок
          </span>
        </div>
        <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200">
          {(['5', '10', '20'] as DatasetKey[]).map((key) => (
            <button
              key={key}
              onClick={() => onDatasetChange(key)}
              className={`py-1.5 text-xs font-medium rounded-lg transition-all ${
                datasetKey === key
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              {key} точок
            </button>
          ))}
        </div>
      </div>

      {/* 2. Параметри апроксимації та шари */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-800 mb-2">
            Ступінь полінома МНК (m)
          </label>
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200">
            {[1, 2, 3].map((deg) => (
              <button
                key={deg}
                onClick={() => onDegreeChange(deg)}
                className={`py-1.5 text-xs font-medium rounded-lg transition-all ${
                  degree === deg
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                m = {deg}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-2 border-t border-slate-200 space-y-3">
          {/* Toggles */}
          <label className="flex items-center justify-between cursor-pointer group">
            <span className="text-xs font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
              Поліном Лагранжа
            </span>
            <input
              type="checkbox"
              checked={showLagrange}
              onChange={(e) => onToggleLagrange(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-8 h-4.5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-3.5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all after:shadow-sm peer-checked:bg-sky-600 relative"></div>
          </label>

          <label className="flex items-center justify-between cursor-pointer group">
            <span className="text-xs font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
              Апроксимація МНК
            </span>
            <input
              type="checkbox"
              checked={showMNK}
              onChange={(e) => onToggleMNK(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-8 h-4.5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-3.5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all after:shadow-sm peer-checked:bg-emerald-600 relative"></div>
          </label>

          <label className="flex items-center justify-between cursor-pointer group">
            <span className="text-xs font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
              Відрізки залишків (r)
            </span>
            <input
              type="checkbox"
              checked={showResiduals}
              onChange={(e) => onToggleResiduals(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-8 h-4.5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-3.5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all after:shadow-sm peer-checked:bg-rose-500 relative"></div>
          </label>

          <label className="flex items-center justify-between cursor-pointer group">
            <span className="text-xs font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
              Автомасштабування осей
            </span>
            <input
              type="checkbox"
              checked={autoScale}
              onChange={(e) => onToggleAutoScale(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-8 h-4.5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-3.5 peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all after:shadow-sm peer-checked:bg-slate-700 relative"></div>
          </label>
        </div>
      </div>

      {/* 3. Анімація */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="text-xs font-semibold text-slate-800 mb-2.5">
          Анімації побудови
        </div>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={onStartLagrangeAnim}
            disabled={isAnimating}
            className="flex items-center justify-center gap-1.5 px-3 py-2 bg-sky-50 hover:bg-sky-100 text-sky-700 rounded-xl border border-sky-200 text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-600" />
            <span>Лагранж</span>
          </button>

          <button
            onClick={onStartMNKAnim}
            disabled={isAnimating}
            className="flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-xl border border-emerald-200 text-xs font-semibold transition-colors disabled:opacity-50"
          >
            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
            <span>МНК</span>
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 mt-2">
          <button
            onClick={onPauseAnim}
            className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 text-xs font-medium transition-colors"
          >
            <Pause className="w-3 h-3 text-slate-500" />
            <span>Пауза</span>
          </button>

          <button
            onClick={onResetAnim}
            className="flex items-center justify-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 text-xs font-medium transition-colors"
          >
            <RotateCcw className="w-3 h-3 text-slate-500" />
            <span>Скинути</span>
          </button>
        </div>
      </div>

      {/* 4. Таблиця точок */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="text-xs font-semibold text-slate-800 mb-3">
          Вхідні координати
        </div>
        <PointsTable points={points} predictMNK={predictMNK} />
      </div>
    </aside>
  );
};
