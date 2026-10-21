import matplotlib.pyplot as plt

def create_sequence_diagram():
    fig, ax = plt.subplots(figsize=(9.5, 7.5), dpi=220)
    ax.axis('off')
    
    # Actors / Lifelines
    actors = [
        ("Користувач", 0.1),
        ("UI Controller\n(app.js)", 0.32),
        ("Math Engine\n(math.js)", 0.58),
        ("Chart Engine\n(chart.js)", 0.85)
    ]
    
    for name, x in actors:
        # Header box
        ax.text(x, 0.92, name, ha="center", va="center", color="#0f172a",
                fontsize=9.5, weight="bold",
                bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.8))
        # Lifeline
        ax.plot([x, x], [0.86, 0.08], color="#94a3b8", linestyle="--", lw=1.3)
        
    messages = [
        (0.1, 0.32, 0.82, "1. Вибір датасету (5/10/20 точок) / Ступеня m", "#0284c7", False),
        (0.32, 0.58, 0.74, "2. fitPolynomialOLS(points, m) / lagrange()", "#0284c7", False),
        (0.58, 0.58, 0.67, "3. QR-розклад X = QR & розрахунок a = R^-1 Q^T Y", "#059669", True),
        (0.58, 0.32, 0.58, "4. Повернення {predict, residuals, metrics}", "#059669", False),
        (0.32, 0.58, 0.50, "5. computeViewport(points, curves, w, h)", "#0284c7", False),
        (0.58, 0.32, 0.42, "6. Повернення меж [minX, maxX, minY, maxY]", "#059669", False),
        (0.32, 0.85, 0.34, "7. renderChart(ctx, curves, viewport)", "#7c3aed", False),
        (0.85, 0.85, 0.26, "8. Відмальовування осей, сітки, кривих, точок", "#7c3aed", True),
        (0.85, 0.1, 0.16, "9. Візуальне оновлення Canvas (60 FPS)", "#b45309", False)
    ]
    
    for x1, x2, y, text, color, is_self in messages:
        if is_self:
            # Self call loop
            ax.plot([x1, x1 + 0.05, x1 + 0.05, x1], [y + 0.02, y + 0.02, y - 0.03, y - 0.03],
                    color=color, lw=1.8)
            ax.annotate("", xy=(x1, y - 0.03), xytext=(x1 + 0.01, y - 0.03),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8))
            ax.text(x1 + 0.06, y - 0.005, text, color="#0f172a", fontsize=8.5, weight="bold", va="center")
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8))
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 0.02, text, color="#0f172a", fontsize=8.5, weight="bold", ha="center", va="bottom")
            
    plt.tight_layout()
    plt.savefig("diagrams/sequence_diagram.png", facecolor="#ffffff", edgecolor="none", bbox_inches='tight', pad_inches=0.08)
    plt.close()

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(9.5, 6.8), dpi=220)
    ax.axis('off')
    
    box_style_ui = dict(boxstyle="round,pad=0.5", fc="#eff6ff", ec="#2563eb", lw=1.8)
    box_style_app = dict(boxstyle="round,pad=0.5", fc="#f8fafc", ec="#0284c7", lw=1.5)
    box_style_math = dict(boxstyle="round,pad=0.5", fc="#ecfdf5", ec="#059669", lw=1.8)
    box_style_data = dict(boxstyle="round,pad=0.5", fc="#fffbeb", ec="#d97706", lw=1.8)
    box_style_render = dict(boxstyle="round,pad=0.5", fc="#faf5ff", ec="#9333ea", lw=1.8)
    
    # Layers
    layers = [
        (0.5, 0.88, "Користувацький інтерфейс (Presentation Layer)\nHTML5 / Tailwind CSS / Dark Theme / Tooltips", box_style_ui, "#1e3a8a"),
        (0.25, 0.60, "Керування станом (app.js)\n• Event Listeners\n• Animation Loop (rAF)\n• Dataset Switching", box_style_app, "#0f172a"),
        (0.75, 0.60, "Графічний рушій (chart.js)\n• Canvas 2D Context\n• Transform World <-> Screen\n• Residuals & Points Rendering", box_style_render, "#581c87"),
        (0.25, 0.28, "Сховище даних (data.js)\n• Варіант 20 (5 точок)\n• Набори 10 і 20 точок\n• Копіювання без мутацій", box_style_data, "#78350f"),
        (0.75, 0.28, "Математичне ядро (math.js)\n• Інтерполятор Лагранжа\n• Стійкий МНК (QR-розклад)\n• Автомасштабування осей\n• Метрики: MSE, RMSE, R^2", box_style_math, "#065f46")
    ]
    
    for x, y, text, style, t_col in layers:
        ax.text(x, y, text, ha="center", va="center", color=t_col,
                fontsize=8.5, weight="bold", bbox=style)
        
    # Connectors
    conns = [
        ((0.5, 0.82), (0.25, 0.68)),
        ((0.5, 0.82), (0.75, 0.68)),
        ((0.25, 0.50), (0.25, 0.36)),
        ((0.25, 0.50), (0.75, 0.36)),
        ((0.75, 0.38), (0.75, 0.50)),
        ((0.36, 0.60), (0.62, 0.60))
    ]
    for start, end in conns:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="<->", color="#64748b", lw=1.8))
        
    ax.set_title("Архітектурна діаграма підсистем програмного комплексу", 
                 color="#0f172a", fontsize=12, pad=12, weight="bold")
    plt.tight_layout()
    plt.savefig("diagrams/architecture_diagram.png", facecolor="#ffffff", edgecolor="none", bbox_inches='tight', pad_inches=0.08)
    plt.close()

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
    create_sequence_diagram()
    autocrop_white("diagrams/sequence_diagram.png")
    create_architecture_diagram()
    autocrop_white("diagrams/architecture_diagram.png")
    print("White sequence and architecture diagrams generated and autocropped successfully!")

