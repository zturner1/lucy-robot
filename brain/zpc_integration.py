"""
ZPC Gateway Integration for Lucy
Allows Lucy to interact with the ZPC Gateway MCP server
"""

import requests
import json
from typing import Optional, Dict, Any

class ZPCGateway:
    """Interface to ZPC Gateway MCP server"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key

    def _check_health(self) -> Dict[str, Any]:
        """Check if ZPC Gateway is available"""
        try:
            resp = requests.get(f"{self.base_url}/healthz", timeout=3)
            return {"ok": True, "status": resp.json()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_system_status(self) -> str:
        """Get system CPU, RAM, disk usage"""
        try:
            # This would call the MCP tool via the gateway
            # For now, return placeholder
            health = self._check_health()
            if health["ok"]:
                return f"✅ ZPC Gateway is online\n{json.dumps(health['status'], indent=2)}"
            else:
                return f"❌ ZPC Gateway offline: {health['error']}"
        except Exception as e:
            return f"❌ Error: {e}"

    def search_knowledge_base(self, keyword: str, max_results: int = 5) -> str:
        """Search the knowledge base (vault)"""
        try:
            # Placeholder - would integrate with actual MCP call
            return f"🔍 Searching knowledge base for: {keyword}\n(Integration pending)"
        except Exception as e:
            return f"❌ Error: {e}"

    def get_comfyui_status(self) -> str:
        """Check ComfyUI status"""
        try:
            health = self._check_health()
            if not health["ok"]:
                return f"❌ Cannot check ComfyUI: Gateway offline"

            # Would call actual MCP tool
            return "🎨 ComfyUI status check (integration pending)"
        except Exception as e:
            return f"❌ Error: {e}"

    def capture_screenshot(self, monitor: int = 0) -> str:
        """Capture screenshot"""
        try:
            health = self._check_health()
            if not health["ok"]:
                return f"❌ Cannot capture screenshot: Gateway offline"

            # Would call actual MCP tool
            return f"📸 Screenshot capture (integration pending)"
        except Exception as e:
            return f"❌ Error: {e}"

    def get_home_assistant_context(self) -> str:
        """Get Home Assistant device status"""
        try:
            health = self._check_health()
            if not health["ok"]:
                return f"❌ Cannot get HA context: Gateway offline"

            # Would call actual MCP tool
            return "🏠 Home Assistant context (integration pending)"
        except Exception as e:
            return f"❌ Error: {e}"

# Factory function for Lucy tools
def create_zpc_tools(api_key: Optional[str] = None):
    """Create ZPC Gateway tool functions for Lucy"""
    gateway = ZPCGateway(api_key=api_key)

    def tool_zpc_health() -> str:
        """Check ZPC Gateway health"""
        return gateway.get_system_status()

    def tool_search_vault(keyword: str) -> str:
        """Search ZPC knowledge base/vault"""
        return gateway.search_knowledge_base(keyword)

    def tool_comfyui_status() -> str:
        """Check ComfyUI status"""
        return gateway.get_comfyui_status()

    def tool_screenshot(monitor: str = "0") -> str:
        """Capture screenshot from ZPC"""
        try:
            mon_num = int(monitor)
            return gateway.capture_screenshot(mon_num)
        except ValueError:
            return "❌ Monitor must be a number (0, 1, 2...)"

    def tool_ha_context() -> str:
        """Get Home Assistant device context"""
        return gateway.get_home_assistant_context()

    return {
        "zpc_health": tool_zpc_health,
        "search_vault": tool_search_vault,
        "comfyui_status": tool_comfyui_status,
        "screenshot": tool_screenshot,
        "ha_context": tool_ha_context,
    }

# Tool descriptions for LLM
ZPC_TOOL_DESCRIPTIONS = """
ZPC Gateway Tools (when available):
- TOOL: zpc_health - Check ZPC Gateway system status
- TOOL: search_vault | ARGS: <keyword> - Search the knowledge base vault
- TOOL: comfyui_status - Check if ComfyUI is running
- TOOL: screenshot | ARGS: [monitor] - Capture screenshot (0=all, 1=primary, etc.)
- TOOL: ha_context - Get Home Assistant device context
"""

if __name__ == "__main__":
    # Quick test
    print("Testing ZPC Gateway Integration...")
    gateway = ZPCGateway()
    print(gateway.get_system_status())
