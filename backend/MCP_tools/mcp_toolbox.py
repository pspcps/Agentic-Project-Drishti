from MCP_tools.mcp_server import MCPClient
import json

class ToolboxSyncClient:
    def __init__(self, server_url="https://gcp-crowd-agents-mcp-268678901849.us-central1.run.app/mcp/mcp_server"):
        self.client = MCPClient(server_url)

    def load_tool(self, tool_name):
        """Return a callable for a single tool by name."""
        def tool_func(**kwargs):
            response = self.client.call_tool(tool_name, kwargs)
            if "result" in response and "content" in response["result"]:
                # Extract text content from MCP response
                content = response["result"]["content"]
                if content and len(content) > 0:
                    return json.loads(content[0]["text"])
                else:
                    return None
            elif "result" in response:
                return response["result"]
            else:
                raise Exception(f"Tool call failed: {response}")
        return tool_func

    def load_toolset(self):
        """Return a dict of all tool callables, keyed by tool name."""
        tools_info = self.client.discover_tools()
        toolset = {}
        if "result" in tools_info and "tools" in tools_info["result"]:
            for tool in tools_info["result"]["tools"]:
                name = tool["name"]
                toolset[name] = self.load_tool(name)
        return toolset

# Example usage:
# toolbox = ToolboxSyncClient("http://localhost:8080/mcp/mcp_server")
# tools = toolbox.load_toolset()
# result = tools['fetch_incidents']()
# result2 = tools['assign_responder_to_incident'](incident_id='abc', responder_id='xyz') 