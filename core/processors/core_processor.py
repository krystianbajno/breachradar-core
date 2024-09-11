import re

class CoreProcessor:
    def __init__(self, repository):
        self.repository = repository

    def get_regexes(self):
        return self.repository.get_credential_regexes()

    def check_for_credentials(self, content):
        found_credentials = []
        for pattern in self.get_regexes():
            matches = re.findall(pattern, content)
            if matches:
                found_credentials.extend(matches)
        return found_credentials
