import json
from typing import Dict, Any


class JSONFormatter:
    def __init__(self, indent: int = 2):
        self.indent = indent
    
    def format(self, summary: Dict[str, Any]) -> str:
        return json.dumps(summary, indent=self.indent, ensure_ascii=False)
