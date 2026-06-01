import json
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionLogger:
    def __init__(self, log_dir: str = "logs"):
        Path(log_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = Path(log_dir) / f"session_{timestamp}.log"

    def log(self, event: str, data: Any = None):
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "event": event,
            "data": data,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False, indent=2))
            file.write("\n\n")

    def log_text(self, title: str, text: str):
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"[{datetime.now().isoformat(timespec='seconds')}] {title}\n")
            file.write(text)
            file.write("\n\n")
