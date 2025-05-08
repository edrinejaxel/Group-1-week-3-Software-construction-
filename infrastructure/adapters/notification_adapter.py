from abc import ABC, abstractmethod
import logging

class NotificationAdapter(ABC):
    @abstractmethod
    def send_notification(self, recipient: str, message: str) -> None:
        pass

class MockNotificationAdapter(NotificationAdapter):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_notification(self, recipient: str, message: str) -> None:
        self.logger.info(f"Sending notification to {recipient}: {message}")