import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

data_5 = np.array([
    [-3.0, -2.1],
    [-1.0, -0.8],
    [1.0, 0.9],
    [3.0, 2.2],
    [5.0, 3.1]
])

data_10 = np.array([
    [-3.0, -2.10],
    [-2.1, -1.55],
    [-1.2, -0.93],
    [-1.0, -0.80],
    [-0.2, -0.12],
    [0.8, 0.72],
    [1.0, 0.90],
    [2.1, 1.68],
    [3.0, 2.20],
    [5.0, 3.10]
])

data_20 = np.array([
    [-3.0, -2.10],
    [-2.6, -1.88],
    [-2.1, -1.55],
    [-1.7, -1.27],
    [-1.3, -1.00],
    [-1.0, -0.80],
    [-0.6, -0.45],
    [-0.2, -0.12],
    [0.2, 0.20],
    [0.6, 0.54],
    [1.0, 0.90],
    [1.4, 1.22],
    [1.8, 1.50],
    [2.2, 1.74],
    [2.6, 1.98],
    [3.0, 2.20],
    [3.5, 2.48],
    [4.0, 2.75],
    [4.5, 2.96],
    [5.0, 3.10]
])

def compute_metrics(points, method='mnk', degree=2):
    x = points[:, 0]
    y = points[:, 1]
    N = len(points)
    
    if method == 'lagrange':
        y_pred = y.copy()
        deg = N - 1
    else:
        deg = degree
        X = np.vander(x, degree + 1, increasing=True)
        Q, R = np.linalg.qr(X)
        coeffs = np.linalg.solve(R, Q.T @ y)
        y_pred = X @ coeffs
        
    residuals = y - y_pred
    mse = np.mean(residuals**2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(residuals))
    
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum(residuals**2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 1.0
    max_res = np.max(np.abs(residuals))
    
    return {
        'N': N,
        'method': method,
        'degree': deg,
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'max_res': max_res
    }

results = []
for d in [data_5, data_10, data_20]:
    results.append(compute_metrics(d, 'lagrange'))
    results.append(compute_metrics(d, 'mnk', degree=1))
    results.append(compute_metrics(d, 'mnk', degree=2))
    results.append(compute_metrics(d, 'mnk', degree=3))

print(f"{'Метод':<12} | {'N':<3} | {'deg':<3} | {'MSE':<10} | {'RMSE':<10} | {'MAE':<10} | {'R^2':<8} | {'Max |r|':<8}")
print("-" * 75)
for r in results:
    m_name = "Лагранж" if r['method'] == 'lagrange' else f"МНК m={r['degree']}"
    print(f"{m_name:<12} | {r['N']:<3} | {r['degree']:<3} | {r['mse']:<10.6f} | {r['rmse']:<10.6f} | {r['mae']:<10.6f} | {r['r2']:<8.4f} | {r['max_res']:<8.4f}")
