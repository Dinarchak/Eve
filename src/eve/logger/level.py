from enum import IntEnum

# уровни логов
class Level(IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40

    @classmethod
    def parse(cls, value: "str | Level | int") -> "Level":
        if isinstance(value, Level):
            return value
        
        if isinstance(value, int):
            try:
                return cls(value)
            except:
                raise ValueError(f'Uncknown log level: {value}')
            
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except:
                raise ValueError(f'Uncknown log level: {value}')
            
        raise TypeError(f'Invalid level type: {type(value)}')
