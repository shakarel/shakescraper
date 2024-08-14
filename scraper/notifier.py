import requests
from config.config import WEBHOOK_URL

class Notifier:
    def notify_offline_components(self, url: str, status: str, content: str):
        notify_webhook_url = WEBHOOK_URL + "/notify"
        data = {"url": url, "status": status, "content": content}
        try:
            response = requests.post(url=notify_webhook_url, json=data)
            response.raise_for_status()  # check if there has been an HTTP error
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to notify: {str(e)}")
