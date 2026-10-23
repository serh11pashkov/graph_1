import React, { useRef, useEffect, useState } from 'react';
import { Point, AnimationState } from '../types';
import { computeViewport, generateTicks } from '../lib/math';

interface MainChartProps {
  points: Point[];
  lagrangeFn: ((x: number) => number) | null;
  mnkFn: ((x: number) => number) | null;
  predictMNK: (x: number) => number;
  showLagrange: boolean;
  showMNK: boolean;
  showResiduals: boolean;
  autoScale: boolean;
  animState: AnimationState;
}

export const MainChart: React.FC<MainChartProps> = ({
  points,
  lagrangeFn,
  mnkFn,
  predictMNK,
  showLagrange,
  showMNK,
  showResiduals,
  autoScale,
  animState,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hoverInfo, setHoverInfo] = useState<{
    x: number;
    y: number;
    point?: Point;
    lagrangeVal?: number;
    mnkVal?: number;
  } | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Retina DPI setup
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const width = rect.width;
    const height = rect.height;

    // Clear background: pure crisp white
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    // Active curves for viewport
    const curvesToFit: ((x: number) => number)[] = [];
    if (showLagrange && lagrangeFn) curvesToFit.push(lagrangeFn);
    if (showMNK && mnkFn) curvesToFit.push(mnkFn);

    const vp = computeViewport(points, autoScale ? curvesToFit : [], 0.12);

    const margin = { top: 32, right: 32, bottom: 48, left: 56 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;

    const toScreenX = (x: number) => margin.left + ((x - vp.minX) / (vp.maxX - vp.minX)) * plotW;
    const toScreenY = (y: number) => margin.top + ((vp.maxY - y) / (vp.maxY - vp.minY)) * plotH;

    // 1. Координатна сітка - тонка, світла, висококонтрастна
    const xTicks = generateTicks(vp.minX, vp.maxX, 8).ticks;
    const yTicks = generateTicks(vp.minY, vp.maxY, 6).ticks;

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

    // 2. Нульові осі X=0 та Y=0
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 1.2;
    if (vp.minY <= 0 && vp.maxY >= 0) {
      const zeroY = toScreenY(0);
      ctx.beginPath();
      ctx.moveTo(margin.left, zeroY);
      ctx.lineTo(margin.left + plotW, zeroY);
      ctx.stroke();
    }
    if (vp.minX <= 0 && vp.maxX >= 0) {
      const zeroX = toScreenX(0);
      ctx.beginPath();
      ctx.moveTo(zeroX, margin.top);
      ctx.lineTo(zeroX, margin.top + plotH);
      ctx.stroke();
    }

    // 3. Підписи осей та мітки
    ctx.fillStyle = '#64748b'; // slate-500
    ctx.font = '11px "JetBrains Mono", Inter, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    for (const xt of xTicks) {
      const sx = toScreenX(xt);
      if (sx >= margin.left + 15 && sx <= margin.left + plotW - 15) {
        ctx.fillText(xt.toString(), sx, margin.top + plotH + 8);
      }
    }

    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (const yt of yTicks) {
      const sy = toScreenY(yt);
      if (sy >= margin.top + 8 && sy <= margin.top + plotH - 8) {
        ctx.fillText(yt.toString(), margin.left - 10, sy);
      }
    }

    // Підписи осей
    ctx.fillStyle = '#475569'; // slate-600
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Аргумент x', margin.left + plotW / 2, margin.top + plotH + 30);

    ctx.save();
    ctx.translate(18, margin.top + plotH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillText('Функція y = f(x)', 0, 0);
    ctx.restore();

    // 4. Малювання кривих (ЧІТКІ, НАСИЧЕНІ)
    const drawCurveMatte = (fn: (x: number) => number, color: string, strokeWidth = 2.0) => {
      ctx.save();
      ctx.beginPath();
      ctx.rect(margin.left, margin.top, plotW, plotH);
      ctx.clip();

      ctx.strokeStyle = color;
      ctx.lineWidth = strokeWidth;
      ctx.shadowBlur = 0;

      const steps = 300;
      const dx = (vp.maxX - vp.minX) / steps;
      let started = false;

      ctx.beginPath();
      for (let i = 0; i <= steps; i++) {
        const x = vp.minX + i * dx;
        const y = fn(x);
        if (!Number.isFinite(y)) {
          started = false;
          continue;
        }

        const sx = toScreenX(x);
        const sy = toScreenY(y);

        if (sy < margin.top - 300 || sy > margin.top + plotH + 300) {
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
    };

    // Крива Лагранжа (насичений синій #0284c7)
    if (showLagrange && lagrangeFn) {
      drawCurveMatte(lagrangeFn, '#0284c7', 2.0);
    }

    // Крива МНК (насичений смарагдовий #059669)
    if (showMNK && mnkFn) {
      drawCurveMatte(mnkFn, '#059669', 2.0);
    }

    // 5. Відрізки залишків r_i (насичений червоний #e11d48)
    if (showResiduals && showMNK) {
      const progress = animState.active && animState.type === 'mnk'
        ? Math.max(0, (animState.progress - 0.4) * 1.66)
        : 1.0;

      if (progress > 0) {
        ctx.save();
        ctx.strokeStyle = '#e11d48';
        ctx.lineWidth = 1.3;
        ctx.setLineDash([3, 3]);

        for (const pt of points) {
          const predY = predictMNK(pt.x);
          const currY = pt.y - (pt.y - predY) * progress;
          const sx = toScreenX(pt.x);
          const sy1 = toScreenY(pt.y);
          const sy2 = toScreenY(currY);

          if (sx >= margin.left && sx <= margin.left + plotW) {
            ctx.beginPath();
            ctx.moveTo(sx, sy1);
            ctx.lineTo(sx, sy2);
            ctx.stroke();

            // Кінцевий маркер
            ctx.beginPath();
            ctx.arc(sx, sy2, 2.5, 0, Math.PI * 2);
            ctx.fillStyle = '#e11d48';
            ctx.fill();
          }
        }
        ctx.restore();
      }
    }

    // 6. Експериментальні точки
    for (let i = 0; i < points.length; i++) {
      const pt = points[i];
      const sx = toScreenX(pt.x);
      const sy = toScreenY(pt.y);

      if (sx < margin.left || sx > margin.left + plotW || sy < margin.top || sy > margin.top + plotH) {
        continue;
      }

      const isCurrentActive = animState.active && animState.type === 'lagrange' && animState.step === i;

      ctx.beginPath();
      ctx.arc(sx, sy, isCurrentActive ? 6.5 : 4.5, 0, Math.PI * 2);
      ctx.fillStyle = isCurrentActive ? '#d97706' : '#2563eb';
      ctx.fill();

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.8;
      ctx.stroke();
    }
  }, [points, lagrangeFn, mnkFn, predictMNK, showLagrange, showMNK, showResiduals, autoScale, animState]);

  return (
    <div className="relative w-full h-[540px] bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        onMouseMove={(e) => {
          const canvas = canvasRef.current;
          if (!canvas) return;
          const rect = canvas.getBoundingClientRect();
          const mx = e.clientX - rect.left;
          const my = e.clientY - rect.top;

          // Hit test for points
          const margin = { top: 32, right: 32, bottom: 48, left: 56 };
          const plotW = rect.width - margin.left - margin.right;
          const plotH = rect.height - margin.top - margin.bottom;

          const vp = computeViewport(points, [], 0.12);
          const toScreenX = (x: number) => margin.left + ((x - vp.minX) / (vp.maxX - vp.minX)) * plotW;
          const toScreenY = (y: number) => margin.top + ((vp.maxY - y) / (vp.maxY - vp.minY)) * plotH;

          let found: Point | null = null;
          for (const pt of points) {
            const sx = toScreenX(pt.x);
            const sy = toScreenY(pt.y);
            if (Math.hypot(mx - sx, my - sy) <= 12) {
              found = pt;
              break;
            }
          }

          if (found) {
            setHoverInfo({
              x: mx,
              y: my,
              point: found,
              lagrangeVal: lagrangeFn ? lagrangeFn(found.x) : undefined,
              mnkVal: mnkFn ? mnkFn(found.x) : undefined,
            });
          } else {
            setHoverInfo(null);
          }
        }}
        onMouseLeave={() => setHoverInfo(null)}
      />

      {/* Легенда у верхньому правому кутку */}
      <div className="absolute top-4 right-5 flex items-center gap-4 bg-white/95 backdrop-blur-md px-3.5 py-1.5 rounded-xl border border-slate-200 text-[11px] text-slate-700 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600 border border-white shadow-sm"></span>
          <span className="font-medium text-slate-700">Вузли</span>
        </div>
        {showLagrange && (
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-[2.5px] bg-sky-600 rounded-full"></span>
            <span className="font-medium text-slate-800">Лагранж</span>
          </div>
        )}
        {showMNK && (
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-[2.5px] bg-emerald-600 rounded-full"></span>
            <span className="font-medium text-slate-800">МНК</span>
          </div>
        )}
        {showResiduals && showMNK && (
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-[2px] border-t-2 border-dashed border-rose-500"></span>
            <span className="font-medium text-rose-600">Залишки</span>
          </div>
        )}
      </div>

      {/* Тултіп в стилі modern light */}
      {hoverInfo && hoverInfo.point && (
        <div
          className="absolute z-20 pointer-events-none bg-white/95 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-200 shadow-lg text-xs space-y-1 transform -translate-x-1/2 -translate-y-full mb-3"
          style={{ left: hoverInfo.x, top: hoverInfo.y - 8 }}
        >
          <div className="font-mono text-slate-900 font-semibold border-b border-slate-100 pb-1">
            ({hoverInfo.point.x.toFixed(2)}, {hoverInfo.point.y.toFixed(2)})
          </div>
          {hoverInfo.lagrangeVal !== undefined && (
            <div className="text-sky-700 text-[11px] font-mono font-medium">
              Лагранж: {hoverInfo.lagrangeVal.toFixed(3)}
            </div>
          )}
          {hoverInfo.mnkVal !== undefined && (
            <div className="text-emerald-700 text-[11px] font-mono font-medium">
              МНК: {hoverInfo.mnkVal.toFixed(3)} (r: {(hoverInfo.point.y - hoverInfo.mnkVal).toFixed(3)})
            </div>
          )}
        </div>
      )}
    </div>
  );
};
