from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import hashlib
from scraper.scraper import Scraper
from scraper.notifier import Notifier
from config.config import HOST, PORT


class WebSocketServer:
    def __init__(self, host=HOST, port=PORT):
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
            data = request.json
            key = self._generate_key_by_url(data['url'])
            data['key'] = key
            self.socketio.emit("scraping_update", data)
            return {"status": "notification sent successfully to client"}, 200

        @self.app.route('/page/<key>', methods=["GET"])
        def serve_page(key):
            if key in self.scraped_pages.keys():
                content = self.scraped_pages[key]
                return content
            else:
                return "page not foung", 404

    def _generate_key_by_url(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def run(self):
        self.socketio.run(app=self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = WebSocketServer()
    server.run()
