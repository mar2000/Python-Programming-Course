import pandas as pd
import matplotlib.pyplot as plt
from wordfreq import get_frequency_dict


class LanguageAnalyzer:
    """
    Klasa do analizy częstotliwości słów w artykule w porównaniu z językiem.
    """

    def __init__(self, language_code='en', word_counts=None):
        """
        Inicjalizuje analizator.

        :param language_code: kod języka (np. 'en', 'pl')
        :param word_counts: słownik zliczeń słów z artykułu
        """
        self.language_code = language_code
        self.word_counts = word_counts or {}
        # Pobranie słownika częstotliwości dla danego języka z biblioteki wordfreq
        self.lang_freq = get_frequency_dict(lang=language_code, wordlist='best')

    def normalize(self, freq_dict):
        """
        Normalizuje słownik częstotliwości do przedziału [0, 1],
        dzieląc przez maksymalną wartość.

        :param freq_dict: słownik {słowo: częstotliwość}
        :return: znormalizowany słownik
        """
        if not freq_dict:
            return {}
        max_val = max(freq_dict.values())
        if max_val == 0:      # zapobiega dzieleniu przez zero
            return freq_dict
        return {k: v / max_val for k, v in freq_dict.items()}

    def prepare_table(self, mode='article', n=10):
        """
        Przygotowuje tabelę porównawczą dla n najczęstszych słów
        w wybranym trybie ('article' lub 'language').

        :param mode: 'article' – sortowanie wg artykułu,
                     'language' – sortowanie wg języka
        :param n: liczba słów do uwzględnienia
        :return: pandas.DataFrame z kolumnami:
                 word, frequency_in_article, frequency_in_language
        """
        norm_article = self.normalize(self.word_counts)
        norm_lang = self.normalize(self.lang_freq)

        if mode == 'article':
            # Pobierz n najczęstszych słów z artykułu
            top = sorted(norm_article.items(),
                         key=lambda x: x[1], reverse=True)[:n]
            words = [w for w, _ in top]
        else:
            # Pobierz n najczęstszych słów z języka
            top = sorted(norm_lang.items(),
                         key=lambda x: x[1], reverse=True)[:n]
            words = [w for w, _ in top]

        data = []
        for word in words:
            data.append({
                'word': word,
                'frequency_in_article': norm_article.get(word, 0),
                'frequency_in_language': norm_lang.get(word, 0)
            })

        df = pd.DataFrame(data)

        # Posortuj zgodnie z wybranym trybem
        if mode == 'article':
            df = df.sort_values('frequency_in_article', ascending=False)
        else:
            df = df.sort_values('frequency_in_language', ascending=False)
        return df

    def plot_chart(self, df, output_path):
        """
        Tworzy wykres słupkowy porównujący częstotliwości słów
        i zapisuje go do pliku.

        :param df: DataFrame wygenerowany przez prepare_table
        :param output_path: ścieżka do pliku PNG
        """
        words = df['word'].tolist()
        freq_article = df['frequency_in_article'].tolist()
        freq_lang = df['frequency_in_language'].tolist()

        x = range(len(words))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar([i - width / 2 for i in x],
               freq_article, width, label='Artykuł')
        ax.bar([i + width / 2 for i in x],
               freq_lang, width, label='Język')

        ax.set_xlabel('Słowa')
        ax.set_ylabel('Znormalizowana częstotliwość')
        ax.set_title('Porównanie częstotliwości słów')
        ax.set_xticks(x)
        ax.set_xticklabels(words, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
