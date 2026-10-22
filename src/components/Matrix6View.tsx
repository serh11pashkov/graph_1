import React, { useRef, useEffect } from 'react';
import { DATASETS } from '../data/datasets';
import { lagrangeInterpolate, fitPolynomialOLS, computeViewport, generateTicks } from '../lib/math';
import { Point } from '../types';

interface MiniChartProps {
  points: Point[];
  type: 'lagrange' | 'mnk';
  title: string;
  badge: string;
}

const MiniChart: React.FC<MiniChartProps> = ({ points, type, title, badge }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    let curveFn: (x: number) => number;
    let color = '#0284c7';

    if (type === 'lagrange') {
      curveFn = (x: number) => lagrangeInterpolate(points, x);
      color = '#0284c7';
    } else {
      const ols = fitPolynomialOLS(points, 2);
      curveFn = (x: number) => ols.predict(x);
      color = '#059669';
    }

    const vp = computeViewport(points, [curveFn], 0.14);
    const margin = { top: 20, right: 20, bottom: 32, left: 44 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;

    const toScreenX = (x: number) => margin.left + ((x - vp.minX) / (vp.maxX - vp.minX)) * plotW;
    const toScreenY = (y: number) => margin.top + ((vp.maxY - y) / (vp.maxY - vp.minY)) * plotH;

    // Grid
    const xTicks = generateTicks(vp.minX, vp.maxX, 5).ticks;
    const yTicks = generateTicks(vp.minY, vp.maxY, 4).ticks;

    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (const xt of xTicks) {
      const sx = toScreenX(xt);
      if (sx >= margin.left && sx <= margin.left + plotW) {
        ctx.beginPath();
        ctx.moveTo(sx, margin.top);
        ctx.lineTo(sx, margin.top + plotH);
        ctx.stroke();
      }
    }
    for (const yt of yTicks) {
      const sy = toScreenY(yt);
      if (sy >= margin.top && sy <= margin.top + plotH) {
        ctx.beginPath();
        ctx.moveTo(margin.left, sy);
        ctx.lineTo(margin.left + plotW, sy);
        ctx.stroke();
      }
    }

    // Ticks
    ctx.fillStyle = '#64748b';
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    for (const xt of xTicks) {
      const sx = toScreenX(xt);
      if (sx >= margin.left + 10 && sx <= margin.left + plotW - 10) {
        ctx.fillText(xt.toString(), sx, margin.top + plotH + 8);
      }
    }
    ctx.textAlign = 'right';
    for (const yt of yTicks) {
      const sy = toScreenY(yt);
      if (sy >= margin.top + 6 && sy <= margin.top + plotH - 6) {
        ctx.fillText(yt.toString(), margin.left - 6, sy + 3);
      }
    }

    // Curve
    ctx.save();
    ctx.beginPath();
    ctx.rect(margin.left, margin.top, plotW, plotH);
    ctx.clip();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.0;
    ctx.shadowBlur = 0;

    const steps = 180;
    const dx = (vp.maxX - vp.minX) / steps;
    ctx.beginPath();
    let started = false;
    for (let i = 0; i <= steps; i++) {
      const x = vp.minX + i * dx;
      const y = curveFn(x);
      if (!Number.isFinite(y)) {
        started = false;
        continue;
      }
      const sx = toScreenX(x);
      const sy = toScreenY(y);
      if (sy < margin.top - 200 || sy > margin.top + plotH + 200) {
        started = false;
        continue;
      }
      if (!started) {
        ctx.moveTo(sx, sy);
        started = true;
      } else {
        ctx.lineTo(sx, sy);
      }
    }
    ctx.stroke();
    ctx.restore();

    // Points
    for (const pt of points) {
      const sx = toScreenX(pt.x);
      const sy = toScreenY(pt.y);
      if (sx >= margin.left && sx <= margin.left + plotW && sy >= margin.top && sy <= margin.top + plotH) {
        ctx.beginPath();
        ctx.arc(sx, sy, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = type === 'lagrange' ? '#0284c7' : '#059669';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    }
  }, [points, type]);

  return (
    <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-800">{title}</span>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded-md border ${
          type === 'lagrange'
            ? 'bg-sky-50 text-sky-700 border-sky-200'
            : 'bg-emerald-50 text-emerald-700 border-emerald-200'
        }`}>
          {badge}
        </span>
      </div>
      <div className="w-full h-52 bg-white rounded-xl overflow-hidden border border-slate-200">
        <canvas ref={canvasRef} className="w-full h-full block" />
      </div>
    </div>
  );
};

export const Matrix6View: React.FC = () => {
  const configs: MiniChartProps[] = [
    { points: DATASETS['5'], type: 'lagrange', title: '1. Лагранж (5 точок)', badge: 'Ступінь 4' },
    { points: DATASETS['5'], type: 'mnk', title: '2. МНК (5 точок)', badge: 'm = 2' },
    { points: DATASETS['10'], type: 'lagrange', title: '3. Лагранж (10 точок)', badge: 'Ступінь 9' },
    { points: DATASETS['10'], type: 'mnk', title: '4. МНК (10 точок)', badge: 'm = 2' },
    { points: DATASETS['20'], type: 'lagrange', title: '5. Лагранж (20 точок)', badge: 'Ступінь 19 (Рунге)' },
    { points: DATASETS['20'], type: 'mnk', title: '6. МНК (20 точок)', badge: 'm = 2' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {configs.map((cfg, i) => (
        <MiniChart key={i} {...cfg} />
      ))}
    </div>
  );
};
