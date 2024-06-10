class StrategyTemplate:
    def __init__(self, client):
        self.client = client

    def apply_strategy(self):
        raise NotImplementedError("You should implement this method.")
