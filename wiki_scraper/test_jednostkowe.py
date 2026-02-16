import unittest
import os
import tempfile
from scraper import WikiScraper
from word_counter import WordCounter


class TestScraperMethods(unittest.TestCase):
    """
    Testy jednostkowe dla klasy WikiScraper i WordCounter.
    """

    def setUp(self):
        """Przygotowuje tymczasowy plik HTML z przykładową stroną."""
        self.html = """
        <html>
        <body>
        <div class="mw-content-ltr">
        <p>To jest <b>pierwszy</b> paragraf.</p>
        <p>Drugi paragraf.</p>
        </div>
        <table>
        <tr><th>H1</th><th>H2</th></tr>
        <tr><td>a</td><td>b</td></tr>
        </table>
        <a href="/wiki/Strona1">Link1</a>
        <a href="/wiki/Strona2">Link2</a>
        <a href="/wiki/File:Obraz.jpg">Plik</a>
        """
        self.tmp = tempfile.NamedTemporaryFile(mode='w',
                                               encoding='utf-8',
                                               delete=False)
        self.tmp.write(self.html)
        self.tmp.close()

    def tearDown(self):
        """Usuwa tymczasowy plik."""
        os.unlink(self.tmp.name)

    def test_get_first_paragraph(self):
        """Sprawdza, czy pierwszy paragraf jest poprawnie wyodrębniany."""
        scraper = WikiScraper("http://example.com", "x",
                              use_local_file=True,
                              local_file_path=self.tmp.name)
        self.assertEqual(scraper.get_first_paragraph(),
                         "To jest pierwszy paragraf.")

    def test_get_all_links_filters_files(self):
        """
        Sprawdza, czy get_all_links zwraca tylko linki do artykułów,
        pomijając linki do plików (z dwukropkiem).
        """
        scraper = WikiScraper("http://example.com", "x",
                              use_local_file=True,
                              local_file_path=self.tmp.name)
        links = scraper.get_all_links()
        self.assertIn("Strona1", links)
        self.assertIn("Strona2", links)
        self.assertNotIn("File:Obraz", links)

    def test_extract_table_data(self):
        """Sprawdza poprawne wyodrębnianie danych z tabeli."""
        scraper = WikiScraper("http://example.com", "x",
                              use_local_file=True,
                              local_file_path=self.tmp.name)
        table = scraper.get_table(1)
        rows = scraper.extract_table_data(table)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["H1", "H2"])
        self.assertEqual(rows[1], ["a", "b"])

    def test_count_words_in_text(self):
        """Sprawdza, czy WordCounter poprawnie zlicza słowa."""
        with tempfile.NamedTemporaryFile(mode='w',
                                         suffix='.json',
                                         delete=False) as f:
            temp_json = f.name
        try:
            counter = WordCounter(json_path=temp_json)
            text = "Ala ma kota. Kot ma Alę."
            counts = counter.count_words_in_text(text)
            self.assertEqual(counts['ala'], 1)
            self.assertEqual(counts['alę'], 1)
            self.assertEqual(counts['ma'], 2)
            self.assertEqual(counts['kota'], 1)
            self.assertEqual(counts['kot'], 1)
        finally:
            os.unlink(temp_json)


if __name__ == '__main__':
    unittest.main()
