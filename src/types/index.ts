export interface Point {
  x: number;
  y: number;
}

export type DatasetKey = '5' | '10' | '20';

export interface Metrics {
  mse: number;
  rmse: number;
  mae: number;
  r2: number;
  maxResidual: number;
  residuals: number[];
}

export interface RegressionModel {
  coeffs: number[];
  degree: number;
  predict: (x: number) => number;
  metrics: Metrics;
}

export interface Viewport {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export interface AnimationState {
  active: boolean;
  type: 'lagrange' | 'mnk' | null;
  step: number;
  progress: number;
}
