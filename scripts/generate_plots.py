import numpy as np
import matplotlib.pyplot as plt

# Вхідні датасети для варіанта 20
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

def lagrange_interp(points, x_vals):
    n = len(points)
    y_vals = np.zeros_like(x_vals, dtype=float)
    for k in range(n):
        xk, yk = points[k]
        num = np.ones_like(x_vals, dtype=float)
        den = 1.0
        for j in range(n):
            if j != k:
                xj, _ = points[j]
                num *= (x_vals - xj)
                den *= (xk - xj)
        y_vals += yk * (num / den)
    return y_vals

def mnk_poly(points, degree=2):
    x = points[:, 0]
    y = points[:, 1]
    # QR розклад матриці планування (стійкий МНК без звичайних нормальних рівнянь)
    X = np.vander(x, degree + 1, increasing=True)
    Q, R = np.linalg.qr(X)
    coeffs = np.linalg.solve(R, Q.T @ y)
    
    def predict(x_eval):
        X_eval = np.vander(x_eval, degree + 1, increasing=True)
        return X_eval @ coeffs
    
    return coeffs, predict

# Налаштування стилю (чистий білий фон для академічного звіту)
plt.style.use('default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.facecolor'] = '#ffffff'
plt.rcParams['axes.facecolor'] = '#ffffff'

datasets = [
    ('5', data_5, 4),
    ('10', data_10, 9),
    ('20', data_20, 19)
]

