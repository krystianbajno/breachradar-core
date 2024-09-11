class Scrap:
    def __init__(self, source, content=None, attachments=None, state="NEW"):
        self.source = source
        self.content = content
        self.attachments = attachments if attachments else []
        self.state = state
        self.hash = self.generate_hash()

    def generate_hash(self):
        return hash(self.content or self.source)
