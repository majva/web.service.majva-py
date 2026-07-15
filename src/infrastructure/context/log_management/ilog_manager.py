
from abc import ABC, abstractmethod

class ILogManager(ABC):

    @abstractmethod
    def set_log(self, message: str, from_file: str, line: int, type: str) -> bool:
        pass
