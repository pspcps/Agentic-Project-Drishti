from google.adk.agents import LlmAgent
from google.adk.runners import InMemorySessionService, Runner
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.adk.tools import FunctionTool
from tools import db_tools
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

class AgentServiceDirect:
    """Direct local approach without MCP - uses db_tools functions directly."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentServiceDirect, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing tools for LlmAgent using direct local approach...")
        self.session_service = InMemorySessionService()
        self.app_name = "gcp_crowd_agents"
        self.user_id = "default_user"

        # Create FunctionTool objects directly from db_tools functions
        # No MCP involved - direct local function calls
        self.tools = [
            FunctionTool(func=db_tools.fetch_incidents),
            FunctionTool(func=db_tools.get_active_incidents),
            FunctionTool(func=db_tools.fetch_zones),
            FunctionTool(func=db_tools.fetch_responders),
            FunctionTool(func=db_tools.get_available_responders),
            FunctionTool(func=db_tools.fetch_alerts),
            FunctionTool(func=db_tools.analyze_responder_assignments),
            FunctionTool(func=db_tools.assign_responder_to_incident),
            FunctionTool(func=db_tools.assign_any_responder_to_incident),
            FunctionTool(func=db_tools.assign_responder_to_zone),
            FunctionTool(func=db_tools.assign_any_responder_to_zone),
            FunctionTool(func=db_tools.notify_unavailable),
            FunctionTool(func=db_tools.suggest_zones_needing_responders),
            FunctionTool(func=db_tools.get_incidents_for_responder),
            FunctionTool(func=db_tools.get_incidents_details_for_responder),
            FunctionTool(func=db_tools.get_incident_by_id),
            FunctionTool(func=db_tools.get_incidents_by_status),
            FunctionTool(func=db_tools.get_incidents_by_zone),
            FunctionTool(func=db_tools.get_responders_assigned_to_incident),
            FunctionTool(func=db_tools.fetch_venues),
            FunctionTool(func=db_tools.get_venue_by_id),
            FunctionTool(func=db_tools.create_venue),
            FunctionTool(func=db_tools.update_venue),
            FunctionTool(func=db_tools.delete_venue),
            FunctionTool(func=db_tools.fetch_events),
            FunctionTool(func=db_tools.get_event_by_id),
            FunctionTool(func=db_tools.get_events_by_venue),
            FunctionTool(func=db_tools.create_event),
            FunctionTool(func=db_tools.update_event),
            FunctionTool(func=db_tools.delete_event),
            FunctionTool(func=db_tools.fetch_event_responders),
            FunctionTool(func=db_tools.get_event_responders_by_event),
            FunctionTool(func=db_tools.get_event_responders_by_responder),
            FunctionTool(func=db_tools.create_event_responder),
            FunctionTool(func=db_tools.delete_event_responder),
            FunctionTool(func=db_tools.fetch_user_details),
            FunctionTool(func=db_tools.get_user_by_id),
            FunctionTool(func=db_tools.get_user_by_responder_id),
            FunctionTool(func=db_tools.create_user),
            FunctionTool(func=db_tools.update_user),
            FunctionTool(func=db_tools.delete_user),
            FunctionTool(func=db_tools.authenticate_user)
        ]
        
        logger.info(f"Created {len(self.tools)} direct FunctionTool objects for LlmAgent")
        logger.info(f"Tool names: {[tool.func.__name__ for tool in self.tools]}")

        model_name = os.getenv("VERTEX_MODEL", "gemini-1.5-pro")
        agent_name = os.getenv("AGENT_NAME", "crowd_agent")
        logger.info(f"Initializing LlmAgent with model: {model_name}, name: {agent_name}")

        try:
            self.llm_agent = LlmAgent(
                model=model_name,
                name=agent_name,
                instruction=(
                    "You are an event safety AI assistant. Use the available tools to handle user queries. "
                    "Tools are available locally and can be called by name with parameters. "
                    "Use the tool schemas for guidance on arguments and expected results."
                ),
                tools=self.tools  # Pass the list of direct FunctionTool objects
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
        logger.info("[AgentServiceDirect] Initialization complete.")

    def call_tool(self, tool_name, **kwargs):
        """Call a tool by name with parameters, with detailed logging and error handling."""
        logger.info(f"Calling direct tool: {tool_name} with params: {kwargs}")
        
        # Find the tool by function name
        tool_obj = None
        for tool in self.tools:
            if hasattr(tool, 'func') and tool.func.__name__ == tool_name:
                tool_obj = tool
                break
        
        if tool_obj is None:
            logger.error(f"Tool '{tool_name}' not found in LlmAgent tools.")
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        try:
            # Call the direct FunctionTool (local function call)
            result = tool_obj(**kwargs)
            logger.info(f"Direct tool '{tool_name}' result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error calling direct tool '{tool_name}' with params {kwargs}: {str(e)}")
            raise

    # ... rest of the methods same as AgentService ... 