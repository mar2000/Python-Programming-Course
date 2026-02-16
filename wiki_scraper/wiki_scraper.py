#!/usr/bin/env python3
"""
Główny skrypt CLI do scrapowania Bulbapedii i analizy słów.
"""

import argparse
import sys
import time
from collections import deque
import io

import pandas as pd

from scraper import WikiScraper
from word_counter import WordCounter
from language_analyzer import LanguageAnalyzer

BASE_URL = "https://bulbapedia.bulbagarden.net"
LANGUAGE = "en"


def cmd_summary(fraza):
    """Wyświetla pierwszy paragraf artykułu."""
    scraper = WikiScraper(BASE_URL, fraza)
    print(scraper.get_first_paragraph())


def cmd_table(fraza, number, first_row_is_header):
    """
    Zapisuje tabelę z artykułu do pliku CSV.
    Dodatkowo wypisuje częstotliwości wartości w kolumnach.
    """
    scraper = WikiScraper(BASE_URL, fraza)
    table_soup = scraper.get_table(number)

    # Próba wczytania tabeli przez pandas.read_html (łatwiejsze)
    html_str = str(table_soup)
    try:
        df = pd.read_html(io.StringIO(html_str),
                          header=0 if first_row_is_header else None)[0]
    except Exception as e:
        print(f"Nie udało się wczytać tabeli przez pandas: {e}")
        # Fallback na własne parsowanie
        rows = scraper.extract_table_data(table_soup,
                                          first_row_is_header=first_row_is_header)
        if not rows:
            print("Tabela jest pusta.")
            return

        if first_row_is_header:
            # Wyrównaj długości wierszy
            max_cols = max(len(row) for row in rows)
            header = rows[0]
            if len(header) < max_cols:
                header += [f"col{i+1}" for i in range(len(header), max_cols)]
            data = rows[1:]
            data_filled = [row + [''] * (max_cols - len(row)) for row in data]
            df = pd.DataFrame(data_filled, columns=header)
        else:
            max_cols = max(len(row) for row in rows)
            data_filled = [row + [''] * (max_cols - len(row)) for row in rows]
            df = pd.DataFrame(data_filled)

    filename = f"{fraza.replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)
    print(f"Zapisano tabelę do {filename}")

    if not df.empty:
        print("\nCzęstotliwości wartości w tabeli (bez nagłówków):")
        for col in df.columns:
            print(f"\nKolumna: {col}")
            print(df[col].value_counts().to_string())


def cmd_count_words(fraza):
    """Zlicza słowa w artykule i aktualizuje plik JSON."""
    scraper = WikiScraper(BASE_URL, fraza)
    full_text = scraper.get_full_text()
    counter = WordCounter()
    counter.update(full_text)
    print(f"Zaktualizowano liczniki słów dla '{fraza}'.")


def cmd_analyze(mode, count, chart):
    """
    Przeprowadza analizę częstotliwości słów na podstawie
    zebranych danych (z pliku JSON) i języka wzorcowego.
    """
    wc = WordCounter()
    analyzer = LanguageAnalyzer(language_code=LANGUAGE,
                                word_counts=wc.get_counts())
    df = analyzer.prepare_table(mode=mode, n=count)
    print(df.to_string(index=False))

    if chart:
        analyzer.plot_chart(df, chart)
        print(f"Wykres zapisany do {chart}")


def cmd_auto_count_words(poczatkowa, depth, wait):
    """
    Automatyczne przechodzenie po linkach (BFS) i zliczanie słów
    z odwiedzonych artykułów.
    """
    queue = deque()
    queue.append((poczatkowa, 0))
    visited = {poczatkowa}
    wc = WordCounter()

    while queue:
        fraza, curr_depth = queue.popleft()
        print(f"Przetwarzanie: {fraza} (głębokość {curr_depth})")
        try:
            scraper = WikiScraper(BASE_URL, fraza)
        except Exception as e:
            print(f"Błąd dla {fraza}: {e}")
            continue

        full_text = scraper.get_full_text()
        wc.update(full_text)

        if curr_depth < depth:
            for link in scraper.get_all_links():
                if link not in visited:
                    visited.add(link)
                    queue.append((link, curr_depth + 1))

        time.sleep(wait)

    print("Zakończono przetwarzanie.")


def main():
    parser = argparse.ArgumentParser(
        description='WikiScraper - narzędzie do scrapowania Bulbapedii'
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--summary', metavar='fraza',
                       help='Wyświetl pierwszy paragraf artykułu')
    group.add_argument('--table', metavar='fraza',
                       help='Zapisz tabelę do CSV (wymaga --number)')
    group.add_argument('--count-words', metavar='fraza',
                       help='Zlicz słowa w artykule')
    group.add_argument('--analyze-relative-word-frequency',
                       action='store_true',
                       help='Analiza częstotliwości (wymaga --mode i --count)')
    group.add_argument('--auto-count-words', metavar='fraza',
                       help='Automatyczne zliczanie słów z podążaniem za linkami'
                            ' (wymaga --depth i --wait)')

    parser.add_argument('--number', type=int,
                        help='Numer tabeli (dla --table)')
    parser.add_argument('--first-row-is-header', action='store_true',
                        help='Czy pierwszy wiersz tabeli to nagłówek (dla --table)')
    parser.add_argument('--mode', choices=['article', 'language'],
                        help='Tryb analizy (dla --analyze-relative-word-frequency)')
    parser.add_argument('--count', type=int,
                        help='Liczba słów do analizy (dla --analyze-relative-word-frequency)')
    parser.add_argument('--chart', metavar='PLIK_PNG',
                        help='Ścieżka do pliku PNG z wykresem'
                             ' (dla --analyze-relative-word-frequency)')
    parser.add_argument('--depth', type=int,
                        help='Głębokość przechodzenia (dla --auto-count-words)')
    parser.add_argument('--wait', type=float,
                        help='Czas oczekiwania między zapytaniami'
                             ' (dla --auto-count-words)')

    args = parser.parse_args()

    if args.summary:
        cmd_summary(args.summary)
    elif args.table:
        if args.number is None:
            parser.error("--table wymaga podania --number")
        cmd_table(args.table, args.number, args.first_row_is_header)
    elif args.count_words:
        cmd_count_words(args.count_words)
    elif args.analyze_relative_word_frequency:
        if args.mode is None or args.count is None:
            parser.error("--analyze-relative-word-frequency wymaga --mode i --count")
        cmd_analyze(args.mode, args.count, args.chart)
    elif args.auto_count_words:
        if args.depth is None or args.wait is None:
            parser.error("--auto-count-words wymaga --depth i --wait")
        cmd_auto_count_words(args.auto_count_words, args.depth, args.wait)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
