import matplotlib.pyplot as plt

def create_flowchart_lagrange():
    fig, ax = plt.subplots(figsize=(7.5, 9.5), dpi=220)
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    start_style = dict(boxstyle="round,pad=0.5", fc="#dbeafe", ec="#2563eb", lw=2)
    process_style = dict(boxstyle="square,pad=0.5", fc="#f8fafc", ec="#0284c7", lw=1.5)
    decision_style = dict(boxstyle="round4,pad=0.5", fc="#fefce8", ec="#d97706", lw=1.5)
    end_style = dict(boxstyle="round,pad=0.5", fc="#fee2e2", ec="#dc2626", lw=2)

    steps = [
        (0.5, 0.95, "Початок: lagrangeInterpolate(points, x)", start_style, "#1e3a8a"),
        (0.5, 0.84, "Ініціалізація:\n n = points.length, P = 0", process_style, "#0f172a"),
        (0.5, 0.72, "Цикл k від 0 до n-1\n(додавання базисних доданків)", decision_style, "#78350f"),
        (0.5, 0.58, "Обчислення базисного полінома L_k(x):\n term = points[k].y;\n Цикл j від 0 до n-1 (j != k):\n term *= (x - x_j) / (x_k - x_j)", process_style, "#0f172a"),
        (0.5, 0.44, "Накопичення суми:\n P = P + term", process_style, "#0f172a"),
        (0.5, 0.32, "k < n - 1 ?", decision_style, "#78350f"),
        (0.5, 0.19, "Повернення значення полінома P(x)", process_style, "#0f172a"),
        (0.5, 0.07, "Кінець алгоритму", end_style, "#991b1b")
    ]
    
    for x, y, text, style, t_col in steps:
        ax.text(x, y, text, ha="center", va="center", color=t_col,
                fontsize=9.5, weight="bold", bbox=style)
        
    arrows = [
        ((0.5, 0.92), (0.5, 0.88)),
        ((0.5, 0.80), (0.5, 0.76)),
        ((0.5, 0.68), (0.5, 0.64)),
        ((0.5, 0.52), (0.5, 0.47)),
        ((0.5, 0.41), (0.5, 0.36)),
        ((0.5, 0.28), (0.5, 0.22)),
        ((0.5, 0.16), (0.5, 0.10))
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2))
        
    # Цикл (зворотний зв'язок при k < n-1: Так)
    # Стрілочка виходить знизу з блоку умови вправо, а вгорі входить у блок циклу
    loop_x = 0.79
    # 1. Горизонтальна стрілка внизу від правого краю блоку умови вправо
    ax.annotate("", xy=(loop_x, 0.32), xytext=(0.564, 0.32),
                arrowprops=dict(arrowstyle="->", color="#b45309", lw=1.8, ls="--"))
    ax.text(0.67, 0.338, "Так", ha="center", va="bottom", color="#b45309", fontsize=9.5, weight="bold")
    # 2. Вертикальна лінія вгору
    ax.plot([loop_x, loop_x], [0.32, 0.72], color="#b45309", lw=1.8, ls="--")
    # 3. Горизонтальна лінія вліво у блок циклу
    ax.plot([loop_x, 0.704], [0.72, 0.72], color="#b45309", lw=1.8, ls="--")
    ax.text(0.52, 0.25, "Ні", ha="left", va="center", color="#0284c7", fontsize=9.5, weight="bold")

    plt.tight_layout()
    plt.savefig("diagrams/flowchart_lagrange.png", facecolor="#ffffff", edgecolor="none", bbox_inches='tight', pad_inches=0.08)
    plt.close()

