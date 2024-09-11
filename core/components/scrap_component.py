from core.entities.scrap import Scrap

class ScrapComponent:
    def __init__(self, scrap: Scrap):
        self.scrap = scrap

    def update_state(self, new_state):
        self.scrap.state = new_state
