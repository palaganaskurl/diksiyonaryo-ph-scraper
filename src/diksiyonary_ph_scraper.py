import json
import logging
from string import ascii_lowercase, ascii_uppercase
from time import sleep
from typing import Dict, Union

from requests_html import HTMLSession, HTML, Element

logging.basicConfig(level=logging.INFO)


class DiksiyonaryoPHScraper:
    url = 'https://diksiyonaryo.ph'
    letters = list(ascii_uppercase) + ['Ng']
    session = HTMLSession()

    # noinspection PyMethodMayBeStatic
    def print_words(self, words: Dict) -> None:
        """
        Puts words dictionary to JSON file.
        :type words: Dict
        :param words: Words Dictionary in the form of {'word': {'part_of_speech': [], definition: ''}
        :rtype: None
        :return: Nothing
        """
        with open('../words/tagalog-words.json', 'w+', encoding='utf-8') as f:
            json.dump(words, f, indent=4, ensure_ascii=False)

    # noinspection PyMethodMayBeStatic
    def _get_url_content(self, url: str) -> HTML:
        """
        Gets content of URL synchronously.

        :type url: str
        :param url: URL where to get the content
        :rtype: HTML
        :return: requests_html.HTML instance
        """
        response = self.session.get(url)

        return response.html

    def scrape(self) -> Dict:
        """
        Start scraping here.

        :rtype: Dict
        :return: Dictionary in the form of {'word': {data: 'data'}
        """
        words = {}
        # Storage for HTML data to avoid request to the URL
        htmls = {}

        for letter in self.letters:
            logging.info('Current Letter: {}'.format(letter))
            current_url = '{url}/list/{letter}'.format(
                url=self.url,
                letter=letter
            )
            first_page = self._get_url_content(current_url)
            next_page = first_page
            htmls[letter] = [first_page]

            while True:
                next_page = self._get_next_page(next_page)

                if next_page is None:
                    break

                htmls[letter].append(next_page)

                # logging.info('Current Letter: {} Page: {}'.format(letter, next_page.url))

            words.update(self._get_page_content(htmls[letter]))

            logging.info('Done Letter: {}'.format(letter))

            sleep(5)

        return words

    def _get_next_page(self, current_page: HTML):
        next_page_href = current_page.find('a', containing='>>', first=True)
        next_page_html = self._get_url_content('{url}{next_page}'.format(
            url=self.url,
            next_page=next_page_href.attrs['href']
        ))

        if current_page.url == next_page_html.url:
            return None

        return next_page_html

    # noinspection PyMethodMayBeStatic
    def _get_page_content(self, htmls):
        def _get_text_if_exists(elem: Union[Element, None]) -> str:
            if not elem:
                return ''

            return elem.text.strip()

        words = {}

        for html in htmls:
            words_div = html.find('.word')

            for word_div in words_div:
                word = word_div.attrs['id']
                definitions_div = word_div.find('.definition-text') or []
                definitions = []

                for definition in definitions_div:
                    definitions.append(definition.text.strip())

                words[word] = {
                    'pronunciation': _get_text_if_exists(word_div.find('.pronunciation', first=True)),
                    'part_of_speech': _get_text_if_exists(word_div.find('.pos', first=True)),
                    'etymology': _get_text_if_exists(word_div.find('.etymology', first=True)),
                    'derivative': _get_text_if_exists(word_div.find('.derivative', first=True)),
                    'definitions': definitions
                }

        return words


if __name__ == '__main__':
    t = DiksiyonaryoPHScraper()
    w = t.scrape()
    t.print_words(w)
