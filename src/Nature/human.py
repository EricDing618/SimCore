from src.base import *
class Human(SimCoreBaseObject):
    def __init__(self,
                 name: str,
                 height: float = 170.0,
                 weight: float = 50.0,
                 gender: str = "male",
                 nationality: str = "unknown",
                 birthdate: str = "2000-01-01",
                 ):
        self.name = name
        self.height = height  # in cm
        self.weight = weight  # in kg
        self.gender = gender
        self.nationality = nationality
        self.birthdate = birthdate