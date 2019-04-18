from enum import Enum, auto

class Material(Enum):
    FOOD = auto()
    WOOD = auto()
    STONE = auto()
    IRON = auto()

class Asset(Enum):
    WORKER = auto()
    HOUSE = auto()
    FARM = auto()
    WOODWORK = auto()
    QUARRY = auto()
    MINE = auto()   