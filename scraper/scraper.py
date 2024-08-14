import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from .notifier import Notifier


class Scraper:
    def __init__(self, url: str, notifier: Notifier) -> None:
        self.url = url
        self.notifier = notifier

    def scrape(self) -> str:
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            if 'html' in content_type:
                content = self._scrape_html(response)
            elif 'xml' in content_type or 'application/xml' in content_type:
                content = self._scrape_xml(response)
            elif 'json' in content_type:
                content = self._scrape_json(response)
            elif 'text' in content_type:
                content = self._scrape_plain_text(response)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            self.notifier.notify_offline_components(url=self.url, status="scraping complete", content=content)
            return content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to scrape data: {str(e)}")

    def _scrape_html(self, response):
        html_content = BeautifulSoup(response.content, "html.parser")
        return html_content.prettify()

    def _scrape_xml(self, response):
        data = ET.fromstring(response.content)
        return ET.tostring(data, encoding="unicode", method="xml")

    def _scrape_json(self, response):
        data = response.json()
        return json.dumps(data, indent=4)

    def _scrape_plain_text(self, response):
        return response.text
