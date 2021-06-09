class Config:
    def __init__(self):
        self.__configuration = {
            "bansos_id": 1,
            "filename": "captured_card.jpg",
            "nik": [210, 270, 0, 520],
            "nama": [285, 325, 20, 500],
            "face": [215, 590, 500, 800],
        }

    @property
    def configuration(self):
        return self.__configuration
