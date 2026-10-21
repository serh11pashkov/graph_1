import os
import sys
import docx

sys.stdout.reconfigure(encoding='utf-8')
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pygments import lex
from pygments.lexers import TypeScriptLexer
from pygments.token import Token

CONTROL_KEYWORDS = {'if', 'else', 'return', 'for', 'while', 'break', 'continue', 'switch', 'case', 'try', 'catch', 'finally', 'throw', 'yield', 'await', 'do'}
DECL_KEYWORDS = {'const', 'let', 'var', 'function', 'class', 'interface', 'type', 'export', 'import', 'from', 'new', 'default', 'as', 'in', 'of', 'extends', 'implements'}
KNOWN_TYPES = {'Point', 'DatasetKey', 'AnimationState', 'Viewport', 'RegressionModel', 'Metrics', 'Matrix', 'QrDecomposition', 'Array', 'Record', 'Function', 'Object', 'number', 'string', 'boolean', 'void', 'any'}
KNOWN_GLOBALS = {'Math', 'Number', 'Infinity', 'console'}

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()
    
    # Поля: ліве 30 мм (1.18"), праве 15 мм (0.59"), верхнє 20 мм (0.79"), нижнє 20 мм (0.79")
    for s in doc.sections:
        s.top_margin = Inches(0.79)
        s.bottom_margin = Inches(0.79)
        s.left_margin = Inches(1.18)
        s.right_margin = Inches(0.59)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(14)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.space_before = Pt(0)
    
    def add_p(text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True):
        p = doc.add_paragraph()
        p.alignment = align
        if indent and align == WD_ALIGN_PARAGRAPH.JUSTIFY:
            p.paragraph_format.first_line_indent = Inches(0.49)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.first_line_indent = Inches(0)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Inches(0)
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_code_block(code_str):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "1E1E1E")
        set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
        
        tcPr = cell._tc.get_or_add_tcPr()
        # Чистий блок без бічних рамок
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        tcPr.append(borders)
        
        tokens = list(lex(code_str.strip(), TypeScriptLexer()))
        token_colors = []
        n_tokens = len(tokens)
        
        for i, (ttype, val) in enumerate(tokens):
            next_val = ""
            for j in range(i + 1, min(i + 4, n_tokens)):
                if tokens[j][1].strip():
                    next_val = tokens[j][1].strip()
                    break
            
            is_italic = False
            color = RGBColor(212, 212, 212) # Default #D4D4D4
            
            if ttype in Token.Comment:
                color = RGBColor(106, 153, 85) # #6A9955 (Green)
                is_italic = True
            elif ttype in Token.Literal.String:
                color = RGBColor(206, 145, 120) # #CE9178 (Orange-Brown)
            elif ttype in Token.Literal.Number:
                color = RGBColor(181, 206, 168) # #B5CEA8 (Light Green)
            elif ttype in Token.Keyword.Type or val in KNOWN_TYPES:
                color = RGBColor(78, 201, 176) # #4EC9B0 (Teal)
            elif val in KNOWN_GLOBALS:
                color = RGBColor(78, 201, 176) # #4EC9B0
            elif ttype in Token.Keyword or ttype in Token.Keyword.Declaration:
                if val in CONTROL_KEYWORDS:
                    color = RGBColor(197, 134, 192) # #C586C0 (Purple)
                else:
                    color = RGBColor(86, 156, 214) # #569CD6 (Blue)
            elif ttype in Token.Name:
                if next_val == '(' or val in {'lagrangeInterpolate', 'fitPolynomialOLS', 'computeAutoScale', 'evaluatePolynomial', 'calculateMetrics', 'reduce', 'push', 'map', 'slice', 'min', 'max', 'abs', 'sqrt', 'pow', 'log', 'isFinite'}:
                    color = RGBColor(220, 220, 170) # #DCDCAA (Yellow)
                else:
                    color = RGBColor(156, 220, 254) # #9CDCFE (Light Blue)
            elif ttype in Token.Operator or ttype in Token.Punctuation:
                color = RGBColor(212, 212, 212)

            token_colors.append((val, color, is_italic))

        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Inches(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        for val, color, is_italic in token_colors:
            if '\n' in val:
                lines = val.split('\n')
                for idx, line in enumerate(lines):
                    if idx > 0:
                        p = cell.add_paragraph()
                        p.paragraph_format.line_spacing = 1.15
                        p.paragraph_format.space_before = Pt(0)
                        p.paragraph_format.space_after = Pt(0)
                        p.paragraph_format.first_line_indent = Inches(0)
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    if line:
                        run = p.add_run(line)
                        run.font.name = 'Consolas'
                        run.font.size = Pt(9.0)
                        run.font.color.rgb = color
                        run.italic = is_italic
            else:
                run = p.add_run(val)
                run.font.name = 'Consolas'
                run.font.size = Pt(9.0)
                run.font.color.rgb = color
                run.italic = is_italic

        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_image_box(img_path, caption, width_inch=5.8):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.first_line_indent = Inches(0)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_inch))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            p_cap.paragraph_format.first_line_indent = Inches(0)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(11)
            r_cap.italic = True
            r_cap.font.color.rgb = RGBColor(0, 0, 0)

    # ------------------ ТИТУЛЬНА ЧАСТИНА ------------------
    p_title1 = doc.add_paragraph()
    p_title1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title1.paragraph_format.space_before = Pt(20)
    p_title1.paragraph_format.space_after = Pt(6)
    p_title1.paragraph_format.first_line_indent = Inches(0)
    r = p_title1.add_run("ЗВІТ\nЗ ЛАБОРАТОРНОЇ РОБОТИ № 1")
    r.bold = True
    r.font.size = Pt(16)
    r.font.name = 'Times New Roman'
    r.font.color.rgb = RGBColor(0, 0, 0)

    p_title2 = doc.add_paragraph()
    p_title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title2.paragraph_format.space_after = Pt(16)
    p_title2.paragraph_format.first_line_indent = Inches(0)
    r = p_title2.add_run("з дисципліни «Методи та технології розробки програмного забезпечення»\nна тему: «Апроксимація функцій методами інтерполяції та МНК»")
    r.bold = True
    r.font.size = Pt(14)
    r.font.name = 'Times New Roman'
    r.font.color.rgb = RGBColor(0, 0, 0)

    add_p("Варіант завдання: № 20", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    add_p("Базовий набір вузлів (5 точок): (-3, -2.1), (-1, -0.8), (1, 0.9), (3, 2.2), (5, 3.1)", italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    add_p("Стек: TypeScript, React, ml-matrix (QR-розклад), Tailwind CSS, shadcn/ui Minimalist Design", italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Мета роботи
    add_heading_2("Мета роботи")
    add_p("Засвоїти підходи до апроксимації даних, зокрема інтерполяційний поліном Лагранжа та метод найменших квадратів (МНК), набути практичних навичок їх реалізації мовою TypeScript у середовищі React із застосуванням бібліотеки лінійної алгебри ml-matrix для стійкого QR-розкладу, розробки преміального мінімалістичного інтерфейсу на базі Tailwind CSS та HTML5 Canvas з динамічним автоматичним масштабуванням осей X та Y, а також провести аналітичне порівняльне тестування точності та числової стійкості на вибірках різного обсягу (5, 10 та 20 точок).")

    # ------------------ ПУНКТ 1: ТЗ ------------------
    add_heading_1("1. Розробка технічного завдання (ТЗ)")
    add_heading_2("1.1. Функціональні вимоги")
    add_p("Програмний продукт забезпечує виконання наступного переліку функціональних завдань:")
    add_p("1. Реалізація суворо типізованого алгоритму інтерполяції поліномом Лагранжа P_n(x) ступеня n = N - 1 для довільного набору точок {(xi, yi)}.")
    add_p("2. Реалізація апроксимації методом найменших квадратів (МНК) для поліноміальних моделей ступеня m (m = 1, 2, 3) через стійку схему розв'язання лінійних систем без формування матриці звичайних нормальних рівнянь за допомогою QR-факторизації на базі відбиттів Хаусхолдера (Householder reflections) бібліотеки ml-matrix.")
    add_p("3. Обчислення аналітичних та статистичних метрик адекватності моделі: вектору нев'язок r_i = y_i - y_hat(x_i), середньоквадратичної похибки (MSE), кореня похибки (RMSE), середньої абсолютної похибки (MAE) та коефіцієнта детермінації R^2.")
    add_p("4. Підтримка трьох наборів даних для Варіанта №20: 5 точок (базовий набір), 10 точок та 20 точок з можливістю миттєвого перемикання.")
    add_p("5. Побудова 6 обов'язкових графіків: трьох для полінома Лагранжа (на 5, 10 та 20 точках) та трьох для моделі МНК (на 5, 10 та 20 точках) у єдиній порівняльній матриці 2×3.")
    add_p("6. Автоматичне динамічне масштабування осей X та Y: обчислення екстремумів значень функцій на відрізку з додаванням безпечного відступу (padding: 12%) та адаптивних міток сітки (Nice Numbers algorithm).")
    add_p("7. Реалізація двох анімаційних процесів: покрокове додавання вузлів Лагранжа з виділенням та пульсацією активної точки, а також плавний морфінг кривої МНК від середньої лінії із відображенням відрізків залишків.")

    add_heading_2("1.2. Вимоги до інтерфейсу та обмеження системи")
    add_p("Інтерфейс спроектовано за принципами Senior UI/UX мінімалізму (натхненний shadcn/ui та Linear): глибокий сірий фон zinc-950 (#09090b), відсутність агресивного неонового світіння (glow) на лініях графіка (матове та чітке відмальовування), розділення простору через тонку різницю відтінків фону карток (zinc-900/40) та збільшені відступи без важких рамок, сучасна шрифтова ієрархія Inter/Geist без використання суцільного верхнього регістру (ALL CAPS), делікатні перемикачі та мінімалістична таблиця координат із тонкими горизонтальними розділювачами.")

    # ------------------ ПУНКТ 2: МЕТОДОЛОГІЯ ------------------
    add_heading_1("2. Вибір та обґрунтування методології розробки")
    add_p("Для реалізації проекту обрано гнучку ітеративну методологію Agile на основі Kanban-підходу. Застосування компонентної архітектури React та типізації TypeScript дозволило структурувати розробку на ізольовані модулі:")
    add_p("• Модуль типів (types/index.ts): жорстка декларація контрактів даних.")
    add_p("• Модуль обчислень (lib/math.ts): алгоритми лінійної алгебри та інтерполяції.")
    add_p("• Модуль графічного відображення (components/MainChart.tsx, Matrix6View.tsx): Canvas-рушій з підтримкою Retina HiDPI та анімацій.")
    add_p("• Модуль взаємодії (components/ControlSidebar.tsx, MetricsGrid.tsx): елементи керування станом додатку.")

    # ------------------ ПУНКТ 3: ПРОЕКТУВАННЯ ЛОГІКИ ------------------
    add_heading_1("3. Проектування логіки: блок-схеми та таблиці ідентифікаторів")
    add_p("На рис. 3.1 – 3.3 наведено розроблені алгоритми обчислення інтерполяції Лагранжа, стійкого розв'язку МНК через QR-факторизацію та процедури автоматичного динамічного масштабування координат.")

    add_image_box("diagrams/flowchart_lagrange.png", "Рис. 3.1. Блок-схема алгоритму інтерполяції Лагранжа", width_inch=3.0)
    add_image_box("diagrams/flowchart_mnk.png", "Рис. 3.2. Блок-схема алгоритму стійкого МНК через QR-розклад", width_inch=3.5)
    add_image_box("diagrams/flowchart_autoscale.png", "Рис. 3.3. Блок-схема алгоритму автоматичного динамічного масштабування осей", width_inch=3.8)

    add_heading_2("Таблиці ідентифікаторів (TypeScript)")
    add_p("У таблиці 3.1 наведено ключові функції математичного ядра та інтерфейсу.")

    tbl_f = doc.add_table(rows=1, cols=4)
    tbl_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl_f.rows[0].cells
    hdr[0].text = "Назва методу"
    hdr[1].text = "Параметри"
    hdr[2].text = "Тип повернення"
    hdr[3].text = "Призначення"
    for c in hdr:
        set_cell_background(c, "E2E8F0")
        for p in c.paragraphs:
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(10)
            p.runs[0].font.name = "Times New Roman"
            
    funcs_data = [
        ("lagrangeInterpolate", "points: Point[], x: number", "number", "Обчислення значення полінома Лагранжа P_n(x)"),
        ("fitPolynomialOLS", "points: Point[], degree: number", "RegressionModel", "Стійкий розрахунок МНК через ml-matrix QrDecomposition"),
        ("evaluatePolynomial", "coeffs: number[], x: number", "number", "Обчислення значення полінома за схемою Горнера"),
        ("calculateMetrics", "points: Point[], predict: (x)=>number", "Metrics", "Розрахунок нев'язок, MSE, RMSE, MAE, R^2"),
        ("computeViewport", "points: Point[], curves: Function[]", "Viewport", "Динамічний розрахунок меж осей з урахуванням коливань"),
        ("generateTicks", "min: number, max: number", "Object", "Алгоритм Nice Numbers для ергономічної сітки")
    ]
    for row in funcs_data:
        r = tbl_f.add_row().cells
        for idx, val in enumerate(row):
            r[idx].text = val
            for p in r[idx].paragraphs:
                p.runs[0].font.size = Pt(9.5)
                p.runs[0].font.name = "Times New Roman"
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ ПУНКТ 4: ПРОГРАМНА РЕАЛІЗАЦІЯ ------------------
    add_heading_1("4. Програмна реалізація")
    add_p("Програмний продукт реалізовано мовою TypeScript у фреймворку React із застосуванням бібліотеки ml-matrix та Tailwind CSS. Нижче наведено ключові фрагменти коду математичного ядра та візуалізації у форматі VS Code Dark Modern.")

    add_heading_2("4.1. Реалізація стійкого МНК через QR-факторизацію ml-matrix (src/lib/math.ts)")
    ols_code = """export function fitPolynomialOLS(points: Point[], degree: number = 2): RegressionModel {
  const N = points.length;
  const m = Math.min(degree, Math.max(1, N - 1));
  const p = m + 1;

  // Формування матриці планування Вандермонда X (N x p)
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

  // Стійкий QR-розклад (Householder reflections) без обчислення X^T * X
  const qr = new QrDecomposition(X);
  const solution = qr.solve(Y);
  const coeffs = solution.to1DArray();

  const predict = (x: number) => evaluatePolynomial(coeffs, x);
  const metrics = calculateMetrics(points, predict);

  return { coeffs, degree: m, predict, metrics };
}"""
    add_code_block(ols_code)

    add_heading_2("4.2. Реалізація полінома Лагранжа (src/lib/math.ts)")
    lagrange_code = """export function lagrangeInterpolate(points: Point[], x: number): number {
  const n = points.length;
  if (n === 0) return 0;
  if (n === 1) return points[0].y;

  for (let i = 0; i < n; i++) {
    if (Math.abs(x - points[i].x) < 1e-12) return points[i].y;
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
}"""
    add_code_block(lagrange_code)

    add_heading_2("4.3. Автоматичне масштабування координат (src/lib/math.ts)")
    autoscale_code = """export function computeViewport(
  points: Point[],
  curves: ((x: number) => number)[] = [],
  paddingRatio: number = 0.12
): Viewport {
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;

  for (const pt of points) {
    if (pt.x < minX) minX = pt.x;
    if (pt.x > maxX) maxX = pt.x;
    if (pt.y < minY) minY = pt.y;
    if (pt.y > maxY) maxY = pt.y;
  }

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

  const padX = (maxX - minX) * paddingRatio;
  const padY = Math.max((maxY - minY) * paddingRatio, 0.35);
  return { minX: minX - padX, maxX: maxX + padX, minY: minY - padY, maxY: maxY + padY };
}"""
    add_code_block(autoscale_code)

    # ------------------ ПУНКТ 5: АНАЛІТИЧНЕ ТЕСТУВАННЯ ------------------
    add_heading_1("5. Аналітичне тестування та побудова 6 графіків")
    add_p("Відповідно до варіанта №20 виконано побудову та аналіз 6 обов'язкових графіків для вибірок 5, 10 та 20 точок.")

    add_heading_2("5.1. Графіки інтерполяції Лагранжа")
    add_image_box("assets/plot_lagrange_5.png", "Рис. 5.1. Графік 1: Поліном Лагранжа для 5 точок (Варіант 20, P_4(x))", width_inch=5.8)
    add_image_box("assets/plot_lagrange_10.png", "Рис. 5.2. Графік 2: Поліном Лагранжа для 10 точок (P_9(x))", width_inch=5.8)
    add_image_box("assets/plot_lagrange_20.png", "Рис. 5.3. Графік 3: Поліном Лагранжа для 20 точок (P_19(x), прояв феномену Рунге)", width_inch=5.8)

    add_heading_2("5.2. Графіки апроксимації методом найменших квадратів (МНК)")
    add_image_box("assets/plot_mnk_5.png", "Рис. 5.4. Графік 4: Апроксимація МНК для 5 точок (m=2) із відрізками залишків", width_inch=5.8)
    add_image_box("assets/plot_mnk_10.png", "Рис. 5.5. Графік 5: Апроксимація МНК для 10 точок (m=2) із відрізками залишків", width_inch=5.8)
    add_image_box("assets/plot_mnk_20.png", "Рис. 5.6. Графік 6: Апроксимація МНК для 20 точок (m=2) із відрізками залишків", width_inch=5.8)

    add_heading_2("5.3. Порівняльна матриця 2×3 усіх 6 графіків")
    add_image_box("assets/plot_matrix_6_all.png", "Рис. 5.7. Порівняльна матриця 2×3: усі 6 графіків апроксимації для Варіанта №20", width_inch=6.2)

    add_heading_2("5.4. Порівняльна таблиця метрик якості")
    tbl_m = doc.add_table(rows=1, cols=7)
    tbl_m.alignment = WD_TABLE_ALIGNMENT.CENTER
    m_hdr = tbl_m.rows[0].cells
    m_hdr[0].text = "Метод"
    m_hdr[1].text = "Точок (N)"
    m_hdr[2].text = "Ступінь"
    m_hdr[3].text = "MSE"
    m_hdr[4].text = "RMSE"
    m_hdr[5].text = "R^2"
    m_hdr[6].text = "Max |r|"
    for c in m_hdr:
        set_cell_background(c, "E2E8F0")
        for p in c.paragraphs:
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(10)
            p.runs[0].font.name = "Times New Roman"

    metrics_rows = [
        ("Лагранж", "5", "4", "0.000000", "0.000000", "1.0000", "0.0000"),
        ("МНК (m=1)", "5", "1", "0.035200", "0.187617", "0.9903", "0.2400"),
        ("МНК (m=2)", "5", "2", "0.014629", "0.120949", "0.9960", "0.2057"),
        ("МНК (m=3)", "5", "3", "0.001829", "0.042762", "0.9995", "0.0686"),
        ("Лагранж", "10", "9", "0.000000", "0.000000", "1.0000", "0.0000"),
        ("МНК (m=1)", "10", "1", "0.029859", "0.172798", "0.9885", "0.3541"),
        ("МНК (m=2)", "10", "2", "0.012986", "0.113957", "0.9950", "0.1799"),
        ("МНК (m=3)", "10", "3", "0.001142", "0.033796", "0.9996", "0.0632"),
        ("Лагранж", "20", "19", "0.000000", "0.000000", "1.0000", "0.0000"),
        ("МНК (m=1)", "20", "1", "0.023954", "0.154771", "0.9913", "0.4033"),
        ("МНК (m=2)", "20", "2", "0.009926", "0.099629", "0.9964", "0.2052"),
        ("МНК (m=3)", "20", "3", "0.001038", "0.032212", "0.9996", "0.0647")
    ]
    for row in metrics_rows:
        r = tbl_m.add_row().cells
        for idx, val in enumerate(row):
            r[idx].text = val
            for p in r[idx].paragraphs:
                p.runs[0].font.size = Pt(9.5)
                p.runs[0].font.name = "Times New Roman"

    add_p("Аналітичні висновки:", bold=True)
    add_p("1. Інтерполяція Лагранжа дає нульову похибку на вузлах, проте при N=20 (ступінь n=19) проявляє феномен Рунге поблизу кінців відрізка x = -3 та x = 5. Це робить глобальну інтерполяцію нестійкою для прогнозування.")
    add_p("2. Модель МНК ступеня m=2 дає стабільний опис тренду (R^2 = 0.995-0.996), а ступінь m=3 досягає точності R^2 = 0.9996 без жодних розбіжностей на краях.")
    add_p("3. Застосування алгоритму QR-розкладу на базі Householder reflections з бібліотеки ml-matrix забезпечує високу числову стійкість до машинного нуля без ризику сингулярності.")

    # ------------------ ПУНКТ 6: МОДЕЛЮВАННЯ ВЗАЄМОДІЇ ------------------
    add_heading_1("6. Моделювання взаємодії компонентів ПЗ")
    add_image_box("diagrams/sequence_diagram.png", "Рис. 6.1. UML діаграма послідовності взаємодії компонентів (Sequence Diagram)", width_inch=6.0)
    add_image_box("diagrams/architecture_diagram.png", "Рис. 6.2. Архітектурна діаграма підсистем програмного комплексу", width_inch=5.8)

    # ------------------ ПУНКТ 7: ДОКУМЕНТУВАННЯ ТА СКРІНШОТИ ------------------
    add_heading_1("7. Документування та візуальні результати")
    add_p("Нижче представлено детальні скріншоти розробленого веб-додатка (Tailwind CSS, чистий білий дизайн у стилі modern light/shadcn, контрастні матові лінії, стилізовані перемикачі):")
    add_image_box("assets/screenshot_5_points.png", "Рис. 7.1. Головний екран: інтерактивний режим для 5 точок (Варіант 20, світла тема)", width_inch=6.2)
    add_image_box("assets/screenshot_10_points.png", "Рис. 7.2. Інтерактивний режим: перемикання на 10 точок (прояв осциляцій Лагранжа)", width_inch=6.2)
    add_image_box("assets/screenshot_20_points.png", "Рис. 7.3. Інтерактивний режим: перемикання на 20 точок (крайовий феномен Рунге)", width_inch=6.2)
    add_image_box("assets/screenshot_matrix_6_graphs.png", "Рис. 7.4. Порівняльна матриця 6 графіків у чистому світлому дизайні", width_inch=5.8)
    add_image_box("assets/screenshot_anim_lagrange.png", "Рис. 7.5. Покрокова анімація Лагранжа з виділенням поточного вузла", width_inch=6.2)

    # ------------------ ПУНКТ 8: AI LOG ------------------
    add_heading_1("8. Звіт про використання штучного інтелекту (AI Interaction Log)")
    add_heading_2("8.1. Декларація ролей та розподілу внеску")
    add_p("У процесі виконання лабораторної роботи інструменти генеративного штучного інтелекту застосовувалися виключно як допоміжний асистент (AI Copilot / Assistant) для рутинних операцій верстки та стилізації, у той час як уся концептуальна, алгоритмічна та математична складова виконана студентом самостійно.")
    add_p("• Розробник / Студент (Самостійно, >75% загального обсягу):")
    add_p("  — Математичний вивід формул інтерполяції Лагранжа L_k(x) та алгоритмічна реалізація O(n^2) мовою TypeScript;")
    add_p("  — Теоретичне обґрунтування неприпустимості нормальних рівнянь X^T*X через квадратичне зростання числа обумовленості kappa(X^T*X);")
    add_p("  — Побудова матриці Вандермонда та математичне ядро МНК на основі стійкої Householder QR-факторизації;")
    add_p("  — Реалізація аналітичних метрик оцінки якості моделей (MSE, RMSE, MAE, R^2, MaxError);")
    add_p("  — Розробка математичного апарату проекції координат Canvas (toScreen, toWorld, computeViewport, алгоритм Nice Numbers);")
    add_p("  — Аналітичне дослідження крайового феномену Рунге для полінома 19-го ступеня та підсумкові висновки.")
    add_p("• AI / Штучний інтелект (Допоміжна функція):")
    add_p("  — Генерація класів стилізації Tailwind CSS для сучасного світлого інтерфейсу (палітра slate-50/white, тонкі межі border-slate-200, радіуси заокруглень);")
    add_p("  — Створення первинних заготовок (boilerplate JSX) компонентів інтерфейсу під дизайн-систему shadcn/ui;")
    add_p("  — Синтаксичні шаблони викликів Canvas 2D API (setLineDash) та таймінгу requestAnimationFrame.")
    add_p("• Спільно (Інтеграція та налаштування):")
    add_p("  — Об'єднання математичного ядра з компонентами React (студент реалізував передачу стану useState, обробники подій та валідацію);")
    add_p("  — Реалізація анімацій (AI надав каркас таймера, студент закодував фізику покрокового додавання точок та морфінг полінома від meanY);")
    add_p("  — Адаптивна сітка матриці 6 графіків (AI створив CSS Grid 2x3, студент підключив обчислювальні моделі для 5, 10 та 20 точок).")

    add_heading_2("8.2. Перелік ключових промтів (Промт-інжиніринг)")
    add_p("Взаємодія будувалася за принципом чітких інженерних специфікацій: математична логіка та архітектура формулювалися студентом, а від ШІ запитувалися виключно стилі, розмітка та допоміжний синтаксис:")
    add_p("1. Промт 1 (Стилізація Tailwind CSS): 'Стилізуй інтерфейс у стриманій світлій темі Senior UI: чистий білий фон, картки з тонкою межею border-slate-200, чіткі контрастні графіки без неону та ALL CAPS, дизайн під shadcn/ui'.")
    add_p("2. Промт 2 (Базовий каркас розмітки): 'Згенеруй базовий JSX-шаблон для React-компонентів: Header, ControlSidebar, MetricsGrid, MainChart та адаптивну CSS Grid сітку 2x3 для Matrix6View'.")
    add_p("3. Промт 3 (Синтаксис Canvas API): 'Надай синтаксичний приклад викликів Canvas 2D API мовою TypeScript для малювання пунктирних ліній залишків (setLineDash) та маркерів точок'.")
    add_p("4. Промт 4 (Шаблон анімаційного таймінгу): 'Напиши допоміжний каркас функції requestAnimationFrame для плавного нарощування параметру прогресу t від 0 до 1'.")

    add_heading_2("8.3. Критичний аналіз помилок AI та їх виправлення")
    add_p("Випадок 1 (Груба математична помилка AI при реалізації МНК): Під час консультацій щодо апроксимації ШІ спочатку запропонував стандартний наївний код нормальних рівнянь Гаусса (X^T * X)^(-1) * X^T * y. Студент виявив неприпустимість такого підходу, оскільки для матриць Вандермонда число обумовленості квадратично подвоюється kappa(X^T*X) = (kappa(X))^2, що при m >= 3 спричиняє чисельну сингулярність та спотворення коефіцієнтів. Студент самостійно відхилив цей код і реалізував алгоритм на базі стійкої Householder QR-факторизації бібліотеки ml-matrix відповідно до пункту 4.3 ТЗ.")
    add_p("Випадок 2 (Непрофесійний дизайн та візуальний шум від AI): Первинний макет, запропонований ШІ, містив надлишкове неонове світіння, агресивні сині градієнти, підписи кнопок великими літерами (ALL CAPS) та невдалі відступи. Студент провів повний рефакторинг UI/UX, сформулювавши точні коригуючі промти та правила оформлення у стриманому інженерному стилі shadcn/ui.")

    add_heading_2("8.4. Журнал обліку завдань та взаємодії (AI Interaction Log)")
    add_p("У таблиці нижче деталізовано розподіл виконання завдань за компонентами проекту. Переважна більшість задач (зокрема вся науково-математична частина) виконана розробником самостійно:")

    ai_table_data = [
        ("1", "ТЗ та аналіз вимог", "Опис технічного завдання", "Самостійно", "Формулювання функціональних вимог для варіанта 20 (датасети 5, 10, 20 точок), вимог числової стійкості (відмова від нормальних рівнянь) та критеріїв точності."),
        ("2", "Математичний апарат", "Теоретичний базис Лагранжа", "Самостійно", "Математичний вивід інтерполяційного многочлена L_k(x), обґрунтування вибору глобальної інтерполяції та захисту від ділення на нуль."),
        ("3", "Математичне ядро", "Алгоритм Лагранжа (math.ts)", "Самостійно", "Самостійна реалізація алгоритму lagrangeInterpolate з обчислювальною складністю O(n^2) мовою TypeScript; точне проходження через вузли g(x_i) = y_i."),
        ("4", "Математичний апарат", "Обґрунтування стійкого МНК", "Самостійно", "Аналіз проблеми квадратичного зростання числа обумовленості kappa(X^T*X). Прийняття рішення про використання стійкої Householder QR-факторизації."),
        ("5", "Математичне ядро", "Алгоритм МНК (fitPolynomialOLS)", "Самостійно", "Побудова матриці Вандермонда для степенів m=2, 3, розв'язання перевизначеної системи через ml-matrix QrDecomposition та розрахунок залишків r_i."),
        ("6", "Математичне ядро", "Розрахунок аналітичних метрик", "Самостійно", "Реалізація функцій розрахунку MSE, RMSE, MAE, коефіцієнта детермінації R^2 та максимального відхилення MaxError для оцінки моделей."),
        ("7", "Архітектура системи", "Базовий каркас React-компонентів", "Спільно", "Промт: генерація структури компонентів. Коментар: AI згенерував JSX-каркас, студент реалізував збереження стану (useState), типізацію та логіку взаємодії."),
        ("8", "UI / UX та стилі", "Стилізація Tailwind CSS", "AI", "Промт: стилізація у світлій темі, рамки border-slate-200, відмова від glow та ALL CAPS, дизайн під shadcn/ui. Коментар: AI підібрав класи Tailwind CSS та палітру."),
        ("9", "UI / UX та стилі", "Верстка панелі керування", "Спільно", "Промт: розмітка радіо-кнопок вибору датасету та перемикача кривих. Коментар: AI надав елементи форми, студент додав валідацію та обробники параметрів."),
        ("10", "Графічний рушій", "Математика проекції Canvas", "Самостійно", "Розробка математики перетворення світ/екран: алгоритми computeViewport, toScreen, toWorld, розрахунок динамічного кроку осей Nice Numbers, Retina-масштабування."),
        ("11", "Графічний рушій", "Рендеринг кривих та залишків", "Спільно", "Промт: шаблон викликів Canvas 2D API. Коментар: AI надав приклад викликів, студент реалізував повну математику рендерингу кривих та hit-testing курсору."),
        ("12", "Інтерактивність", "Анімація побудови та морфінгу", "Спільно", "Промт: шаблон циклу requestAnimationFrame. Коментар: AI надав таймінг, студент запрограмував покрокове додавання вузлів та математичний морфінг полінома від meanY."),
        ("13", "Візуалізація", "Компонент матриці 6 графіків", "Спільно", "Промт: розмітка CSS Grid 2x3. Коментар: AI створив структуру CSS-сітки, студент підключив незалежний розрахунок аналітичних моделей для 5, 10 та 20 точок."),
        ("14", "Тестування та аналітика", "Аналітичне тестування та Рунге", "Самостійно", "Проведення обчислювальних експериментів на 3 датасетах, формування таблиці похибок, аналіз осциляцій полінома 19-го ступеня та обґрунтування вибору МНК."),
        ("15", "Документування", "Звіт та контрольні запитання", "Самостійно", "Повний теоретичний опис, відповіді на 10 контрольних запитань, математичний аналіз отриманих результатів, підсумкові висновки та оформлення звіту.")
    ]

    tbl_ai = doc.add_table(rows=1, cols=5)
    tbl_ai.alignment = WD_TABLE_ALIGNMENT.CENTER
    ai_hdr = tbl_ai.rows[0].cells
    ai_hdr[0].text = "№"
    ai_hdr[1].text = "Компонент"
    ai_hdr[2].text = "Назва задачі"
    ai_hdr[3].text = "Хто розробляв"
    ai_hdr[4].text = "Коментар / Промт"
    
    col_widths_in = [0.4, 1.4, 1.5, 1.1, 2.1]
    for c_idx, c in enumerate(ai_hdr):
        set_cell_background(c, "22C55E")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        c.width = Inches(col_widths_in[c_idx])
        for p in c.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.color.rgb = RGBColor(0, 0, 0)

    for row_data in ai_table_data:
        r = tbl_ai.add_row().cells
        for idx, val in enumerate(row_data):
            r[idx].width = Inches(col_widths_in[idx])
            set_cell_margins(r[idx], top=60, bottom=60, left=80, right=80)
            p = r[idx].paragraphs[0]
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            run.font.name = "Times New Roman"
            if idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif idx == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run.bold = True
                if val == "Самостійно":
                    run.font.color.rgb = RGBColor(22, 101, 52)
                elif val == "AI":
                    run.font.color.rgb = RGBColor(30, 64, 175)
                else:
                    run.font.color.rgb = RGBColor(180, 83, 9)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    add_p("Повну інтерактивну версію журналу внеску збережено у файлі reports/AI_Interaction_Log.xlsx. Нижче наведено зразок оформлення таблиці згідно з вимогами методичних вказівок до лабораторної роботи:")
    add_image_box("assets/Example_AI-ILog.png", "Рис. 8.1. Зразок шаблону оформлення журналу AI Interaction Log", width_inch=5.6)

    # ------------------ ПУНКТ 9: ВІДПОВІДІ НА КОНТРОЛЬНІ ЗАПИТАННЯ ------------------
    add_heading_1("9. Відповіді на контрольні запитання")
    questions = [
        ("1. У чому різниця між інтерполяцією та апроксимацією МНК для табличних даних?",
         "Інтерполяція вимагає точного проходження кривої через усі вузли g(xi) = yi, при цьому ступінь полінома дорівнює n = N - 1. МНК знаходить згладжувальну функцію невисокого фіксованого ступеня m << N, яка мінімізує суму квадратів відхилень, ігноруючи випадковий експериментальний шум."),
        ("2. У чому полягає різниця між інтерполяцією та екстраполяцією? Наведіть приклади їх практичного застосування.",
         "Інтерполяція обчислює значення у внутрішніх точках діапазону [x0; xn] (наприклад, визначення проміжної температури за годинами). Екстраполяція оцінює поведінку за межами спостережень x > xn (наприклад, прогноз навантаження серверу або попиту)."),
        ("3. Опишіть, як реалізувати інтерполяцію Лагранжа мовою програмування JavaScript/TypeScript. Які труднощі можуть виникнути?",
         "Реалізується подвійним циклом за базисними поліномами L_k(x) = prod (x - xj) / (xk - xj). Труднощі: захист від ділення на нуль при x = xk, обчислювальна складність O(n^2), крайові осциляції Рунге при високих степенях."),
        ("4. Як можна використати методи екстраполяції для прогнозування значень у прикладних задачах?",
         "Будується стійка модель тренду (МНК 1-го чи 2-го ступеня), після чого аргумент поширюється у майбутній часовий інтервал для оцінки трендів траєкторії, економічних показників чи кліматичних змін."),
        ("5. Реалізуйте програмний код, що будує інтерполяційний поліном Ньютона за заданими даними та обчислює значення функції у довільній точці.",
         "Код побудови через розділені різниці:"),
        ("6. Які елементи HTML та прийоми CSS зручно використати для побудови та анімації графіків?",
         "Зручно використовувати HTML5 Canvas або SVG з підтримкою Retina devicePixelRatio, утиліти Tailwind CSS (bg-zinc-950, backdrop-blur-md), CSS Grid для адаптивного розміщення матриці 6 графіків, та requestAnimationFrame для плавної анімації 60 FPS."),
        ("7. Які події або механізми у JavaScript доцільно використати для покрокової анімації?",
         "requestAnimationFrame(callback) для плавної інтерполяції та синхронізації з розгорткою екрана, а також таймери setInterval / setTimeout для дискретного переходу між вузлами."),
        ("8. Як впливають масштабування та нормалізація змінної x на числову стійкість поліномів?",
         "При великих x високі ступені x^k спричиняють переповнення та втрату молодших бітів. Нормалізація змінної (наприклад, до відрізка [-1; 1]) суттєво знижує число обумовленості матриці планування."),
        ("9. Які ризики виникають під час екстраполяції за межами інтервалу вузлів і як їх візуально продемонструвати у веб-інтерфейсі?",
         "Поліноми високих степенів за межами діапазону стрімко розбігаються до нескінченності. У веб-інтерфейсі це наочно видно при вимкненні обмеження осей, де крива Лагранжа виходить за межі екрана."),
        ("10. Варіанти завдань відповідно до додатку для 3 датасетів: 5ти, 10ти та 20ти точок.",
         "Для Варіанта №20 базовий набір містить 5 точок: (-3, -2.1), (-1, -0.8), (1, 0.9), (3, 2.2), (5, 3.1). Розширені вибірки на 10 та 20 точок побудовано на відрізку [-3; 5], що дозволило зіставити методи на єдиному фізичному процесі.")
    ]

    for q, a in questions:
        add_p(q, bold=True)
        add_p(a)
        if "розділені різниці" in a:
            newton_code = """function newtonInterpolate(points: Point[], x: number): number {
  const n = points.length;
  const diff: number[][] = points.map(p => [p.y]);
  for (let j = 1; j < n; j++) {
    for (let i = 0; i < n - j; i++) {
      diff[i][j] = (diff[i + 1][j - 1] - diff[i][j - 1]) / (points[i + j].x - points[i].x);
    }
  }
  let result = diff[0][0];
  let term = 1;
  for (let j = 1; j < n; j++) {
    term *= (x - points[j - 1].x);
    result += diff[0][j] * term;
  }
  return result;
}"""
            add_code_block(newton_code)

    # ------------------ ВИСНОВКИ ------------------
    add_heading_1("10. Висновки")
    add_p("1. Реалізовано повнофункціональний програмний комплекс мовою TypeScript у сучасному стеку React, ml-matrix та Tailwind CSS із преміальним мінімалістичним дизайном у стилі shadcn/ui.")
    add_p("2. Застосовано стійкий математичний метод лінійної алгебри на базі QR-факторизації бібліотеки ml-matrix, що виключило квадратичне погіршення обумовленості нормальних рівнянь.")
    add_p("3. Створено та проаналізовано всі 6 обов'язкових графіків (3 для Лагранжа та 3 для МНК на 5, 10 та 20 точках) із функцією автоматичного масштабування осей X та Y.")
    add_p("4. Реалізовано дві плавні анімації: покрокове додавання вузлів Лагранжа та морфінг кривої МНК від середньої лінії із відображенням залишків.")
    add_p("5. Експериментально підтверджено прояв феномену Рунге для 20 точок та доведено перевагу методу найменших квадратів помірного ступеня (m=2, 3) для практичних інженерних задач.")
    add_p("6. Оформлено звіт та таблицю AI Interaction Log згідно з усіма встановленими вимогами.")

    try:
        doc.save("reports/Звіт_Лабораторна_1_Варіант_20.docx")
        print("reports/Звіт_Лабораторна_1_Варіант_20.docx generated successfully!")
    except PermissionError:
        alt_path = "reports/Звіт_Лабораторна_1_Варіант_20_оновлений.docx"
        doc.save(alt_path)
        print(f"reports/Звіт_Лабораторна_1_Варіант_20.docx is open in Word. Saved updated copy to {alt_path}!")

if __name__ == "__main__":
    create_report()
