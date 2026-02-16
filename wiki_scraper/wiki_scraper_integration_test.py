#!/usr/bin/env python3
"""
Test integracyjny dla WikiScraper.
Wczytuje lokalny plik HTML z przykładowym artykułem i sprawdza,
czy pierwszy paragraf jest poprawnie wyodrębniany.
"""

import os
import sys
import tempfile
from scraper import WikiScraper

TEST_HTML = """
<html>
<body>
<div class="mw-content-ltr">
<p>Team Rocket (Japanese: ロケット団だん Rocket-dan, literally Rocket Gang) is a villainous team with a small outpost in the Sevii Islands.</p>
</div>
</body>
</html>
"""


def main():
    with tempfile.NamedTemporaryFile(mode='w',
                                     encoding='utf-8',
                                     suffix='.html',
                                     delete=False) as f:
        f.write(TEST_HTML)
        path = f.name

    try:
        scraper = WikiScraper("http://example.com", "Team_Rocket",
                              use_local_file=True,
                              local_file_path=path)
        para = scraper.get_first_paragraph()
        expected_start = "Team Rocket (Japanese:"
        expected_end = "Sevii Islands."
        if para.startswith(expected_start) and para.endswith(expected_end):
            print("Test integracyjny zaliczony.")
            sys.exit(0)
        else:
            print("Niepoprawny tekst:", para)
            sys.exit(1)
    except Exception as e:
        print("Błąd:", e)
        sys.exit(1)
    finally:
        os.unlink(path)


if __name__ == '__main__':
    main()
