import os
import json
import time
import logging
import re
import asyncio
from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.runners import InMemorySessionService, Runner
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.adk.tools import FunctionTool
from utils.mcp_toolbox import ToolboxSyncClient
import os
import logging
import json
import time
import re
from typing import Dict, Any, List

# Configure logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(handler)

class AgentService:
    """Singleton class to manage shared LlmAgent, Runner, and InMemorySessionService, using MCP toolbox for tool access."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing tools for LlmAgent using pure MCP approach...")
        self.session_service = InMemorySessionService()
        self.app_name = "gcp_crowd_agents"
        self.user_id = "default_user"

        # Use MCP toolbox for all tool access
        toolbox = ToolboxSyncClient("https://gcp-crowd-agents-mcp-268678901849.us-central1.run.app/mcp/mcp_server")
        self.tools_dict = toolbox.load_toolset()  # Dict of tool callables
        logger.info(f"Registered MCP tools: {list(self.tools_dict.keys())}")

        # Create FunctionTool objects that call MCP server
        # This way the agent actually uses MCP for tool execution
        self.tools = []
        
        # Create FunctionTool wrappers for MCP callables
        for tool_name, mcp_callable in self.tools_dict.items():
            try:
                logger.info(f"Creating MCP FunctionTool for: {tool_name}")
                
                # Get the tool description from the MCP tools registry
                from utils.mcp_tools_registry import ALL_TOOLS
                tool_description = "Tool function"
                if tool_name in ALL_TOOLS:
                    schema = ALL_TOOLS[tool_name].get("schema", {})
                    tool_description = schema.get("description", f"Tool: {tool_name}")
                
                # Create a wrapper function that calls the MCP server
                def create_mcp_wrapper(tool_name, mcp_callable, description):
                    def wrapper(**kwargs):
                        logger.info(f"Calling MCP tool: {tool_name} with params: {kwargs}")
                        try:
                            result = mcp_callable(**kwargs)
                            logger.info(f"MCP tool {tool_name} result: {result}")
                            return result
                        except Exception as e:
                            logger.error(f"MCP tool {tool_name} error: {str(e)}")
                            raise
                    return wrapper
                
                # Create the wrapper function
                wrapper_func = create_mcp_wrapper(tool_name, mcp_callable, tool_description)
                wrapper_func.__name__ = tool_name
                wrapper_func.__doc__ = tool_description  # Use proper description
                
                # Create FunctionTool with the wrapper
                func_tool = FunctionTool(func=wrapper_func)
                func_tool.name = tool_name
                self.tools.append(func_tool)
                logger.info(f"Successfully created MCP FunctionTool: {tool_name} with description: {tool_description}")
                
                # Test the tool to see if it has proper function declaration
                try:
                    declaration = func_tool._get_declaration()
                    logger.info(f"MCP FunctionTool {tool_name} declaration: {declaration}")
                except Exception as decl_error:
                    logger.warning(f"MCP FunctionTool {tool_name} declaration error: {str(decl_error)}")
                    
            except Exception as e:
                logger.error(f"Failed to create MCP FunctionTool for {tool_name}: {str(e)}")
        
        logger.info(f"Created {len(self.tools)} MCP FunctionTool objects for LlmAgent")
        logger.info(f"Tool names: {[getattr(tool, 'name', 'unknown') for tool in self.tools]}")

        model_name = os.getenv("VERTEX_MODEL", "gemini-1.5-pro")
        agent_name = os.getenv("AGENT_NAME", "crowd_agent")
        logger.info(f"Initializing LlmAgent with model: {model_name}, name: {agent_name}")

        try:
            self.llm_agent = LlmAgent(
                model=model_name,
                name=agent_name,
                instruction=(
                    "You are an event safety AI assistant. Use the available tools to handle user queries. "
                    "Tools are available via the MCP server and can be called by name with parameters. "
                    "Use the tool schemas for guidance on arguments and expected results."
                ),
                tools=self.tools  # Pass the list of MCP FunctionTool objects
            )
        except Exception as e:
            logger.error(f"Failed to initialize LlmAgent: {str(e)}")
            raise

        logger.info(f"Initializing Runner with app_name: {self.app_name}")
        try:
            self.runner = Runner(
                agent=self.llm_agent,
                session_service=self.session_service,
                app_name=self.app_name
            )
        except Exception as e:
            logger.error(f"Failed to initialize Runner: {str(e)}")
            raise

        self.initialized = True
        logger.info("[AgentService] Initialization complete.")

    async def ensure_session(self, session_id):
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=session_id
        )
        if session is None:
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=session_id,
                state={}
            )
        return session

    async def get_structured_context(self, session_id):
        session = await self.ensure_session(session_id)
        state = session.state if hasattr(session, 'state') else {}
        return state.get("structured_context", {})

    async def update_structured_context(self, session_id, user_query, llm_answer, prev_context):
        new_context = prev_context.copy() if prev_context else {}
        if "zone" in user_query.lower():
            match = re.search(r"zone\s*([a-zA-Z0-9]+)", user_query, re.IGNORECASE)
            if match:
                new_context["last_zone"] = match.group(1)
                new_context["last_intent"] = "zone_analysis"
        if "incident" in user_query.lower():
            new_context["last_intent"] = "incident_analysis"
        session = await self.ensure_session(session_id)
        state = session.state if hasattr(session, 'state') else {}
        state["structured_context"] = new_context
        session.state = state
        logger.info(f"Updated structured context: {new_context}")
        return new_context

    async def get_short_term_context(self, session_id):
        session = await self.ensure_session(session_id)
        all_session_events = session.events if hasattr(session, 'events') else []
        filtered_context = []
        for e in reversed(all_session_events):
            content_text = ""
            if isinstance(e.content, Content):
                for part in e.content.parts:
                    if isinstance(part, Part) and hasattr(part, 'text') and part.text is not None:
                        content_text += part.text
            elif isinstance(e.content, str):
                content_text = e.content
            if e.author == "user":
                filtered_context.append(f"User: {content_text}")
            elif e.author == "assistant":
                filtered_context.append(f"Assistant: {content_text}")
            if len(filtered_context) >= 10:
                break
        return "\n".join(reversed(filtered_context))

    def _sanitize_for_log(self, obj):
        # If it's a Content object, flatten its text
        if isinstance(obj, Content):
            return " | ".join([part.text.replace('\n', ' | ') if hasattr(part, 'text') and part.text else '' for part in obj.parts])
        # Handle EventActions
        if isinstance(obj, EventActions):
            return vars(obj)
        if isinstance(obj, dict):
            return {k: self._sanitize_for_log(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize_for_log(i) for i in obj]
        if isinstance(obj, str):
            return obj.replace('\n', ' | ')
        return obj

    async def append_event(self, session_id, event_data):
        session = await self.ensure_session(session_id)
        event_data = event_data.copy()
        event_data.setdefault("author", "system")
        event_data.setdefault("invocation_id", "default_event")
        event_data.setdefault("timestamp", int(time.time() * 1000))
        if "actions" not in event_data or not isinstance(event_data["actions"], EventActions):
            event_data["actions"] = EventActions()
        if "content" in event_data and isinstance(event_data["content"], str):
            event_data["content"] = Content(parts=[Part(text=event_data["content"])])
        elif "content" not in event_data:
            event_data["content"] = Content(parts=[Part(text="")])
        event_type = event_data.pop("type", None)
        sanitized_event_data = self._sanitize_for_log(event_data)
        logger.info(f"[AgentService] Creating event with: {json.dumps(sanitized_event_data, separators=(',', ':'))}, original type: {event_type}")
        try:
            event = Event(**event_data)
            await self.session_service.append_event(session, event)
            # Log session events after append
            logger.info(f"[AgentService] Session events after append: {[e for e in getattr(session, 'events', [])]}")
        except Exception as e:
            logger.error(f"[AgentService] Validation error details: {str(e)}")
            raise

    def call_tool(self, tool_name, **kwargs):
        """Call a tool by name with parameters, with detailed logging and error handling."""
        logger.info(f"Calling tool: {tool_name} with params: {kwargs}")
        
        # Find the tool by name
        tool_obj = None
        for tool in self.tools:
            tool_name_attr = getattr(tool, 'name', None)
            if tool_name_attr == tool_name:
                tool_obj = tool
                break
        
        if tool_obj is None:
            logger.error(f"Tool '{tool_name}' not found in LlmAgent tools.")
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        try:
            # Call the MCP FunctionTool (which will call the MCP server)
            result = tool_obj(**kwargs)
            logger.info(f"Tool '{tool_name}' result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' with params {kwargs}: {str(e)}")
            raise

    async def run_llm(self, prompt, session_id="default"):
        input_content = Content(
            role="user",
            parts=[Part(text=prompt)]
        )
        logger.info(f"[AgentService] Running LLM with prompt: {prompt}")
        answer = ""
        try:
            async for result_event in self.runner.run_async(
                user_id=self.user_id,
                session_id=session_id,
                new_message=input_content
            ):
                logger.info(f"Result event: {result_event}")
                if result_event.actions and hasattr(result_event.actions, "tool_call") and result_event.actions.tool_call:
                    logger.info(f"Tool call: name={result_event.actions.tool_call.name}, args={result_event.actions.tool_call.args}")
                if result_event.error_code:
                    logger.error(f"Error in result event: code={result_event.error_code}, message={result_event.error_message}")
                    logger.info(f"Full result event details: {vars(result_event)}")
                if isinstance(result_event.content, Content):
                    for part in result_event.content.parts:
                        logger.info(f"Processing Part: {vars(part)}")
                        if isinstance(part, Part) and hasattr(part, 'text') and part.text is not None:
                            answer += part.text
                        else:
                            logger.warning(f"Skipping Part with invalid or missing text: {vars(part)}")
        except Exception as e:
            logger.error(f"[AgentService] Error in run_llm: {str(e)}")
            raise
        logger.info(f"[AgentService] LLM answer: {answer}")
        return answer

    async def close(self):
        logger.info("[AgentService] Closing AgentService...")