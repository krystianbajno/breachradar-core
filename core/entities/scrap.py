class Scrap:
    def __init__(self, source=None, content=None, attachments=None, state="NEW", filename=None, file_path=None, hash=None, timestamp=None):
        self.source = source
        self.content = content
        self.filename = filename
        self.file_path = file_path
        self.attachments = attachments if attachments else []
        self.state = state
        self.hash = hash
        self.timestamp = timestamp
