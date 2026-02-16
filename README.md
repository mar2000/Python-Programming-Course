
# Wiki Scraper

Projekt CLI do scrapowania danych z Wiki, zliczania słów oraz analizy częstotliwości językowej.

---

## 1. Przygotowanie środowiska

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
````

---

## 2. Testy jednostkowe i integracyjny

```bash
python3 test_jednostkowe.py
python3 wiki_scraper_integration_test.py
```

---

## 3. Ręczne sprawdzanie

### Pobranie streszczenia artykułu

```bash
python3 wiki_scraper.py --summary "Team Rocket"
```

### Pobranie tabeli

```bash
python3 wiki_scraper.py --table "Type" --number 2 --first-row-is-header
```

### Zliczanie słów w artykule

```bash
python3 wiki_scraper.py --count-words "Team Rocket"
```

### Analiza względnej częstotliwości słów + wykres

```bash
python3 wiki_scraper.py --analyze-relative-word-frequency --mode article --count 10 --chart wykres.png
```

### Automatyczne zliczanie słów z linków

```bash
python3 wiki_scraper.py --auto-count-words "Team Rocket" --depth 1 --wait 1
```

---

## 4. Uruchamianie Jupyter Notebook

```bash
jupyter notebook
```

---

## 5. Struktura projektu

```
/wiki_scraper
├── wiki_scraper.py                   # główny skrypt CLI
├── scraper.py                        # klasa do scrapowania
├── word_counter.py                   # zarządzanie zliczaniem słów i JSON
├── language_analyzer.py              # analiza częstotliwości i wykresy
├── test_jednostkowe.py               # 4 testy jednostkowe
├── wiki_scraper_integration_test.py  # test integracyjny
├── requirements.txt                  # zależności
├── analysis.ipynb                    # notatnik Jupyter z analizą języka
└── (opcjonalnie) test_data/          # katalog z lokalnymi plikami HTML do testów
```

---
