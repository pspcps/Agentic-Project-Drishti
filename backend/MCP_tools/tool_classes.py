from google.adk.tools import FunctionTool
from .db_tools import (
    # Existing functions
    fetch_incidents, get_active_incidents, fetch_zones, fetch_responders, get_available_responders,
    fetch_alerts, analyze_responder_assignments, assign_responder_to_incident, assign_any_responder_to_incident,
    assign_responder_to_zone, assign_any_responder_to_zone, notify_unavailable, suggest_zones_needing_responders,
    get_incidents_for_responder, get_incidents_details_for_responder,
    get_incident_by_id, get_incidents_by_status, get_incidents_by_zone, get_responders_assigned_to_incident,
    get_all_incident_reports, get_incident_reports_by_venue, get_incident_statistics,
    # New Venue functions
    fetch_venues, get_venue_by_id, create_venue, update_venue, delete_venue,
    # New Event functions
    fetch_events, get_event_by_id, get_events_by_venue, create_event, update_event, delete_event,
    # New EventResponder functions
    fetch_event_responders, get_event_responders_by_event, get_event_responders_by_responder,
    create_event_responder, delete_event_responder,
    # New UserDetails functions
    fetch_user_details, get_user_by_id, get_user_by_responder_id, create_user, update_user, delete_user,
    authenticate_user
)
import logging
from typing import Dict, Any, List

# Configure logging
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(handler)

# Existing Tool Classes
class FetchIncidentsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_incidents)

class GetActiveIncidentsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_active_incidents)

class FetchZonesTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_zones)

class FetchRespondersTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_responders)

class GetAvailableRespondersTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_available_responders)

class FetchAlertsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_alerts)

class AnalyzeResponderAssignmentsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=analyze_responder_assignments)

class AssignResponderToIncidentTool(FunctionTool):
    def __init__(self):
        super().__init__(func=assign_responder_to_incident)

class AssignAnyResponderToIncidentTool(FunctionTool):
    def __init__(self):
        super().__init__(func=assign_any_responder_to_incident)

class AssignResponderToZoneTool(FunctionTool):
    def __init__(self):
        super().__init__(func=assign_responder_to_zone)

class AssignAnyResponderToZoneTool(FunctionTool):
    def __init__(self):
        super().__init__(func=assign_any_responder_to_zone)

class NotifyUnavailableTool(FunctionTool):
    def __init__(self):
        super().__init__(func=notify_unavailable)

class SuggestZonesNeedingRespondersTool(FunctionTool):
    def __init__(self):
        super().__init__(func=suggest_zones_needing_responders)

class GetIncidentsForResponderTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incidents_for_responder)

class GetIncidentsDetailsForResponderTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incidents_details_for_responder)

# Incident-related Tool Classes
class GetIncidentByIdTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incident_by_id)

class GetIncidentsByStatusTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incidents_by_status)

class GetIncidentsByZoneTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incidents_by_zone)

class GetRespondersAssignedToIncidentTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_responders_assigned_to_incident)

class GetAllIncidentReportsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_all_incident_reports)

class GetIncidentReportsByVenueTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incident_reports_by_venue)

class GetIncidentStatisticsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_incident_statistics)

# Venue Tool Classes
class FetchVenuesTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_venues)

class GetVenueByIdTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_venue_by_id)

class CreateVenueTool(FunctionTool):
    def __init__(self):
        super().__init__(func=create_venue)

class UpdateVenueTool(FunctionTool):
    def __init__(self):
        super().__init__(func=update_venue)

class DeleteVenueTool(FunctionTool):
    def __init__(self):
        super().__init__(func=delete_venue)

# Event Tool Classes
class FetchEventsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_events)

class GetEventByIdTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_event_by_id)

class GetEventsByVenueTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_events_by_venue)

class CreateEventTool(FunctionTool):
    def __init__(self):
        super().__init__(func=create_event)

class UpdateEventTool(FunctionTool):
    def __init__(self):
        super().__init__(func=update_event)

class DeleteEventTool(FunctionTool):
    def __init__(self):
        super().__init__(func=delete_event)

# EventResponder Tool Classes
class FetchEventRespondersTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_event_responders)

class GetEventRespondersByEventTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_event_responders_by_event)

class GetEventRespondersByResponderTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_event_responders_by_responder)

class CreateEventResponderTool(FunctionTool):
    def __init__(self):
        super().__init__(func=create_event_responder)

class DeleteEventResponderTool(FunctionTool):
    def __init__(self):
        super().__init__(func=delete_event_responder)

# UserDetails Tool Classes
class FetchUserDetailsTool(FunctionTool):
    def __init__(self):
        super().__init__(func=fetch_user_details)

class GetUserByIdTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_user_by_id)

class GetUserByResponderIdTool(FunctionTool):
    def __init__(self):
        super().__init__(func=get_user_by_responder_id)

class CreateUserTool(FunctionTool):
    def __init__(self):
        super().__init__(func=create_user)

class UpdateUserTool(FunctionTool):
    def __init__(self):
        super().__init__(func=update_user)

class DeleteUserTool(FunctionTool):
    def __init__(self):
        super().__init__(func=delete_user)

class AuthenticateUserTool(FunctionTool):
    def __init__(self):
        super().__init__(func=authenticate_user)