from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import hashlib
from scraper.scraper import Scraper
from scraper.notifier import Notifier
from config.config import HOST, PORT


class WebSocketServer:
    """
    A class to represent a WebSocket server using Flask and SocketIO.

    Attributes
    ----------
    host : str
        The host address on which the server will run.
    port : int
        The port number on which the server will listen.
    app : Flask
        The Flask application instance.
    socketio : SocketIO
        The SocketIO instance for handling WebSocket connections.
    scraped_pages : dict
        A dictionary to store scraped pages content keyed by their MD5 hash.

    Methods
    -------
    _register_routes():
        Registers the HTTP routes for scraping, notifying, and serving pages.
    _generate_key_by_url(url: str) -> str:
        Generates an MD5 hash key for a given URL.
    run():
        Runs the WebSocket server.
    """

    def __init__(self, host=HOST, port=PORT):
        """
        Initializes the WebSocketServer with a specified host and port.

        Parameters
        ----------
        host : str, optional
            The host address (default is from the config).
        port : int, optional
            The port number (default is from the config).
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.scraped_pages = {}
        self._register_routes()

    def _register_routes(self):
        @self.app.route('/scrape', methods=["POST"])
        def scrape():
            """
            Handles the /scrape route to scrape content from a given URL.

            Expects JSON with the 'url' key in the request body.
            Returns a JSON response with the status and a key for the scraped content.
            """
            data = request.json
            url = data.get('url')
            if url:
                try:
                    notifier = Notifier()
                    scraper = Scraper(url=url, notifier=notifier)
                    data = scraper.scrape()
                    key = self._generate_key_by_url(url)
                    self.scraped_pages[key] = data
                    return jsonify({"status": f"scraping completed for {url}", "key": key}), 200
                except Exception as e:
                    return jsonify({"error": str(e)}), 500

        @self.app.route('/notify', methods=["POST"])
        def notify():
            """
            Handles the /notify route to send scraping updates to the client.

            Expects JSON with the 'url' key in the request body.
            Emits the scraping update via WebSocket to all connected clients.
            """
            data = request.json
            key = self._generate_key_by_url(data['url'])
            data['key'] = key
            self.socketio.emit("scraping_update", data)
            return {"status": "notification sent successfully to client"}, 200

        @self.app.route('/page/<key>', methods=["GET"])
        def serve_page(key):
            """
            Handles the /page/<key> route to serve the scraped content.

            If the key is found in the scraped_pages dictionary, the content is returned.
            Otherwise, a 404 error is returned.
            """
            if key in self.scraped_pages.keys():
                content = self.scraped_pages[key]
                return content
            else:
                return "page not found", 404

    def _generate_key_by_url(self, url: str) -> str:
        """
        Generates an MD5 hash key based on the given URL.

        Parameters
        ----------
        url : str
            The URL for which to generate the key.

        Returns
        -------
        str
            The MD5 hash of the URL.
        """
        return hashlib.md5(url.encode()).hexdigest()

    def run(self):
        """
        Runs the Flask and SocketIO server on the specified host and port.
        """
        self.socketio.run(app=self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    # Entry point to start the WebSocket server
    server = WebSocketServer()
    server.run()
