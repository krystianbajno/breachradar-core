# /plugins/telegram_plugin/collectors/telegram_collector.py
from plugins.telegram_plugin.services.telegram_service import TelegramService
from core.collectors.collector_interface import CollectorInterface
from core.models.scrap import Scrap
from core.database.postgres_repository import PostgresRepository

class TelegramCollector(CollectorInterface):
    def __init__(self, identity, event_system):
        self.source = TelegramService(identity)
        self.repository = PostgresRepository()
        self.event_system = event_system

    def collect(self):
        for channel in self.source.get_channels():
            last_cursor = self.repository.get_last_cursor(channel.id)
            messages = self.source.fetch_messages(channel.id, last_cursor)
            for message in messages:
                scrap = Scrap(
                    source='telegram',
                    content=message.text,
                    attachments=self.process_attachments(message.attachments)
                )
                self.repository.save_scrap(scrap)
                self.event_system.trigger_event('NEW_SCRAPE', scrap)

    def process_attachments(self, attachments):
        processed_attachments = []
        for attachment in attachments:
            processed_attachments.append(self.process_attachment(attachment))
        return processed_attachments

    def process_attachment(self, attachment):
        # Logic for processing individual attachments
        return attachment
