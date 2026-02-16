import json
import os
import re
from collections import Counter


class WordCounter:
    """
    Zarządza zliczaniem słów w przetwarzanych tekstach.
    Wyniki przechowywane są w pliku JSON.
    """

    def __init__(self, json_path='word-counts.json'):
        """
        Inicjalizuje licznik, ładując istniejące dane z pliku JSON.

        :param json_path: ścieżka do pliku JSON z danymi
        """
        self.json_path = json_path
        self.word_counts = self._load()

    def _load(self):
        """
        Wczytuje słownik z pliku JSON.
        Jeśli plik nie istnieje lub jest uszkodzony, zwraca pusty słownik.
        """
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Jeśli plik jest pusty lub uszkodzony, zwróć pusty słownik
                return {}
        return {}

    def _save(self):
        """Zapisuje bieżący słownik do pliku JSON."""
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.word_counts, f, indent=2, ensure_ascii=False)

    def count_words_in_text(self, text):
        """
        Zlicza słowa w podanym tekście.
        Używa wyrażenia regularnego, które wyodrębnia ciągi liter (także Unicode),
        pomijając cyfry i podkreślenia.

        :param text: tekst do analizy
        :return: obiekt collections.Counter ze słowami
        """
        # \b[^\W\d_]+\b  - dopasowuje słowa składające się wyłącznie z liter
        words = re.findall(r'\b[^\W\d_]+\b', text.lower())
        return Counter(words)

    def update(self, text):
        """
        Aktualizuje liczniki słów na podstawie nowego tekstu
        i zapisuje zmiany do pliku.
        """
        counter = self.count_words_in_text(text)
        for word, count in counter.items():
            self.word_counts[word] = self.word_counts.get(word, 0) + count
        self._save()

    def get_counts(self):
        """Zwraca słownik zliczeń słów."""
        return self.word_counts
