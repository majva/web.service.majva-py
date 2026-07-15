from .elk.elk import ELK
from .stdout_log.stdout_log import StdoutLog


class LogManager:

    def __init__(self, instance: str, vault_service):
        if instance == "elk":
            self._instance = ELK(vault_service)
        else:
            self._instance = StdoutLog()
    
    def instance(self):
        return self._instance