# 1. Генерація 6 окремих графіків
for key, data, deg_lag in datasets:
    x_min, x_max = -3.2, 5.2
    x_dense = np.linspace(x_min, x_max, 500)
    
    # --- Лагранж ---
    fig, ax = plt.subplots(figsize=(7, 4.4), dpi=220)
    y_lag = lagrange_interp(data, x_dense)
    ax.plot(x_dense, y_lag, color='#0284c7', lw=2.2, label=f'Поліном Лагранжа P_{deg_lag}(x)')
    ax.scatter(data[:, 0], data[:, 1], color='#ffffff', edgecolors='#0284c7', lw=1.8, s=50, zorder=5, label=f'Вузли (N={key})')
    ax.set_title(f'Інтерполяція Лагранжа для {key} точок (Ступінь {deg_lag})', color='#0f172a', fontsize=11.5, pad=10, weight='bold')
    ax.set_xlabel('x', color='#334155', fontsize=10, weight='bold')
    ax.set_ylabel('y', color='#334155', fontsize=10, weight='bold')
    ax.tick_params(colors='#334155', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.7, color='#cbd5e1')
    for spine in ax.spines.values():
        spine.set_color('#94a3b8')
    ax.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#0f172a', fontsize=9.5)
    
    # Автомасштабування
    y_pts_min, y_pts_max = np.min(data[:, 1]), np.max(data[:, 1])
    span = y_pts_max - y_pts_min
    if key == '20':
        ax.set_ylim(y_pts_min - 2.5 * span, y_pts_max + 2.5 * span)
    else:
        ax.set_ylim(min(np.min(y_lag), y_pts_min) - 0.15*span, max(np.max(y_lag), y_pts_max) + 0.15*span)
        
    plt.tight_layout()
    plt.savefig(f'assets/plot_lagrange_{key}.png', facecolor='#ffffff', edgecolor='none', bbox_inches='tight', pad_inches=0.08)
    plt.close()

    # --- МНК ---
    fig, ax = plt.subplots(figsize=(7, 4.4), dpi=220)
    coeffs, predict = mnk_poly(data, degree=2)
    y_mnk = predict(x_dense)
    y_pred_pts = predict(data[:, 0])
    residuals = data[:, 1] - y_pred_pts
    
    ax.plot(x_dense, y_mnk, color='#059669', lw=2.2, label='Апроксимація МНК (m=2)')
    # Малювання залишків
    for xi, yi, y_hat in zip(data[:, 0], data[:, 1], y_pred_pts):
        ax.plot([xi, xi], [yi, y_hat], color='#e11d48', linestyle=':', lw=1.6)
        
    ax.scatter(data[:, 0], data[:, 1], color='#ffffff', edgecolors='#059669', lw=1.8, s=50, zorder=5, label=f'Вузли (N={key})')
    ax.set_title(f'Апроксимація методом найменших квадратів (N={key}, m=2)', color='#0f172a', fontsize=11.5, pad=10, weight='bold')
    ax.set_xlabel('x', color='#334155', fontsize=10, weight='bold')
    ax.set_ylabel('y', color='#334155', fontsize=10, weight='bold')
    ax.tick_params(colors='#334155', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.7, color='#cbd5e1')
    for spine in ax.spines.values():
        spine.set_color('#94a3b8')
    ax.legend(frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#0f172a', fontsize=9.5)
    
    span = np.max(data[:, 1]) - np.min(data[:, 1])
    ax.set_ylim(np.min(y_mnk) - 0.2*span, np.max(y_mnk) + 0.2*span)
    
    plt.tight_layout()
    plt.savefig(f'assets/plot_mnk_{key}.png', facecolor='#ffffff', edgecolor='none', bbox_inches='tight', pad_inches=0.08)
    plt.close()

# 2. Матриця всіх 6 графіків (2 x 3)
fig, axes = plt.subplots(3, 2, figsize=(13, 12), dpi=220)

for row_idx, (key, data, deg_lag) in enumerate(datasets):
    x_dense = np.linspace(-3.2, 5.2, 500)
    
    # Колонка 0: Лагранж
    ax_l = axes[row_idx, 0]
    y_lag = lagrange_interp(data, x_dense)
    ax_l.plot(x_dense, y_lag, color='#0284c7', lw=2, label=f'Лагранж P_{deg_lag}(x)')
    ax_l.scatter(data[:, 0], data[:, 1], color='#ffffff', edgecolors='#0284c7', lw=1.5, s=40, zorder=5)
    ax_l.set_title(f'Лагранж: N={key} точок (Ступінь {deg_lag})', fontsize=11, color='#0284c7', weight='bold')
    ax_l.grid(True, linestyle='--', alpha=0.7, color='#cbd5e1')
    ax_l.tick_params(colors='#334155', labelsize=8.5)
    for spine in ax_l.spines.values():
        spine.set_color('#94a3b8')
    span = np.max(data[:, 1]) - np.min(data[:, 1])
    if key == '20':
        ax_l.set_ylim(np.min(data[:, 1]) - 3.0 * span, np.max(data[:, 1]) + 3.0 * span)
    else:
        ax_l.set_ylim(min(np.min(y_lag), np.min(data[:, 1])) - 0.15*span, max(np.max(y_lag), np.max(data[:, 1])) + 0.15*span)
        
    # Колонка 1: МНК
    ax_m = axes[row_idx, 1]
    coeffs, predict = mnk_poly(data, degree=2)
    y_mnk = predict(x_dense)
    y_pred_pts = predict(data[:, 0])
    ax_m.plot(x_dense, y_mnk, color='#059669', lw=2, label='МНК (m=2)')
    for xi, yi, y_hat in zip(data[:, 0], data[:, 1], y_pred_pts):
        ax_m.plot([xi, xi], [yi, y_hat], color='#e11d48', linestyle=':', lw=1.3)
    ax_m.scatter(data[:, 0], data[:, 1], color='#ffffff', edgecolors='#059669', lw=1.5, s=40, zorder=5)
    ax_m.set_title(f'МНК: N={key} точок (Поліном m=2)', fontsize=11, color='#059669', weight='bold')
    ax_m.grid(True, linestyle='--', alpha=0.7, color='#cbd5e1')
    ax_m.tick_params(colors='#334155', labelsize=8.5)
    for spine in ax_m.spines.values():
        spine.set_color('#94a3b8')
    ax_m.set_ylim(np.min(y_mnk) - 0.2*span, np.max(y_mnk) + 0.2*span)

fig.suptitle('Порівняльна матриця: 6 графіків апроксимації (Лагранж vs МНК) для Варіанта №20', 
             fontsize=13.5, color='#0f172a', weight='bold', y=0.995)
plt.tight_layout()
plt.savefig('assets/plot_matrix_6_all.png', facecolor='#ffffff', edgecolor='none', bbox_inches='tight', pad_inches=0.1)
plt.close()

print("All 6 individual plots and combined 2x3 matrix generated on clean white background successfully!")
