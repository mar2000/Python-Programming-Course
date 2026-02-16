import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin


class WikiScraper:
    """
    Klasa do scrapowania pojedynczej strony wiki.
    Może pobierać z internetu lub z lokalnego pliku HTML.
    """

    def __init__(self, base_url, page_title,
                 use_local_file=False, local_file_path=None):
        """
        Inicjalizuje scraper i ładuje stronę.

        :param base_url: bazowy adres wiki (np. https://bulbapedia.bulbagarden.net)
        :param page_title: tytuł artykułu (może zawierać spacje)
        :param use_local_file: czy używać pliku lokalnego zamiast HTTP
        :param local_file_path: ścieżka do lokalnego pliku HTML
        """
        self.base_url = base_url.rstrip('/')
        self.page_title = page_title
        self.use_local_file = use_local_file
        self.local_file_path = local_file_path
        self.soup = None
        self.page_url = self._build_page_url()
        self._load_page()

    def _build_page_url(self):
        """Tworzy pełny URL artykułu (zamienia spacje na podkreślenia)."""
        title_underscore = self.page_title.replace(' ', '_')
        return f"{self.base_url}/wiki/{title_underscore}"

    def _load_page(self):
        """
        Ładuje stronę – albo z pliku lokalnego, albo przez HTTP.
        Ustawia atrybut self.soup (obiekt BeautifulSoup).
        """
        if self.use_local_file:
            with open(self.local_file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            self.soup = BeautifulSoup(html, 'lxml')
        else:
            response = requests.get(self.page_url)
            if response.status_code == 404:
                raise Exception(f"Artykuł '{self.page_title}' nie istnieje (404).")
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'lxml')

    def get_first_paragraph(self):
        """
        Zwraca tekst pierwszego niepustego paragrafu w głównej treści artykułu.
        """
        # Znajdź div z treścią (klasa zazwyczaj mw-content-ltr lub mw-content-rtl)
        content_div = self.soup.find('div',
                                     class_=re.compile(r'mw-content-?(ltr|rtl)?'))
        if not content_div:
            content_div = self.soup.body

        paragraphs = content_div.find_all('p', recursive=True)
        for p in paragraphs:
            text = p.get_text(separator=' ', strip=True)
            # Pomijamy puste oraz paragrafy wewnątrz tabel (często szablony)
            if text and not p.find_parent('table'):
                return text
        return ""

    def get_full_text(self):
        """
        Zwraca cały tekst artykułu (bez elementów stałych strony,
        takich jak menu, stopka itp.).
        """
        content_div = self.soup.find('div',
                                     class_=re.compile(r'mw-content-?(ltr|rtl)?'))
        if content_div:
            return content_div.get_text(separator=' ', strip=True)
        return self.soup.body.get_text(separator=' ', strip=True)

    def get_table(self, table_index):
        """
        Zwraca n-tą tabelę (licząc od 1) jako obiekt BeautifulSoup.

        :param table_index: numer tabeli (1-based)
        :return: obiekt BeautifulSoup reprezentujący tabelę
        :raises Exception: jeśli tabela o podanym indeksie nie istnieje
        """
        tables = self.soup.find_all('table')
        if not tables or table_index > len(tables):
            raise Exception(f"Tabela nr {table_index} nie istnieje.")
        return tables[table_index - 1]

    def extract_table_data(self, table_soup, first_row_is_header=False):
        """
        Wyciąga dane z tabeli jako lista wierszy.

        :param table_soup: obiekt BeautifulSoup tabeli
        :param first_row_is_header: czy pierwszy wiersz traktować jako nagłówek
        :return: lista wierszy, gdzie każdy wiersz to lista komórek (tekst)
        """
        rows = []
        # Obsługa sekcji <thead>
        thead = table_soup.find('thead')
        if thead:
            for hr in thead.find_all('tr'):
                rows.append([cell.get_text(strip=True)
                             for cell in hr.find_all(['th', 'td'])])

        # Obsługa <tbody> lub bezpośrednich wierszy w tabeli
        tbody = table_soup.find('tbody')
        if tbody:
            data_rows = tbody.find_all('tr')
        else:
            data_rows = table_soup.find_all('tr', recursive=False)

        for tr in data_rows:
            cells = tr.find_all(['td', 'th'])
            if cells:
                rows.append([cell.get_text(strip=True) for cell in cells])

        # Jeśli nie było <thead>, a first_row_is_header=True,
        # pierwszy wiersz pozostanie nagłówkiem – nic nie zmieniamy.
        return rows

    def get_all_links(self):
        """
        Zwraca listę tytułów artykułów wewnętrznych (wewnętrznych linków wiki)
        znalezionych na stronie. Pomija linki do plików, kategorii itp.
        """
        links = []
        for a in self.soup.find_all('a', href=True):
            href = a['href']
            # Link zaczyna się od /wiki/ i nie zawiera dwukropka poza tym prefixem
            if href.startswith('/wiki/') and ':' not in href.split('/wiki/')[1]:
                full_url = urljoin(self.base_url, href)
                path = full_url.split('/wiki/')[-1]
                title = path.replace('_', ' ')
                links.append(title)
        return links
