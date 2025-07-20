from enum import Enum


class BaseEnum(Enum):
    pass

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
    @classmethod
    def values(cls):
        return [item.value for item in cls]
