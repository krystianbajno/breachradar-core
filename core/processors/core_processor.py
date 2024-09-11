import re

class CoreProcessor:
    def __init__(self, repository):
        self.repository = repository

    def get_regexes(self):
        """Load regexes from the database."""
        return self.repository.get_credential_regexes()

    def check_for_credentials(self, content):
        """Check for credentials using regex patterns."""
        found_credentials = []
        for pattern in self.get_regexes():
            matches = re.findall(pattern, content)
            if matches:
                found_credentials.extend(matches)
        return found_credentials
