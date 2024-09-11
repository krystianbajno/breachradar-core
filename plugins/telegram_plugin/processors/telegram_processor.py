# /plugins/telegram_plugin/processors/telegram_processor.py
from core.processors.processor_interface import ProcessorInterface

class TelegramProcessor(ProcessorInterface):
    def process(self, scrap):
        print(f"Processing Telegram scrap: {scrap.hash}")
        # Add specific processing logic here
