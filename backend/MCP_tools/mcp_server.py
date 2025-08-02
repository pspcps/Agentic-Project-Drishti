import json
import logging
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, List
from MCP_tools import db_tools
import aiohttp
import requests
from MCP_tools.mcp_tools_registry import ALL_TOOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class MCPServer:
    def __init__(self):
        self.tools = ALL_TOOLS

    def handle_request(self, request_data: Dict) -> Dict:
        """Handles JSON-RPC requests following standard MCP protocol."""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")

            if method == "tools/list":
                # Standard MCP tools/list method
                tools_list = []
                for name, tool_info in self.tools.items():
                    schema = tool_info.get("schema", {})
                    tools_list.append({
                        "name": name,
                        "description": schema.get("description", f"Tool: {name}"),
                        "inputSchema": {
                            "type": "object",
                            "properties": schema.get("parameters", {}),
                            "required": [k for k, v in schema.get("parameters", {}).items() if v.get("required", False)]
                        }
                    })
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": tools_list
                    },
                    "id": request_id
                }
                logger.info(f"[MCPServer] Listed tools: {len(tools_list)} tools")
                return response

            elif method == "tools/call":
                # Standard MCP tools/call method
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name]["function"](**arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, default=str)
                                    }
                                ]
                            },
                            "id": request_id
                        }
                        logger.info(f"[MCPServer] Executed {tool_name} with args {arguments}: {result}")
                        return response
                    except Exception as e:
                        logger.error(f"[MCPServer] Tool execution error: {str(e)}")
                        return {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32603,
                                "message": f"Tool execution failed: {str(e)}"
                            },
                            "id": request_id
                        }
                else:
                    logger.error(f"[MCPServer] Tool {tool_name} not found")
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32601,
                            "message": f"Tool {tool_name} not found"
                        },
                        "id": request_id
                    }

            else:
                logger.error(f"[MCPServer] Method {method} not found")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method {method} not found"
                    },
                    "id": request_id
                }

        except Exception as e:
            logger.error(f"[MCPServer] Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": str(e)
                },
                "id": request_id
            }

class MCPClient:
    def __init__(self, server_url: str = "http://localhost:8080/mcp/mcp_server"):
        self.server_url = server_url

    def discover_tools(self) -> Dict[str, Any]:
        """Discovers available tools from the MCP server using standard MCP protocol."""
        try:
            response = requests.post(self.server_url, json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            })
            data = response.json()
            logger.info(f"[MCPClient] Discover response: {data}")
            return data
        except Exception as e:
            logger.error(f"[MCPClient] Discover error: {str(e)}")
            raise

    def call_tool(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calls a tool on the MCP server using standard MCP protocol."""
        try:
            response = requests.post(self.server_url, json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": method,
                    "arguments": params
                },
                "id": 2
            })
            data = response.json()
            logger.info(f"[MCPClient] Tool call response for {method}: {data}")
            return data
        except Exception as e:
            logger.error(f"[MCPClient] Tool call error: {str(e)}")
            raise

    async def close(self):
        logger.info("[MCPClient] Closing...")
        if hasattr(self, 'session'):
            await self.session.close()

# FastAPI endpoint for MCP server
mcp_server = MCPServer()

@router.post("/mcp_server")
async def mcp_endpoint(request: Request):
    try:
        request_data = await request.json()
        response = mcp_server.handle_request(request_data)
        return response
    except Exception as e:
        logger.error(f"[MCPServer] Endpoint error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))