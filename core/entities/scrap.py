# core/entities/scrap.py
from datetime import datetime

class Scrap:
    def __init__(self, id=None, hash=None, source=None, filename=None, file_path=None, state='NEW', timestamp=None, content=None, occurrence_time=None, attachments=None, elastic_id=None):
        self.id = id
        self.hash = hash
        self.source = source
        self.filename = filename
        self.file_path = file_path
        self.state = state
        self.timestamp = timestamp
        self.content = content
        self.occurrence_time = occurrence_time 
        self.attachments = attachments or []
