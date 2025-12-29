# 🧩 Intelligent Sudoku Solver and Analyzer

Yapay zeka teknikleri ile geliştirilmiş, çoklu çözüm algoritmaları ve interaktif oynanış özelliklerine sahip bir Sudoku oyunu.

---

## 📋 İçindekiler

1. [Proje Hakkında](#proje-hakkında)
2. [Özellikler](#özellikler)
3. [Kurulum](#kurulum)
4. [Nasıl Çalıştırılır](#nasıl-çalıştırılır)
5. [Nasıl Oynanır](#nasıl-oynanır)
6. [Algoritmalar](#algoritmalar)
7. [Performans Karşılaştırması](#performans-karşılaştırması)
8. [Dosya Yapısı](#dosya-yapısı)
9. [Teknik Detaylar](#teknik-detaylar)
10. [Sorun Giderme](#sorun-giderme)
11. [Yazarlar](#yazarlar)

---

## 📖 Proje Hakkında

Bu proje, SENG 465 - Artificial Intelligence in Game Programming dersi için geliştirilmiş bir Sudoku oyunudur. Oyuncu bulmacaları manuel olarak çözebilir veya AI algoritmalarından yardım isteyebilir. Sistem birden fazla zorluk seviyesi ve algoritma performans karşılaştırma özellikleri içerir.

### Temel Amaçlar
- Constraint Satisfaction Problem (CSP) çözümü gösterimi
- Üç farklı AI algoritması karşılaştırması
- Adım adım algoritma görselleştirmesi
- İnteraktif oyun deneyimi

---

## ✨ Özellikler

### Temel Fonksiyonlar
| Özellik | Açıklama |
|---------|----------|
| 🎮 **İnteraktif Oynanış** | Gerçek zamanlı doğrulama ile manuel bulmaca çözme |
| 📐 **Çoklu Board Boyutu** | 3x3 mini-Sudoku ve 9x9 standart Sudoku |
| 🎯 **Zorluk Seviyeleri** | Easy, Medium, Hard |
| 🔴 **Hata Vurgulama** | Çakışan hücreler kırmızı ile gösterilir |
| 🎬 **Adım Adım Animasyon** | Algoritmanın çözüm sürecini izleme |
| 📊 **Algoritma Karşılaştırma** | Üç algoritmanın performans karşılaştırması |
| 💡 **İpucu Sistemi** | Seçili algoritma ile ipucu alma |
| ↶ **Geri Al/İleri Al** | Hamle geçmişi |

### AI Algoritmaları
1. **Constraint Propagation** - Domain daraltma ile mantıksal eleme
2. **AC-3** - Arc consistency ile ikili tutarlılık
3. **Backtracking** - MRV heuristic ile DFS
4. **Iterative Backtracking** - Büyük bulmacalar için stack tabanlı

---

## 🚀 Kurulum

### Gereksinimler
- **Python 3.7 veya üzeri**
- **tkinter** (Python ile birlikte gelir)
- İşletim Sistemi: Windows / Linux / Mac

### Python Kontrolü

```bash
# Windows
python --version

# Linux/Mac
python3 --version
```

Python yüklü değilse: https://www.python.org/downloads/

### Ek Paket Gerekmiyor!
Bu proje sadece Python standart kütüphanesini kullanır. Ek kurulum gerekmez.

---

## ▶️ Nasıl Çalıştırılır

### Windows
```bash
cd C:\path\to\Sudoku-Solver
python sudoku_game.py
```

### Linux/Mac
```bash
cd /path/to/Sudoku-Solver
python3 sudoku_game.py
```

### Test Çalıştırma
```bash
python test_game.py
```

---

## 🎮 Nasıl Oynanır

### Oyun Arayüzü
```
┌─────────────────────────────────────────────────┐
│  [Board Size▼] [Difficulty▼] [Algorithm▼]       │
│  [New Puzzle] [Hint] [Solve] [Compare] [Animate]│
│  [Undo] [Redo] [Clear] [Check] [Stats]          │
├─────────────────────────────────────────────────┤
│                                                 │
│              SUDOKU TAHTASI                     │
│            (9x9 veya 3x3 grid)                  │
│                                                 │
│    [1] [2] [3]  │  [4] [5] [6]  │  [7] [8] [9] │
│    [4] [5] [6]  │  [7] [8] [9]  │  [1] [2] [3] │
│    [7] [8] [9]  │  [1] [2] [3]  │  [4] [5] [6] │
│    ────────────┼───────────────┼────────────── │
│    ...                                          │
│                                                 │
├─────────────────────────────────────────────────┤
│ Status: Ready to play!                          │
│ Metrics: Runtime: 0.00s | Nodes: 0              │
└─────────────────────────────────────────────────┘
```

### Adım Adım Oynama

#### 1️⃣ Yeni Bulmaca Oluşturma
1. **Board Size** menüsünden seçin:
   - `3x3` = Mini Sudoku (kolay, başlangıç için)
   - `9x9` = Standart Sudoku
   - `16x16`, `25x25` = Büyük Sudoku
2. **Difficulty** menüsünden seçin:
   - `Easy` = %50 dolu (kolay)
   - `Medium` = %35 dolu (orta)
   - `Hard` = %25 dolu (zor)
3. **"New Puzzle"** butonuna tıklayın

#### 2️⃣ Manuel Çözüm
- Boş bir hücreye **fare ile tıklayın**
- **1-9** arası bir sayı yazın
- **Enter** tuşuna basın
- Hatalı girişler **kırmızı** renkle gösterilir

#### 3️⃣ İpucu Alma
1. Boş bir hücreye tıklayın
2. **"Get Hint"** butonuna tıklayın
3. Doğru değer hücreye yazılır

#### 4️⃣ Otomatik Çözüm
1. **Algorithm** menüsünden bir algoritma seçin
2. **"Solve"** butonuna tıklayın
3. Bulmaca anında çözülür

#### 5️⃣ Animasyonlu Çözüm 🎬
1. **"Animate"** butonuna tıklayın
2. Kontrol paneli görünür:
   - ⏸️ **Pause** - Duraklat
   - ⏹️ **Stop** - Durdur
   - ⏭️ **Step** - Tek adım
   - **Speed Slider** - Hız ayarı (10ms-500ms)

### Kontroller

| Tuş/Aksiyon | Açıklama |
|-------------|----------|
| **Fare tıklama** | Hücre seçme |
| **1-9 tuşları** | Sayı girme |
| **Enter** | Değeri onaylama |
| **Backspace/Delete** | Hücreyi temizleme |
| **Tab** | Sonraki hücreye geçme |

### Butonlar

| Buton | Açıklama |
|-------|----------|
| 🆕 **New Puzzle** | Yeni bulmaca oluştur |
| 💡 **Get Hint** | Seçili hücre için ipucu al |
| ⚡ **Solve** | Seçili algoritma ile anında çöz |
| 📊 **Compare** | Tüm algoritmaları karşılaştır |
| 🎬 **Animate** | Adım adım animasyonlu çözüm |
| ↶ **Undo** | Son hamleyi geri al |
| ↷ **Redo** | Geri alınan hamleyi yinele |
| 🗑️ **Clear** | Tahtayı orijinal haline döndür |
| ✓ **Check** | Çözümün doğruluğunu kontrol et |
| 📈 **Stats** | İstatistikleri göster |

---

## 🧠 Algoritmalar

### 1. Constraint Propagation (Kısıt Yayılımı)

**Nasıl Çalışır:**
1. Her boş hücre için olası değerler (domain) hesaplanır
2. Tek değerli hücreler board'a yerleştirilir
3. Bu değer komşu hücrelerin domain'lerinden çıkarılır
4. İşlem tekrarlanır (propagation)
5. Tıkanırsa backtracking yapılır

**Avantajları:**
- ✅ En hızlı algoritma
- ✅ Basit bulmacalar için ideal
- ✅ Domain azaltma ile arama alanını daraltır

**Dezavantajları:**
- ⚠️ Tek başına zor bulmacaları çözemez (backtracking gerekir)

**Pseudocode:**
```
function solve(board):
    domains = initialize_domains(board)
    
    while changed:
        for each cell with single value:
            assign value to cell
            remove value from neighbors' domains
    
    if solved: return board
    
    # Backtracking
    cell = select_cell_with_smallest_domain()
    for value in cell.domain:
        result = solve(board with value)
        if result: return result
    
    return None
```

---

### 2. AC-3 (Arc Consistency Algorithm 3)

**Nasıl Çalışır:**
1. Sudoku bir CSP (Constraint Satisfaction Problem) olarak modellenir
2. Her hücre çifti arasında "arc" (yay) tanımlanır
3. Arc consistency: Bir hücrenin her değeri için komşuda uyumlu değer olmalı
4. Domain'lerden tutarsız değerler çıkarılır
5. Tıkanırsa MAC (Maintaining Arc Consistency) ile backtracking

**Avantajları:**
- ✅ Güçlü domain daraltma
- ✅ Orta zorlukta bulmacalar için etkili

**Dezavantajları:**
- ⚠️ Constraint Propagation'dan biraz yavaş
- ⚠️ Çok zor bulmacalarda yine backtracking gerekir

**Pseudocode:**
```
function ac3(domains):
    queue = all arcs (cell_i, cell_j)
    
    while queue not empty:
        (xi, xj) = queue.pop()
        if revise(xi, xj):
            if domain[xi] is empty: return False
            for each neighbor xk of xi:
                queue.add((xk, xi))
    return True

function revise(xi, xj):
    if domain[xj] has single value v:
        remove v from domain[xi]
        return True
    return False
```

---

### 3. Backtracking (Geri İzleme)

**Nasıl Çalışır:**
1. Boş bir hücre seç (MRV: en az seçenekli)
2. Geçerli bir değer dene
3. Recursive olarak çözmeye devam et
4. Çıkmaz sokakta geri dön (backtrack)
5. Başka değer dene

**Avantajları:**
- ✅ Her bulmacayı çözebilir (complete)
- ✅ Basit ve anlaşılır

**Dezavantajları:**
- ⚠️ Zor bulmacalarda yavaş
- ⚠️ Çok fazla backtrack yapabilir

**Pseudocode:**
```
function backtrack(board):
    if board.is_solved(): return board
    
    cell = select_unassigned_cell()  # MRV heuristic
    
    for value in cell.domain:
        if is_valid(cell, value):
            board[cell] = value
            result = backtrack(board)
            if result: return result
            board[cell] = 0  # Backtrack
    
    return None
```

---

### 4. Iterative Backtracking (Stack Tabanlı)

**Nasıl Çalışır:**
- Backtracking'in recursion yerine stack kullanan versiyonu
- Büyük bulmacalarda (16x16+) RecursionError'ı önler

---

## 📊 Performans Karşılaştırması

### Test Sonuçları (9x9 Sudoku)

| Algoritma | Easy | Medium | Hard |
|-----------|------|--------|------|
| **Constraint Propagation** | ~1-5 node | ~5-15 node | ~10-50 node |
| **AC-3** | ~1-5 node | ~5-15 node | ~10-50 node |
| **Backtracking** | ~30-50 node | ~50-100 node | ~50-200 node |
| **Iterative Backtracking** | ~100-300 node | ~500-5000 node | ~100-500 node |

### Metrikler

| Metrik | Açıklama |
|--------|----------|
| **Runtime** | Çözüm süresi (saniye) |
| **Nodes Visited** | Ziyaret edilen durum sayısı |
| **Backtrack Count** | Geri dönüş sayısı |
| **Domain Reductions** | Domain'den çıkarılan değer sayısı |

### Beklenen Gözlemler

- **Easy bulmacalar**: Tüm algoritmalar hızlı
- **Hard bulmacalar**: 
  - Constraint Propagation ve AC-3 arama alanını daraltır
  - Backtracking daha fazla deneme yapar
- **Hibrit yaklaşımlar**: En iyi performans (CP + Backtracking)

---

## 📁 Dosya Yapısı

```
Sudoku-Solver/
├── sudoku_game.py         # Ana oyun uygulaması (GUI)
├── algorithms.py          # AI çözüm algoritmaları
├── sudoku_board.py        # Sudoku board sınıfı
├── puzzle_generator.py    # Bulmaca üretici
├── animation_controller.py# Animasyon kontrolü
├── test_game.py           # Basit testler
├── README.md              # Bu dosya
└── Seng465Project.pdf     # Proje raporu
```

### Sınıflar

| Sınıf | Dosya | Açıklama |
|-------|-------|----------|
| `SudokuBoard` | sudoku_board.py | Board durumu, doğrulama, domain hesaplama |
| `ConstraintPropagationSolver` | algorithms.py | Kısıt yayılımı algoritması |
| `AC3Solver` | algorithms.py | Arc consistency algoritması |
| `BacktrackingSolver` | algorithms.py | DFS + backtracking |
| `IterativeBacktrackingSolver` | algorithms.py | Stack tabanlı backtracking |
| `PuzzleGenerator` | puzzle_generator.py | Geçerli bulmaca üretimi |
| `AnimationController` | animation_controller.py | Adım adım animasyon |
| `SudokuGame` | sudoku_game.py | Ana GUI uygulaması |

---

## 🔧 Teknik Detaylar

### Board Doğrulama

Her hamle şu kurallara göre kontrol edilir:

1. **Satır Kontrolü**: Aynı satırda tekrar yok
2. **Sütun Kontrolü**: Aynı sütunda tekrar yok
3. **Kutu Kontrolü**: Aynı 3x3 kutuda tekrar yok

```python
def is_valid_move(self, row, col, value):
    # Satır kontrolü
    for c in range(size):
        if board[row][c] == value: return False
    
    # Sütun kontrolü
    for r in range(size):
        if board[r][col] == value: return False
    
    # 3x3 Kutu kontrolü
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == value: return False
    
    return True
```

### Bulmaca Üretimi

1. Boş 9x9 board oluştur
2. Köşegen 3x3 kutuları rastgele doldur (birbirini etkilemez)
3. Backtracking ile geri kalanı doldur
4. Zorluk seviyesine göre hücre sil

### Zorluk Seviyeleri

| Seviye | Dolu Hücre Oranı | Boş Hücre (9x9) |
|--------|------------------|-----------------|
| Easy | %50 | ~40-41 |
| Medium | %35 | ~52-53 |
| Hard | %25 | ~60-61 |

---

## ❓ Sorun Giderme

### Oyun Açılmıyor

**Hata:** `ModuleNotFoundError: No module named 'tkinter'`

**Çözüm:**
```bash
# Linux (Debian/Ubuntu)
sudo apt-get install python3-tk

# Linux (Fedora)
sudo dnf install python3-tkinter

# Mac
brew install python-tk
```

### Python Bulunamıyor

**Hata:** `'python' is not recognized`

**Çözüm:**
- `python3` deneyin
- Python PATH'e eklenmiş mi kontrol edin

### Pencere Görünmüyor

**Çözüm:**
- Başka bir pencerenin arkasında olabilir
- Taskbar'da kontrol edin
- Yeniden başlatın

---

## 👥 Yazarlar

| İsim | Öğrenci No |
|------|------------|
| Berfin Duru ALKAN | 202228005 |
| Şahin ERŞAN | 202128002 |
| Özgün SOYKÖK | 202228043 |
| İsmail DOĞAN | 202128045 |

---

## 📚 Ders Bilgisi

**SENG 465** - Artificial Intelligence in Game Programming

Bu proje eğitim amaçlı geliştirilmiştir.

---

## 📜 Lisans

Bu proje eğitim amaçlı oluşturulmuştur.
