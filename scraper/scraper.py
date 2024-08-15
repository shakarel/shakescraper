import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
from .notifier import Notifier


class Scraper:
    """
    A class used to scrape content from a given URL.

    Attributes
    ----------
    url : str
        The URL to be scraped.
    notifier : Notifier
        An instance of the Notifier class used to send notifications.

    Methods
    -------
    scrape() -> str
        Scrapes content from the URL based on its content type and returns it as a string.
    _scrape_html(response) -> str
        Extracts and prettifies HTML content from the response.
    _scrape_xml(response) -> str
        Extracts and formats XML content from the response.
    _scrape_json(response) -> str
        Extracts and formats JSON content from the response.
    _scrape_plain_text(response) -> str
        Extracts plain text content from the response.
    """

    def __init__(self, url: str, notifier: Notifier) -> None:
        """
        Initializes the Scraper with a URL and a notifier instance.

        Parameters
        ----------
        url : str
            The URL to be scraped.
        notifier : Notifier
            An instance of the Notifier class to send notifications after scraping.
        """
        self.url = url
        self.notifier = notifier

    def scrape(self) -> str:
        """
        Scrapes content from the URL based on its content type.

        Depending on the content type of the URL, this method delegates to specific
        scraping methods for HTML, XML, JSON, or plain text.

        Returns
        -------
        str
            The scraped content as a string.

        Raises
        ------
        RuntimeError
            If the request to the URL fails or the content type is unsupported.
        """
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

    def _scrape_html(self, response) -> str:
        """
        Extracts and prettifies HTML content from the response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object containing HTML content.

        Returns
        -------
        str
            The prettified HTML content as a string.
        """
        html_content = BeautifulSoup(response.content, "html.parser")
        return html_content.prettify()

    def _scrape_xml(self, response) -> str:
        """
        Extracts and formats XML content from the response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object containing XML content.

        Returns
        -------
        str
            The formatted XML content as a string.
        """
        data = ET.fromstring(response.content)
        return ET.tostring(data, encoding="unicode", method="xml")

    def _scrape_json(self, response) -> str:
        """
        Extracts and formats JSON content from the response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object containing JSON content.

        Returns
        -------
        str
            The formatted JSON content as a string.
        """
        data = response.json()
        return json.dumps(data, indent=4)

    def _scrape_plain_text(self, response) -> str:
        """
        Extracts plain text content from the response.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object containing plain text content.

        Returns
        -------
        str
            The plain text content as a string.
        """
        return response.text
