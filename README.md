# 🧩 Intelligent Sudoku Solver and Analyzer

Yapay zeka teknikleri ile geliştirilmiş, modüler yapıya sahip Sudoku çözücü ve analizör.

---

## 📁 Proje Yapısı

```
Sudoku-Solver/
├── main.py                           # Ana giriş noktası
├── README.md                         # Dokümantasyon
└── src/                              # Kaynak kodları
    ├── __init__.py
    ├── core/                         # Temel bileşenler
    │   ├── __init__.py
    │   ├── board.py                  # SudokuBoard sınıfı
    │   ├── generator.py              # PuzzleGenerator
    │   └── metrics.py                # AlgorithmMetrics
    ├── solvers/                      # Çözüm algoritmaları
    │   ├── __init__.py
    │   ├── base.py                   # BaseSolver, StepType, SolveStep
    │   ├── constraint_propagation.py # Kısıt yayılımı
    │   ├── ac3.py                    # AC-3 algoritması
    │   ├── backtracking.py           # Backtracking (DFS)
    │   └── iterative_backtracking.py # Stack tabanlı backtracking
    └── ui/                           # Kullanıcı arayüzü
        ├── __init__.py
        └── animation.py              # Animasyon kontrolcüsü
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.7+
- tkinter (Python ile birlikte gelir)

### Çalıştırma
```bash
python main.py
```

---

## 🧠 Algoritmalar

### 1. Constraint Propagation (Kısıt Yayılımı)
- Domain'leri mantıksal eleme ile daraltır
- Tek değerli hücreleri otomatik doldurur
- Propagation ile komşu domain'leri günceller

```python
from src.solvers import ConstraintPropagationSolver
solver = ConstraintPropagationSolver()
result, metrics = solver.solve(board)
```

### 2. AC-3 (Arc Consistency Algorithm 3)
- CSP (Constraint Satisfaction Problem) olarak modeller
- İkili tutarlılık (arc consistency) sağlar
- Domain'lerden tutarsız değerleri çıkarır

```python
from src.solvers import AC3Solver
solver = AC3Solver()
result, metrics = solver.solve(board)
```

### 3. Backtracking (Geri İzleme)
- DFS (Derinlik Öncelikli Arama) kullanır
- MRV (Minimum Remaining Values) heuristic
- Çıkmaz sokakta geri döner

```python
from src.solvers import BacktrackingSolver
solver = BacktrackingSolver(use_mrv=True)
result, metrics = solver.solve(board)
```

### 4. Iterative Backtracking
- Recursion yerine stack kullanır
- Büyük bulmacalar (16x16+) için RecursionError önler

```python
from src.solvers import IterativeBacktrackingSolver
solver = IterativeBacktrackingSolver()
result, metrics = solver.solve(board)
```

---

## 📊 Performans Karşılaştırması

| Algoritma | Easy (nodes) | Medium (nodes) | Hard (nodes) |
|-----------|-------------|---------------|-------------|
| Constraint Propagation | 1-5 | 5-15 | 10-50 |
| AC-3 | 1-5 | 5-15 | 10-50 |
| Backtracking | 30-50 | 50-100 | 50-200 |
| Iterative Backtracking | 100-300 | 500-5000 | 100-500 |

### Metrikler
- **Runtime**: Çözüm süresi (saniye)
- **Nodes Visited**: Ziyaret edilen durum sayısı
- **Backtrack Count**: Geri dönüş sayısı
- **Domain Reductions**: Domain'den çıkarılan değer sayısı

---

## 🎮 Kullanım

### Programatik Kullanım
```python
from src.core.board import SudokuBoard
from src.core.generator import PuzzleGenerator
from src.solvers import BacktrackingSolver

# Puzzle oluştur
gen = PuzzleGenerator()
puzzle = gen.generate(9, "medium")

# Çöz
solver = BacktrackingSolver()
result, metrics = solver.solve(puzzle)

print(f"Çözüldü: {result.is_solved()}")
print(f"Metrics: {metrics}")
```

### Adım Adım Animasyon
```python
solver = BacktrackingSolver()
for step in solver.solve_with_steps(puzzle):
    print(f"{step.step_type.value}: ({step.row+1}, {step.col+1}) = {step.value}")
    if step.step_type.value == "solved":
        break
```

---

## 🔧 Teknik Detaylar

### Board Doğrulama
Her hamle üç kurala göre kontrol edilir:
1. **Satır**: Aynı satırda tekrar yok
2. **Sütun**: Aynı sütunda tekrar yok
3. **Kutu**: Aynı 3x3 kutuda tekrar yok

### Zorluk Seviyeleri
| Seviye | Dolu Hücre Oranı |
|--------|-----------------|
| Easy | %50 |
| Medium | %35 |
| Hard | %25 |

---

## 👥 Yazarlar

- Berfin Duru ALKAN - 202228005
- Şahin ERŞAN - 202128002
- Özgün SOYKÖK - 202228043
- İsmail DOĞAN - 202128045

**SENG 465** - Artificial Intelligence in Game Programming
