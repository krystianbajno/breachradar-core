# /plugins/telegram_plugin/services/telegram_service.py
from telethon import TelegramClient
import os

class TelegramService:
    def __init__(self, identity):
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)
        self.identity = identity

    def connect(self):
        self.client.start()

    def get_channels(self):
        return self.client.get_dialogs()

    def fetch_messages(self, channel_id, last_cursor):
        return self.client.get_messages(channel_id, min_id=last_cursor)
