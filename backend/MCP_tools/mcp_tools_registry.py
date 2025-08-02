from MCP_tools import db_tools

ALL_TOOLS = {
    # Incident tools
    "fetch_incidents": {
        "function": db_tools.fetch_incidents,
        "schema": {
            "name": "fetch_incidents",
            "description": "Fetches all incidents from Firestore.",
            "parameters": {},
            "returns": "List[Incident]"
        }
    },
    "get_active_incidents": {
        "function": db_tools.get_active_incidents,
        "schema": {
            "name": "get_active_incidents",
            "description": "Return all incidents whose status is not 'close'.",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "fetch_zones": {
        "function": db_tools.fetch_zones,
        "schema": {
            "name": "fetch_zones",
            "description": "Fetches all zones from Firestore.",
            "parameters": {},
            "returns": "List[Zone]"
        }
    },
    "fetch_responders": {
        "function": db_tools.fetch_responders,
        "schema": {
            "name": "fetch_responders",
            "description": "Fetches all responders from Firestore, including their latest status from responder_incident_status if available. If not, use responder doc status or default to 'active'.",
            "parameters": {},
            "returns": "List[Responder]"
        }
    },
    "get_available_responders": {
        "function": db_tools.get_available_responders,
        "schema": {
            "name": "get_available_responders",
            "description": "Return only responders whose latest status event is 'active', or if no event, whose responder doc status is 'active' or missing (default to active).",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "fetch_alerts": {
        "function": db_tools.fetch_alerts,
        "schema": {
            "name": "fetch_alerts",
            "description": "Fetches all alerts from Firestore.",
            "parameters": {},
            "returns": "List[Alert]"
        }
    },
    "analyze_responder_assignments": {
        "function": db_tools.analyze_responder_assignments,
        "schema": {
            "name": "analyze_responder_assignments",
            "description": "Analyzes all responders in the system.",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "assign_responder_to_incident": {
        "function": db_tools.assign_responder_to_incident,
        "schema": {
            "name": "assign_responder_to_incident",
            "description": "Assigns a responder to the specified incident by writing an event to responder_incident_status. If responder_id is not provided, picks the first available responder.",
            "parameters": {
                "incident_id": {"type": "string", "required": True},
                "responder_id": {"type": "string", "required": False}
            },
            "returns": "Dict[str, str]"
        }
    },
    "assign_any_responder_to_incident": {
        "function": db_tools.assign_any_responder_to_incident,
        "schema": {
            "name": "assign_any_responder_to_incident",
            "description": "Assign any available responder to the specified incident by writing an event to responder_incident_status.",
            "parameters": {
                "incident_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, Any]"
        }
    },
    "assign_responder_to_zone": {
        "function": db_tools.assign_responder_to_zone,
        "schema": {
            "name": "assign_responder_to_zone",
            "description": "Assigns a responder to a zone by writing an event to responder_incident_status.",
            "parameters": {
                "responder_id": {"type": "string", "required": True},
                "zone_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, str]"
        }
    },
    "assign_any_responder_to_zone": {
        "function": db_tools.assign_any_responder_to_zone,
        "schema": {
            "name": "assign_any_responder_to_zone",
            "description": "Assign any available responder to the given zone by writing an event to responder_incident_status.",
            "parameters": {
                "zone_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, Any]"
        }
    },
    "notify_unavailable": {
        "function": db_tools.notify_unavailable,
        "schema": {
            "name": "notify_unavailable",
            "description": "Logs an alert in Firestore if no responder is available for a zone (event-driven).",
            "parameters": {
                "zone_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, str]"
        }
    },
    "suggest_zones_needing_responders": {
        "function": db_tools.suggest_zones_needing_responders,
        "schema": {
            "name": "suggest_zones_needing_responders",
            "description": "Suggest zones that need more responders based on incidents and current assignments. Placeholder logic.",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "get_incident_by_id": {
        "function": db_tools.get_incident_by_id,
        "schema": {
            "name": "get_incident_by_id",
            "description": "Get a single incident by ID.",
            "parameters": {
                "incident_id": {"type": "string", "required": True}
            },
            "returns": "Incident"
        }
    },
    "get_incidents_by_status": {
        "function": db_tools.get_incidents_by_status,
        "schema": {
            "name": "get_incidents_by_status",
            "description": "Get all incidents by status.",
            "parameters": {
                "status": {"type": "string", "required": True}
            },
            "returns": "Dict[str, Any]"
        }
    },
    "get_incidents_by_zone": {
        "function": db_tools.get_incidents_by_zone,
        "schema": {
            "name": "get_incidents_by_zone",
            "description": "Get all incidents for a zone.",
            "parameters": {
                "zone_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, Any]"
        }
    },
    "get_responders_assigned_to_incident": {
        "function": db_tools.get_responders_assigned_to_incident,
        "schema": {
            "name": "get_responders_assigned_to_incident",
            "description": "Fetch all responders assigned to a given incident using responder_incident_status.",
            "parameters": {
                "incident_id": {"type": "string", "required": True}
            },
            "returns": "List[Responder]"
        }
    },
    "get_all_incident_reports": {
        "function": db_tools.get_all_incident_reports,
        "schema": {
            "name": "get_all_incident_reports",
            "description": "Fetch all incident reports.",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "get_incident_reports_by_venue": {
        "function": db_tools.get_incident_reports_by_venue,
        "schema": {
            "name": "get_incident_reports_by_venue",
            "description": "Fetch incident reports by venue.",
            "parameters": {
                "venue_id": {"type": "string", "required": True}
            },
            "returns": "Dict[str, Any]"
        }
    },
    "get_incident_statistics": {
        "function": db_tools.get_incident_statistics,
        "schema": {
            "name": "get_incident_statistics",
            "description": "Get incident statistics.",
            "parameters": {},
            "returns": "Dict[str, Any]"
        }
    },
    "get_incidents_for_responder": {
        "function": db_tools.get_incidents_for_responder,
        "schema": {
            "name": "get_incidents_for_responder",
            "description": "Fetch all incidents for a given responder based on responder_incident_status.",
            "parameters": {
                "responder_id": {"type": "string", "required": True}
            },
            "returns": "List[Incident]"
        }
    },
    "get_incidents_details_for_responder": {
        "function": db_tools.get_incidents_details_for_responder,
        "schema": {
            "name": "get_incidents_details_for_responder",
            "description": "Fetch full incident details for a given responder from incident collection.",
            "parameters": {
                "responder_id": {"type": "string", "required": True}
            },
            "returns": "List[Incident]"
        }
    },
    # Venue CRUD
    "fetch_venues": {
        "function": db_tools.fetch_venues,
        "schema": {
            "name": "fetch_venues",
            "description": "Fetches all venues from Firestore.",
            "parameters": {},
            "returns": "List[Venue]"
        }
    },
    "get_venue_by_id": {
        "function": db_tools.get_venue_by_id,
        "schema": {
            "name": "get_venue_by_id",
            "description": "Get a single venue by ID.",
            "parameters": {"venue_id": {"type": "string", "required": True}},
            "returns": "Venue"
        }
    },
    "create_venue": {
        "function": db_tools.create_venue,
        "schema": {
            "name": "create_venue",
            "description": "Create a new venue.",
            "parameters": {"venue_data": {"type": "object", "required": True}},
            "returns": "Venue"
        }
    },
    "update_venue": {
        "function": db_tools.update_venue,
        "schema": {
            "name": "update_venue",
            "description": "Update an existing venue.",
            "parameters": {"venue_id": {"type": "string", "required": True}, "updates": {"type": "object", "required": True}},
            "returns": "Venue"
        }
    },
    "delete_venue": {
        "function": db_tools.delete_venue,
        "schema": {
            "name": "delete_venue",
            "description": "Delete a venue.",
            "parameters": {"venue_id": {"type": "string", "required": True}},
            "returns": "Dict[str, Any]"
        }
    },
    # Event CRUD
    "fetch_events": {
        "function": db_tools.fetch_events,
        "schema": {
            "name": "fetch_events",
            "description": "Fetches all events from Firestore.",
            "parameters": {},
            "returns": "List[Event]"
        }
    },
    "get_event_by_id": {
        "function": db_tools.get_event_by_id,
        "schema": {
            "name": "get_event_by_id",
            "description": "Get a single event by ID.",
            "parameters": {"event_id": {"type": "string", "required": True}},
            "returns": "Event"
        }
    },
    "get_events_by_venue": {
        "function": db_tools.get_events_by_venue,
        "schema": {
            "name": "get_events_by_venue",
            "description": "Get all events for a specific venue.",
            "parameters": {"venue_id": {"type": "string", "required": True}},
            "returns": "List[Event]"
        }
    },
    "create_event": {
        "function": db_tools.create_event,
        "schema": {
            "name": "create_event",
            "description": "Create a new event.",
            "parameters": {"event_data": {"type": "object", "required": True}},
            "returns": "Event"
        }
    },
    "update_event": {
        "function": db_tools.update_event,
        "schema": {
            "name": "update_event",
            "description": "Update an existing event.",
            "parameters": {"event_id": {"type": "string", "required": True}, "updates": {"type": "object", "required": True}},
            "returns": "Event"
        }
    },
    "delete_event": {
        "function": db_tools.delete_event,
        "schema": {
            "name": "delete_event",
            "description": "Delete an event.",
            "parameters": {"event_id": {"type": "string", "required": True}},
            "returns": "Dict[str, Any]"
        }
    },
    # EventResponder CRUD
    "fetch_event_responders": {
        "function": db_tools.fetch_event_responders,
        "schema": {
            "name": "fetch_event_responders",
            "description": "Fetches all event responder assignments from Firestore.",
            "parameters": {},
            "returns": "List[EventResponder]"
        }
    },
    "get_event_responders_by_event": {
        "function": db_tools.get_event_responders_by_event,
        "schema": {
            "name": "get_event_responders_by_event",
            "description": "Get all responder assignments for a specific event.",
            "parameters": {"event_id": {"type": "string", "required": True}},
            "returns": "List[EventResponder]"
        }
    },
    "get_event_responders_by_responder": {
        "function": db_tools.get_event_responders_by_responder,
        "schema": {
            "name": "get_event_responders_by_responder",
            "description": "Get all event assignments for a specific responder.",
            "parameters": {"responder_id": {"type": "string", "required": True}},
            "returns": "List[EventResponder]"
        }
    },
    "create_event_responder": {
        "function": db_tools.create_event_responder,
        "schema": {
            "name": "create_event_responder",
            "description": "Create a new event responder assignment.",
            "parameters": {"event_responder_data": {"type": "object", "required": True}},
            "returns": "EventResponder"
        }
    },
    "delete_event_responder": {
        "function": db_tools.delete_event_responder,
        "schema": {
            "name": "delete_event_responder",
            "description": "Delete an event responder assignment.",
            "parameters": {"event_responder_id": {"type": "string", "required": True}},
            "returns": "Dict[str, Any]"
        }
    },
    # UserDetails CRUD
    "fetch_user_details": {
        "function": db_tools.fetch_user_details,
        "schema": {
            "name": "fetch_user_details",
            "description": "Fetches all user details from Firestore.",
            "parameters": {},
            "returns": "List[UserDetails]"
        }
    },
    "get_user_by_id": {
        "function": db_tools.get_user_by_id,
        "schema": {
            "name": "get_user_by_id",
            "description": "Get a single user by userId.",
            "parameters": {"user_id": {"type": "string", "required": True}},
            "returns": "UserDetails"
        }
    },
    "get_user_by_responder_id": {
        "function": db_tools.get_user_by_responder_id,
        "schema": {
            "name": "get_user_by_responder_id",
            "description": "Get a user by responder_id.",
            "parameters": {"responder_id": {"type": "string", "required": True}},
            "returns": "UserDetails"
        }
    },
    "create_user": {
        "function": db_tools.create_user,
        "schema": {
            "name": "create_user",
            "description": "Create a new user.",
            "parameters": {"user_data": {"type": "object", "required": True}},
            "returns": "UserDetails"
        }
    },
    "update_user": {
        "function": db_tools.update_user,
        "schema": {
            "name": "update_user",
            "description": "Update an existing user.",
            "parameters": {"user_id": {"type": "string", "required": True}, "updates": {"type": "object", "required": True}},
            "returns": "UserDetails"
        }
    },
    "delete_user": {
        "function": db_tools.delete_user,
        "schema": {
            "name": "delete_user",
            "description": "Delete a user.",
            "parameters": {"user_id": {"type": "string", "required": True}},
            "returns": "Dict[str, Any]"
        }
    },
    "authenticate_user": {
        "function": db_tools.authenticate_user,
        "schema": {
            "name": "authenticate_user",
            "description": "Authenticate a user with userId and password.",
            "parameters": {"user_id": {"type": "string", "required": True}, "password": {"type": "string", "required": True}},
            "returns": "Dict[str, Any]"
        }
    }
} 