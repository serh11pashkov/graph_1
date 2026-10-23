import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Header } from './components/Header';
import { MetricsGrid } from './components/MetricsGrid';
import { ControlSidebar } from './components/ControlSidebar';
import { MainChart } from './components/MainChart';
import { Matrix6View } from './components/Matrix6View';
import { getDataset } from './data/datasets';
import { lagrangeInterpolate, fitPolynomialOLS } from './lib/math';
import { DatasetKey, AnimationState } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'interactive' | 'matrix'>('interactive');
  const [datasetKey, setDatasetKey] = useState<DatasetKey>('5');
  const [points, setPoints] = useState(() => getDataset('5'));
  const [degree, setDegree] = useState<number>(2);

  const [showLagrange, setShowLagrange] = useState<boolean>(true);
  const [showMNK, setShowMNK] = useState<boolean>(true);
  const [showResiduals, setShowResiduals] = useState<boolean>(true);
  const [autoScale, setAutoScale] = useState<boolean>(true);

  const [animState, setAnimState] = useState<AnimationState>({
    active: false,
    type: null,
    step: 0,
    progress: 0,
  });

  const animRef = useRef<number | null>(null);

  // Оновлення датасету
  const handleDatasetChange = (key: DatasetKey) => {
    setDatasetKey(key);
    setPoints(getDataset(key));
    handleResetAnim();
  };

  // Розрахунок МНК моделі
  const olsModel = useMemo(() => {
    return fitPolynomialOLS(points, degree);
  }, [points, degree]);

  // Функція Лагранжа
  const lagrangeFn = useMemo(() => {
    if (animState.active && animState.type === 'lagrange') {
      const subPoints = points.slice(0, Math.max(1, animState.step + 1));
      return (x: number) => lagrangeInterpolate(subPoints, x);
    }
    return (x: number) => lagrangeInterpolate(points, x);
  }, [points, animState.active, animState.type, animState.step]);

  // Функція МНК (з морфінгом під час анімації)
  const mnkFn = useMemo(() => {
    if (animState.active && animState.type === 'mnk') {
      const meanY = points.reduce((acc, p) => acc + p.y, 0) / points.length;
      return (x: number) => meanY * (1 - animState.progress) + olsModel.predict(x) * animState.progress;
    }
    return (x: number) => olsModel.predict(x);
  }, [points, olsModel, animState.active, animState.type, animState.progress]);

  // Анімація Лагранжа: покрокове додавання вузлів
  const handleStartLagrangeAnim = () => {
    handleResetAnim();
    setAnimState({
      active: true,
      type: 'lagrange',
      step: 0,
      progress: 0,
    });
  };

  useEffect(() => {
    if (!animState.active || animState.type !== 'lagrange') return;

    const timer = setInterval(() => {
      setAnimState((prev) => {
        if (prev.step + 1 >= points.length) {
          clearInterval(timer);
          return { ...prev, active: false };
        }
        return { ...prev, step: prev.step + 1 };
      });
    }, 1100);

    return () => clearInterval(timer);
  }, [animState.active, animState.type, points.length]);

  // Анімація МНК: плавний морфінг від середньої прямої
  const handleStartMNKAnim = () => {
    handleResetAnim();
    setAnimState({
      active: true,
      type: 'mnk',
      step: 0,
      progress: 0,
    });

    const startTime = performance.now();
    const duration = 1800; // 1.8 seconds

    const frame = (now: number) => {
      const elapsed = now - startTime;
      const t = Math.min(1, elapsed / duration);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - t, 3);

      setAnimState((prev) => ({
        ...prev,
        progress: eased,
      }));

      if (t < 1) {
        animRef.current = requestAnimationFrame(frame);
      } else {
        setAnimState((prev) => ({ ...prev, active: false, progress: 1 }));
      }
    };

    animRef.current = requestAnimationFrame(frame);
  };

  const handlePauseAnim = () => {
    if (animRef.current) cancelAnimationFrame(animRef.current);
    setAnimState((prev) => ({ ...prev, active: false }));
  };

  const handleResetAnim = () => {
    if (animRef.current) cancelAnimationFrame(animRef.current);
    setAnimState({
      active: false,
      type: null,
      step: points.length - 1,
      progress: 1,
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between">
      <main className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <Header activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === 'interactive' ? (
          <div className="flex flex-col lg:flex-row gap-6 items-start">
            <ControlSidebar
              datasetKey={datasetKey}
              onDatasetChange={handleDatasetChange}
              degree={degree}
              onDegreeChange={setDegree}
              showLagrange={showLagrange}
              onToggleLagrange={setShowLagrange}
              showMNK={showMNK}
              onToggleMNK={setShowMNK}
              showResiduals={showResiduals}
              onToggleResiduals={setShowResiduals}
              autoScale={autoScale}
              onToggleAutoScale={setAutoScale}
              onStartLagrangeAnim={handleStartLagrangeAnim}
              onStartMNKAnim={handleStartMNKAnim}
              onPauseAnim={handlePauseAnim}
              onResetAnim={handleResetAnim}
              isAnimating={animState.active}
              points={points}
              predictMNK={olsModel.predict}
            />

            <div className="flex-1 w-full space-y-5">
              <MainChart
                points={points}
                lagrangeFn={showLagrange ? lagrangeFn : null}
                mnkFn={showMNK ? mnkFn : null}
                predictMNK={olsModel.predict}
                showLagrange={showLagrange}
                showMNK={showMNK}
                showResiduals={showResiduals}
                autoScale={autoScale}
                animState={animState}
              />

              <MetricsGrid metrics={olsModel.metrics} />
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <h2 className="text-sm font-semibold text-slate-800">
                Порівняльна матриця: 6 графіків апроксимації
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Одночасне відображення інтерполяції Лагранжа та апроксимації МНК (m=2) для 5, 10 та 20 точок.
              </p>
            </div>
            <Matrix6View />
          </div>
        )}
      </main>

      <footer className="max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 border-t border-slate-200 text-center text-xs text-slate-500">
        Лабораторна робота №1 «Апроксимація функцій методами інтерполяції та МНК» • Варіант 20
      </footer>
    </div>
  );
};
export default App;
