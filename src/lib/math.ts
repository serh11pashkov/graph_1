import { Matrix, QrDecomposition } from 'ml-matrix';
import { Point, Metrics, RegressionModel, Viewport } from '../types';

/**
 * Класичний інтерполяційний поліном Лагранжа:
 * P_n(x) = \sum_{k=0}^{n} y_k \prod_{j \ne k} \frac{x - x_j}{x_k - x_j}
 */
export function lagrangeInterpolate(points: Point[], x: number): number {
  const n = points.length;
  if (n === 0) return 0;
  if (n === 1) return points[0].y;

  // Точний збіг із вузлом для уникнення ділення 0 / 0
  for (let i = 0; i < n; i++) {
    if (Math.abs(x - points[i].x) < 1e-12) {
      return points[i].y;
    }
  }

  let result = 0;
  for (let k = 0; k < n; k++) {
    let term = points[k].y;
    for (let j = 0; j < n; j++) {
      if (j !== k) {
        const denom = points[k].x - points[j].x;
        if (Math.abs(denom) < 1e-12) continue;
        term *= (x - points[j].x) / denom;
      }
    }
    result += term;
  }
  return result;
}

/**
 * Обчислення значення полінома за схемою Горнера
 */
export function evaluatePolynomial(coeffs: number[], x: number): number {
  const m = coeffs.length - 1;
  let res = coeffs[m];
  for (let i = m - 1; i >= 0; i--) {
    res = res * x + coeffs[i];
  }
  return res;
}

/**
 * Стійкий розрахунок МНК для поліноміальної моделі через QR-розклад (ml-matrix).
 * Уникає прямого формування нормальних рівнянь X^T * X,
 * запобігаючи квадратичному зростанню числа обумовленості.
 */
export function fitPolynomialOLS(points: Point[], degree: number = 2): RegressionModel {
  const N = points.length;
  const m = Math.min(degree, Math.max(1, N - 1));
  const p = m + 1; // кількість коефіцієнтів [a_0, a_1, ..., a_m]

  // 1. Формуємо матрицю планування Вандермонда X (N x p)
  const matrixData: number[][] = [];
  const yData: number[] = [];

  for (let i = 0; i < N; i++) {
    const row = new Array<number>(p);
    let val = 1.0;
    const xi = points[i].x;
    for (let j = 0; j < p; j++) {
      row[j] = val;
      val *= xi;
    }
    matrixData.push(row);
    yData.push(points[i].y);
  }

  const X = new Matrix(matrixData);
  const Y = Matrix.columnVector(yData);

  // 2. Стійкий QR-розклад через Householder reflections
  const qr = new QrDecomposition(X);
  const solution = qr.solve(Y);
  const coeffs = solution.to1DArray();

  const predict = (x: number) => evaluatePolynomial(coeffs, x);
  const metrics = calculateMetrics(points, predict);

  return {
    coeffs,
    degree: m,
    predict,
    metrics,
  };
}

/**
 * Обчислення статистичних оцінок якості апроксимації
 */
export function calculateMetrics(points: Point[], predict: (x: number) => number): Metrics {
  const N = points.length;
  if (N === 0) {
    return { mse: 0, rmse: 0, mae: 0, r2: 0, maxResidual: 0, residuals: [] };
  }

  const meanY = points.reduce((acc, p) => acc + p.y, 0) / N;
  let ssRes = 0;
  let ssTot = 0;
  let sumAbs = 0;
  let maxRes = 0;
  const residuals: number[] = [];

  for (let i = 0; i < N; i++) {
    const pred = predict(points[i].x);
    const res = points[i].y - pred;
    residuals.push(res);
    ssRes += res * res;
    ssTot += (points[i].y - meanY) * (points[i].y - meanY);
    sumAbs += Math.abs(res);
    if (Math.abs(res) > maxRes) maxRes = Math.abs(res);
  }

  const mse = ssRes / N;
  const rmse = Math.sqrt(mse);
  const mae = sumAbs / N;
  const r2 = ssTot < 1e-12 ? 1.0 : Math.max(-1.0, 1.0 - ssRes / ssTot);

  return {
    mse,
    rmse,
    mae,
    r2,
    maxResidual: maxRes,
    residuals,
  };
}

/**
 * Автоматичне масштабування (Auto-scale) полотна
 */
export function computeViewport(
  points: Point[],
  curves: ((x: number) => number)[] = [],
  paddingRatio: number = 0.12
): Viewport {
  if (points.length === 0) {
    return { minX: -5, maxX: 5, minY: -5, maxY: 5 };
  }

  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  for (const pt of points) {
    if (pt.x < minX) minX = pt.x;
    if (pt.x > maxX) maxX = pt.x;
    if (pt.y < minY) minY = pt.y;
    if (pt.y > maxY) maxY = pt.y;
  }

  if (minX === maxX) { minX -= 1; maxX += 1; }
  if (minY === maxY) { minY -= 1; maxY += 1; }

  const samples = 200;
  const step = (maxX - minX) / (samples - 1);
  const ySpanBase = maxY - minY;
  const safetyMax = maxY + ySpanBase * 6.0;
  const safetyMin = minY - ySpanBase * 6.0;

  for (const fn of curves) {
    for (let i = 0; i < samples; i++) {
      const x = minX + i * step;
      const y = fn(x);
      if (Number.isFinite(y)) {
        const clampedY = Math.max(safetyMin, Math.min(safetyMax, y));
        if (clampedY < minY) minY = clampedY;
        if (clampedY > maxY) maxY = clampedY;
      }
    }
  }

  const spanX = maxX - minX;
  const padX = spanX * paddingRatio;
  minX -= padX;
  maxX += padX;

  const spanY = maxY - minY;
  const padY = Math.max(spanY * paddingRatio, 0.35);
  minY -= padY;
  maxY += padY;

  return { minX, maxX, minY, maxY };
}

/**
 * Алгоритм розстановки гарних міток сітки
 */
export function generateTicks(min: number, max: number, targetTicks: number = 6) {
  const range = max - min;
  const rawStep = range / targetTicks;
  const power = Math.floor(Math.log10(rawStep));
  const fraction = rawStep / Math.pow(10, power);
  let niceFraction = 1;
  if (fraction < 1.5) niceFraction = 1;
  else if (fraction < 3) niceFraction = 2;
  else if (fraction < 7) niceFraction = 5;
  else niceFraction = 10;
  const step = niceFraction * Math.pow(10, power);

  const start = Math.ceil(min / step) * step;
  const ticks: number[] = [];
  for (let val = start; val <= max + 1e-9; val += step) {
    ticks.push(parseFloat(val.toFixed(4)));
  }
  return { step, ticks };
}
