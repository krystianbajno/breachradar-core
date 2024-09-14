# core/processors/core_processor.py
import re

class CoreProcessor:
    def __init__(self, repository):
        self.repository = repository
        self.patterns = self.load_patterns()

    def load_patterns(self):
        return self.repository.get_credential_patterns()

    def check_for_credentials(self, content):
        credentials = []
        for pattern in self.patterns:
            matches = re.findall(pattern, content)
            credentials.extend(matches)
        return credentials if credentials else None
