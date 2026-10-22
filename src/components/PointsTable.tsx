import React from 'react';
import { Point } from '../types';

interface PointsTableProps {
  points: Point[];
  predictMNK: (x: number) => number;
}

export const PointsTable: React.FC<PointsTableProps> = ({ points, predictMNK }) => {
  return (
    <div className="overflow-x-auto max-h-[220px] overflow-y-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-200 text-[11px] font-semibold text-slate-500 bg-slate-50/50">
            <th className="py-2 px-3 text-center w-8">#</th>
            <th className="py-2 px-3 text-right">X</th>
            <th className="py-2 px-3 text-right">Y факт</th>
            <th className="py-2 px-3 text-right">Y МНК</th>
            <th className="py-2 px-3 text-right">Залишок (r)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-xs font-mono">
          {points.map((pt, i) => {
            const pred = predictMNK(pt.x);
            const res = pt.y - pred;
            return (
              <tr key={i} className="hover:bg-slate-50 transition-colors">
                <td className="py-2 px-3 text-center text-slate-400 font-sans text-[11px]">
                  {i + 1}
                </td>
                <td className="py-2 px-3 text-right text-slate-700">
                  {pt.x.toFixed(2)}
                </td>
                <td className="py-2 px-3 text-right text-slate-900 font-semibold">
                  {pt.y.toFixed(2)}
                </td>
                <td className="py-2 px-3 text-right text-emerald-700 font-medium">
                  {pred.toFixed(2)}
                </td>
                <td className={`py-2 px-3 text-right font-medium ${res >= 0 ? 'text-slate-600' : 'text-rose-600'}`}>
                  {res > 0 ? `+${res.toFixed(2)}` : res.toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
