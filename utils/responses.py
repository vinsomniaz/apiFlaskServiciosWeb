from typing import Any, Dict

def build_response(success: bool, data: Any = None, message: str = "") -> Dict[str, Any]:
    return {"success": success, "data": data, "message": message}
