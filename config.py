class Config:
    def __init__(self):
        self.__configuration = {
            "filename": "captured_card.jpg",
            "nik": [600, 800, 860, 2230],
            "face": [670, 1620, 2300, 3100],
        }

    @property
    def configuration(self):
        return self.__configuration
