
from src.infrastructure.context.log_management import ILogManager

from sys import stdout
import logging
from datetime import datetime, timezone


class StdoutLog(ILogManager):

    def __init__(self):
        super(StdoutLog, self).__init__()
        stdout_handler = logging.StreamHandler(stream=stdout)
        handlers = [stdout_handler]
        logging.basicConfig(
            level=logging.NOTSET, 
            format='[%(asctime)s] %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger('snapp.dvs.dc.bot')

    def set_log(self, message: str, from_file: str, line: int, type: str) -> bool:
        data = {
            "type": type,
            "message": message,
            "line": line,
            "from_file": from_file,
            "datetime_utc": datetime.now(timezone.utc),
            "datetime_local": datetime.now()
        }
        self.logger.info(data)