def create_flowchart_mnk():
    fig, ax = plt.subplots(figsize=(7.5, 9.5), dpi=220)
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    start_style = dict(boxstyle="round,pad=0.5", fc="#d1fae5", ec="#059669", lw=2)
    process_style = dict(boxstyle="square,pad=0.5", fc="#f8fafc", ec="#059669", lw=1.5)
    end_style = dict(boxstyle="round,pad=0.5", fc="#fee2e2", ec="#dc2626", lw=2)

    steps = [
        (0.5, 0.95, "Початок: fitPolynomialOLS(points, degree)", start_style, "#065f46"),
        (0.5, 0.83, "Формування матриці планування X:\n X[i][j] = x_i^j (i=0..N-1, j=0..m)\n Вектор відгуків Y[i] = y_i", process_style, "#0f172a"),
        (0.5, 0.69, "Побудова СЛАР:\n A = X^T * X,  B = X^T * Y\n (або QR-розклад X = Q * R)", process_style, "#0f172a"),
        (0.5, 0.55, "Чисельно стійке розв'язання:\n Метод Гаусса з частковим вибором ведучого елемента\n або зворотна підстановка для R * a = Q^T * Y", process_style, "#0f172a"),
        (0.5, 0.41, "Отримання вектору коефіцієнтів a = [a_0, a_1, ..., a_m]\n Побудова функції моделі y_hat(x) = sum(a_k * x^k)", process_style, "#0f172a"),
        (0.5, 0.27, "Обчислення похибок та критеріїв якості:\n Залишки r_i = y_i - y_hat(x_i),  MSE, RMSE, MAE, R^2", process_style, "#0f172a"),
        (0.5, 0.14, "Повернення результату апроксимації", process_style, "#0f172a"),
        (0.5, 0.04, "Кінець алгоритму", end_style, "#991b1b")
    ]
    
    for x, y, text, style, t_col in steps:
        ax.text(x, y, text, ha="center", va="center", color=t_col,
                fontsize=9.5, weight="bold", bbox=style)
        
    arrows = [
        ((0.5, 0.92), (0.5, 0.88)),
        ((0.5, 0.78), (0.5, 0.74)),
        ((0.5, 0.64), (0.5, 0.60)),
        ((0.5, 0.50), (0.5, 0.46)),
        ((0.5, 0.36), (0.5, 0.32)),
        ((0.5, 0.22), (0.5, 0.18)),
        ((0.5, 0.11), (0.5, 0.07))
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color="#059669", lw=2))

    plt.tight_layout()
    plt.savefig("diagrams/flowchart_mnk.png", facecolor="#ffffff", edgecolor="none", bbox_inches='tight', pad_inches=0.08)
    plt.close()

def create_flowchart_autoscale():
    fig, ax = plt.subplots(figsize=(7.5, 9.5), dpi=220)
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    start_style = dict(boxstyle="round,pad=0.5", fc="#ede9fe", ec="#7c3aed", lw=2)
    process_style = dict(boxstyle="square,pad=0.5", fc="#f8fafc", ec="#7c3aed", lw=1.5)
    end_style = dict(boxstyle="round,pad=0.5", fc="#fee2e2", ec="#dc2626", lw=2)

    steps = [
        (0.5, 0.95, "Початок: computeAutoScale(points, curves, width, height)", start_style, "#5b21b6"),
        (0.5, 0.83, "Визначення діапазону аргументів:\n minX = min(x_i), maxX = max(x_i)", process_style, "#0f172a"),
        (0.5, 0.70, "Дискретизація кривих Лагранжа та МНК\n на K точках на відрізку [minX, maxX]", process_style, "#0f172a"),
        (0.5, 0.56, "Обчислення екстремумів значень:\n minY = min(y_points, y_curves), maxY = max(y_points, y_curves)\n (застосування захисного clamp проти розбіжностей Рунге)", process_style, "#0f172a"),
        (0.5, 0.42, "Додавання безпечного динамічного padding (10-15%)\n spanX = maxX - minX;  spanY = maxY - minY", process_style, "#0f172a"),
        (0.5, 0.28, "Розрахунок коефіцієнтів проекції світ->екран:\n scaleX = plotW / spanX; scaleY = plotH / spanY", process_style, "#0f172a"),
        (0.5, 0.15, "Генерація адаптивної сітки (Nice Step Algorithm: 1, 2, 5 * 10^p)", process_style, "#0f172a"),
        (0.5, 0.04, "Кінець: Повернення об'єкта системи координат Viewport", end_style, "#991b1b")
    ]
    
    for x, y, text, style, t_col in steps:
        ax.text(x, y, text, ha="center", va="center", color=t_col,
                fontsize=9.5, weight="bold", bbox=style)
        
    arrows = [
        ((0.5, 0.92), (0.5, 0.88)),
        ((0.5, 0.78), (0.5, 0.74)),
        ((0.5, 0.65), (0.5, 0.61)),
        ((0.5, 0.51), (0.5, 0.47)),
        ((0.5, 0.37), (0.5, 0.33)),
        ((0.5, 0.23), (0.5, 0.19)),
        ((0.5, 0.11), (0.5, 0.07))
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=2))

from PIL import Image
import numpy as np

def autocrop_white(filepath, pad=25):
    img = Image.open(filepath)
    arr = np.array(img)
    H, W = arr.shape[:2]
    not_white = (arr[:, :, :3] < 248).any(axis=2)
    cols = np.where(not_white.sum(axis=0) > 3)[0]
    rows = np.where(not_white.sum(axis=1) > 3)[0]
    if len(cols) and len(rows):
        x1 = max(0, cols[0] - pad)
        y1 = max(0, rows[0] - pad)
        x2 = min(W, cols[-1] + pad)
        y2 = min(H, rows[-1] + pad)
        img.crop((x1, y1, x2, y2)).save(filepath)

if __name__ == "__main__":
    create_flowchart_lagrange()
    autocrop_white("diagrams/flowchart_lagrange.png")
    create_flowchart_mnk()
    autocrop_white("diagrams/flowchart_mnk.png")
    create_flowchart_autoscale()
    autocrop_white("diagrams/flowchart_autoscale.png")
    print("All white flowcharts generated and autocropped successfully!")

