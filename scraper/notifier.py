import requests
from config.config import WEBHOOK_URL


class Notifier:
    """
    A class used to send notifications about the status of components to a webhook URL.

    Methods
    -------
    notify_offline_components(url: str, status: str, content: str)
        Sends a POST request to a webhook URL with information about a component's status.
    """

    def notify_offline_components(self, url: str, status: str, content: str):
        """
        Sends a notification about a component's status to a predefined webhook.

        Parameters
        ----------
        url : str
            The URL of the component that is being monitored.
        status : str
            The status of the component (e.g., "offline", "online").
        content : str
            Additional content or message to be included in the notification.

        Raises
        ------
        RuntimeError
            If the notification fails to send due to an HTTP error or network issue.
        """
        notify_webhook_url = WEBHOOK_URL + "/notify"
        data = {"url": url, "status": status, "content": content}
        try:
            response = requests.post(url=notify_webhook_url, json=data)
            response.raise_for_status()  # check if there has been an HTTP error
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to notify: {str(e)}")
