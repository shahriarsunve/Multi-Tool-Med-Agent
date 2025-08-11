from typing import Any, Dict

class Tool:
    name: str = "base"
    def describe(self) -> str:
        return "Base tool"
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
