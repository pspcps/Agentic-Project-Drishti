from google.cloud import firestore
from typing import Dict, List, Any, Optional
from datetime import datetime
from MCP_tools.tool_logging import log_tool_call

db = firestore.Client()

@log_tool_call("fetch_incidents")
def fetch_incidents() -> List[Dict]:
    """Fetches all incidents from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('incident').stream()]

@log_tool_call("get_active_incidents")
def get_active_incidents() -> Dict[str, Any]:
    """Return all incidents whose status is not 'close'."""
    all_incidents = fetch_incidents()
    active = [i for i in all_incidents if i.get('status') != 'close']
    return {"status": "success", "incidents": active}

@log_tool_call("fetch_zones")
def fetch_zones() -> List[Dict]:
    """Fetches all zones from Firestore."""
    return [{**doc.to_dict(), "id": doc.id} for doc in db.collection('zone').stream()]

@log_tool_call("fetch_responders")
def fetch_responders() -> List[Dict]:
    """Fetches all responders from Firestore, including their latest status from responder_incident_status if available. If not, use responder doc status or default to 'active'."""
    responders = [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('responder').stream()]
    for responder in responders:
        responder_id = responder['id']
        events = list(db.collection('responder_incident_status')
            .where('responder_id', '==', responder_id)
            .stream())
        latest_event = events[0].to_dict() if events else None
        if latest_event and latest_event.get('status'):
            responder['status'] = latest_event['status']
        else:
            responder['status'] = responder.get('status', 'active')
        responder['last_status_event'] = latest_event or {}
    return responders

@log_tool_call("get_available_responders")
def get_available_responders() -> Dict[str, Any]:
    """Return only responders whose latest status event is 'active', or if no event, whose responder doc status is 'active' or missing (default to active)."""
    responders = [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('responder').stream()]
    available = []
    for responder in responders:
        responder_id = responder.get('id')
        all_events = list(db.collection('responder_incident_status')
            .where('responder_id', '==', responder_id)
            .stream())
        latest_event = all_events[0].to_dict() if all_events else None
        if latest_event and latest_event.get('status') == 'active':
            available.append(responder)
        elif not latest_event:
            # No status event: use responder doc status or default to active
            if responder.get('status', 'active') == 'active':
                responder['status'] = 'active'
                available.append(responder)
    return {"status": "success", "responders": available}

@log_tool_call("fetch_alerts")
def fetch_alerts() -> List[Dict]:
    """Fetches all alerts from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('alerts').stream()]

@log_tool_call("analyze_responder_assignments")
def analyze_responder_assignments() -> Dict[str, Any]:
    """Analyzes all responders in the system."""
    responders_ref = db.collection('responder')
    available_query = responders_ref.where('status', '==', 'active')
    available_docs = available_query.stream()
    available = [doc.id for doc in available_docs]
    responders = responders_ref.stream()
    assigned = {}
    for doc in responders:
        data = doc.to_dict()
        if data.get('assignedIncident'):
            assigned[data.get('assignedIncident')] = doc.id
    return {"available": available, "assigned": assigned}

@log_tool_call("assign_responder_to_incident")
def assign_responder_to_incident(incident_id: str, responder_id: Optional[str] = None) -> Dict[str, str]:
    """Assigns a responder to the specified incident by writing an event to responder_incident_status.
    If responder_id is not provided, picks the first available responder."""
    if responder_id is None:
        available = get_available_responders().get('responders', [])
        if not available:
            return {"status": "error", "message": "No available responder found"}
        responder_id = available[0]['id']
    # Get incident info for zone_id
    incident_ref = db.collection('incident').document(incident_id)
    incident_doc = incident_ref.get()
    if not incident_doc.exists:
        return {"status": "error", "message": "Incident not found"}
    incident = incident_doc.to_dict()
    zone_id = incident.get("zone_id")
    status_update = {
        "responder_id": responder_id,
        "incident_id": incident_id,
        "zone_id": zone_id,
        "status": "assigned",
        "action": "assigned_to_incident",
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    # Write to event log (history)
    db.collection('responder_incident_status').add(status_update)
    return {"status": "assigned", "responder_id": responder_id, "incident_id": incident_id, "zone_id": zone_id}

@log_tool_call("assign_any_responder_to_incident")
def assign_any_responder_to_incident(incident_id: str) -> Dict[str, Any]:
    available = get_available_responders().get('responders', [])
    if not available:
        return {"status": "error", "error_message": "No responders available"}
    responder_id = available[0]['id']
    return assign_responder_to_incident(incident_id, responder_id)

@log_tool_call("assign_responder_to_zone")
def assign_responder_to_zone(responder_id: str, zone_id: str) -> Dict[str, str]:
    """Assigns a responder to a zone by writing an event to responder_incident_status."""
    responders_ref = db.collection('responder')
    zones_ref = db.collection('zone')
    responder_doc = responders_ref.document(responder_id)
    zone_doc = zones_ref.document(zone_id)
    responder = responder_doc.get()
    zone = zone_doc.get()
    if not responder.exists or not zone.exists:
        return {"status": "error", "message": "Responder or zone not found"}
    responder_data = responder.to_dict()
    status_update = {
        "responder_id": responder_id,
        "zone_id": zone_id,
        "status": "assigned",
        "action": "assigned_to_zone",
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection('responder_incident_status').add(status_update)
    return {"status": "assigned", "responder_id": responder_id, "zone_id": zone_id}

@log_tool_call("assign_any_responder_to_zone")
def assign_any_responder_to_zone(zone_id: str) -> Dict[str, Any]:
    """Assign any available responder to the given zone by writing an event to responder_incident_status."""
    available = get_available_responders().get('responders', [])
    if not available:
        return {"status": "error", "error_message": "No responders available"}
    responder_id = available[0]["id"]
    return assign_responder_to_zone(responder_id, zone_id)

@log_tool_call("notify_unavailable")
def notify_unavailable(zone_id: str) -> Dict[str, str]:
    """Logs an alert in Firestore if no responder is available for a zone (event-driven)."""
    db.collection('responder_incident_status').add({
        "zone_id": zone_id,
        "status": "unavailable",
        "action": "no_responder_available",
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    return {"status": "notified", "zone_id": zone_id, "method": "event_logged"}

@log_tool_call("suggest_zones_needing_responders")
def suggest_zones_needing_responders() -> Dict[str, Any]:
    """Suggest zones that need more responders based on incidents and current assignments. Placeholder logic."""
    incidents = fetch_incidents()
    zones = fetch_zones()
    needs = []
    for inc in incidents:
        if inc.get('status') == 'active':
            needs.append(inc.get('zone_id'))
    return {"status": "success", "zones_needing_responders": list(set(needs))}

@log_tool_call("get_incident_by_id")
def get_incident_by_id(incident_id: str) -> dict:
    doc = db.collection('incident').document(incident_id).get()
    if not doc.exists:
        raise Exception("Incident not found")
    return dict(id=doc.id, **doc.to_dict())

@log_tool_call("get_incidents_by_status")
def get_incidents_by_status(status: str) -> dict:
    docs = db.collection('incident').where('status', '==', status).stream()
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    return {"incidents": incidents}

@log_tool_call("get_incidents_by_zone")
def get_incidents_by_zone(zone_id: str) -> dict:
    docs = db.collection('incident').where('zone_id', '==', zone_id).stream()
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    return {"incidents": incidents}

@log_tool_call("get_responders_assigned_to_incident")
def get_responders_assigned_to_incident(incident_id: str) -> List[Dict]:
    """Fetch all responders assigned to a given incident using responder_incident_status."""
    status_events = list(db.collection('responder_incident_status')
        .where('incident_id', '==', incident_id)
        .where('status', '==', 'assigned')
        .stream())
    responder_ids = [e.to_dict().get('responder_id') for e in status_events if e.to_dict().get('responder_id')]
    if not responder_ids:
        return []
    responders = [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('responder').where('id', 'in', responder_ids).stream()]
    return responders 

# @log_tool_call("get_all_incident_reports")
def get_all_incident_reports() -> dict:
    docs = db.collection('incident_reports').stream()
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    return {"incidents": incidents}

# @log_tool_call("get_incident_reports_by_venue")
def get_incident_reports_by_venue(venue_id: str) -> dict:
    docs = db.collection('incident_reports').where('venue_id', '==', venue_id).stream()
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    return {"incidents": incidents}

# @log_tool_call("get_incident_statistics")
def get_incident_statistics() -> dict:
    docs = db.collection('incident_reports').stream()
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in docs]
    if not incidents:
        return {
            "total_incidents": 0,
            "resolved_incidents": 0,
            "resolution_rate": 0.0,
            "avg_severity": 0.0,
            "avg_feedback": 0.0,
            "incident_types": {},
            "severity_distribution": {}
        }
    resolved_incidents = [i for i in incidents if i.get('resolved', False)]
    resolution_rate = len(resolved_incidents) / len(incidents)
    avg_severity = sum([i.get('severity', 0) for i in resolved_incidents]) / max(len(resolved_incidents), 1)
    avg_feedback = sum([i.get('feedback_rating', 4) for i in incidents]) / max(len(incidents), 1)
    incident_types = {}
    for incident in incidents:
        inc_type = incident.get('type', 'unknown')
        incident_types[inc_type] = incident_types.get(inc_type, 0) + 1
    severity_distribution = {}
    for incident in incidents:
        severity = incident.get('severity', 0)
        severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
    return {
        "total_incidents": len(incidents),
        "resolved_incidents": len(resolved_incidents),
        "resolution_rate": resolution_rate,
        "avg_severity": avg_severity,
        "avg_feedback": avg_feedback,
        "incident_types": incident_types,
        "severity_distribution": severity_distribution
    } 
@log_tool_call("get_incidents_for_responder")
def get_incidents_for_responder(responder_id: str) -> list:
    """Fetch all incidents for a given responder based on responder_incident_status."""
    status_events = list(db.collection('responder_incident_status')
        .where('responder_id', '==', responder_id)
        .stream())
    incident_ids = [e.to_dict().get('incident_id') for e in status_events if e.to_dict().get('incident_id')]
    if not incident_ids:
        return []
    incident_ids = list(set(incident_ids))
    incidents = [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('incident').where('id', 'in', incident_ids).stream()]
    return incidents 

@log_tool_call("get_incidents_details_for_responder")
def get_incidents_details_for_responder(responder_id: str) -> list:
    """Fetch full incident details for a given responder from incident collection."""
    status_events = list(db.collection('responder_incident_status')
        .where('responder_id', '==', responder_id)
        .stream())
    incident_ids = [e.to_dict().get('incident_id') for e in status_events if e.to_dict().get('incident_id')]
    if not incident_ids:
        return []
    incident_ids = list(set(incident_ids))
    incidents = []
    for incident_id in incident_ids:
        doc = db.collection('incident').document(incident_id).get()
        if doc.exists:
            incident_data = dict(id=doc.id, **doc.to_dict())
            incidents.append(incident_data)
    return incidents 

# Venue CRUD Functions
@log_tool_call("fetch_venues")
def fetch_venues() -> List[Dict]:
    """Fetches all venues from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('venue').stream()]

@log_tool_call("get_venue_by_id")
def get_venue_by_id(venue_id: str) -> dict:
    """Get a single venue by ID."""
    doc = db.collection('venue').document(venue_id).get()
    if not doc.exists:
        raise Exception("Venue not found")
    return dict(id=doc.id, **doc.to_dict())

@log_tool_call("create_venue")
def create_venue(venue_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new venue."""
    # Validate required fields
    required_fields = ['name', 'type', 'crowdType', 'noOfGates', 'area', 'createdBy']
    for field in required_fields:
        if field not in venue_data:
            raise Exception(f"Missing required field: {field}")
    
    # Add timestamp
    venue_data['createdAt'] = firestore.SERVER_TIMESTAMP
    
    # Create document
    doc_ref = db.collection('venue').add(venue_data)
    return {"id": doc_ref[1].id, **venue_data}

@log_tool_call("update_venue")
def update_venue(venue_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing venue."""
    doc_ref = db.collection('venue').document(venue_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("Venue not found")
    
    # Update document
    doc_ref.update(updates)
    return {"id": venue_id, **updates}

@log_tool_call("delete_venue")
def delete_venue(venue_id: str) -> Dict[str, Any]:
    """Delete a venue."""
    doc_ref = db.collection('venue').document(venue_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("Venue not found")
    
    doc_ref.delete()
    return {"success": True, "id": venue_id}

# Event CRUD Functions
@log_tool_call("fetch_events")
def fetch_events() -> List[Dict]:
    """Fetches all events from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('event').stream()]

@log_tool_call("get_event_by_id")
def get_event_by_id(event_id: str) -> dict:
    """Get a single event by ID."""
    doc = db.collection('event').document(event_id).get()
    if not doc.exists:
        raise Exception("Event not found")
    return dict(id=doc.id, **doc.to_dict())

@log_tool_call("get_events_by_venue")
def get_events_by_venue(venue_id: str) -> List[Dict]:
    """Get all events for a specific venue."""
    docs = db.collection('event').where('venuedocumentID', '==', venue_id).stream()
    return [dict(id=doc.id, **doc.to_dict()) for doc in docs]

@log_tool_call("create_event")
def create_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new event."""
    # Validate required fields
    required_fields = ['name', 'venuedocumentID', 'eventAdmin', 'createdBy', 'startDate', 'endDate']
    for field in required_fields:
        if field not in event_data:
            raise Exception(f"Missing required field: {field}")
    
    # Add timestamp
    event_data['createdAt'] = firestore.SERVER_TIMESTAMP
    
    # Create document
    doc_ref = db.collection('event').add(event_data)
    return {"id": doc_ref[1].id, **event_data}

@log_tool_call("update_event")
def update_event(event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing event."""
    doc_ref = db.collection('event').document(event_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("Event not found")
    
    # Update document
    doc_ref.update(updates)
    return {"id": event_id, **updates}

@log_tool_call("delete_event")
def delete_event(event_id: str) -> Dict[str, Any]:
    """Delete an event."""
    doc_ref = db.collection('event').document(event_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("Event not found")
    
    doc_ref.delete()
    return {"success": True, "id": event_id}

# EventResponder CRUD Functions
@log_tool_call("fetch_event_responders")
def fetch_event_responders() -> List[Dict]:
    """Fetches all event responder assignments from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('eventResponder').stream()]

@log_tool_call("get_event_responders_by_event")
def get_event_responders_by_event(event_id: str) -> List[Dict]:
    """Get all responder assignments for a specific event."""
    docs = db.collection('eventResponder').where('eventId', '==', event_id).stream()
    return [dict(id=doc.id, **doc.to_dict()) for doc in docs]

@log_tool_call("get_event_responders_by_responder")
def get_event_responders_by_responder(responder_id: str) -> List[Dict]:
    """Get all event assignments for a specific responder."""
    docs = db.collection('eventResponder').where('responderID', '==', responder_id).stream()
    return [dict(id=doc.id, **doc.to_dict()) for doc in docs]

@log_tool_call("create_event_responder")
def create_event_responder(event_responder_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new event responder assignment."""
    # Validate required fields
    required_fields = ['eventId', 'responderID']
    for field in required_fields:
        if field not in event_responder_data:
            raise Exception(f"Missing required field: {field}")
    
    # Add timestamp
    event_responder_data['assignedateTime'] = firestore.SERVER_TIMESTAMP
    
    # Create document
    doc_ref = db.collection('eventResponder').add(event_responder_data)
    return {"id": doc_ref[1].id, **event_responder_data}

@log_tool_call("delete_event_responder")
def delete_event_responder(event_responder_id: str) -> Dict[str, Any]:
    """Delete an event responder assignment."""
    doc_ref = db.collection('eventResponder').document(event_responder_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("Event responder assignment not found")
    
    doc_ref.delete()
    return {"success": True, "id": event_responder_id}

# UserDetails CRUD Functions
@log_tool_call("fetch_user_details")
def fetch_user_details() -> List[Dict]:
    """Fetches all user details from Firestore."""
    return [dict(id=doc.id, **doc.to_dict()) for doc in db.collection('userDetails').stream()]

@log_tool_call("get_user_by_id")
def get_user_by_id(user_id: str) -> dict:
    """Get a single user by userId."""
    docs = db.collection('userDetails').where('userId', '==', user_id).stream()
    for doc in docs:
        return dict(id=doc.id, **doc.to_dict())
    raise Exception("User not found")

@log_tool_call("get_user_by_responder_id")
def get_user_by_responder_id(responder_id: str) -> dict:
    """Get a user by responder_id."""
    docs = db.collection('userDetails').where('responder_id', '==', responder_id).stream()
    for doc in docs:
        return dict(id=doc.id, **doc.to_dict())
    raise Exception("User not found")

@log_tool_call("create_user")
def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user."""
    # Validate required fields
    required_fields = ['userId', 'password', 'accessCode']
    for field in required_fields:
        if field not in user_data:
            raise Exception(f"Missing required field: {field}")
    
    # Check if user already exists
    existing_docs = db.collection('userDetails').where('userId', '==', user_data['userId']).stream()
    if list(existing_docs):
        raise Exception("User already exists")
    
    # Create document
    doc_ref = db.collection('userDetails').add(user_data)
    return {"id": doc_ref[1].id, **user_data}

@log_tool_call("update_user")
def update_user(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing user."""
    doc_ref = db.collection('userDetails').document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("User not found")
    
    # Update document
    doc_ref.update(updates)
    return {"id": user_id, **updates}

@log_tool_call("delete_user")
def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete a user."""
    doc_ref = db.collection('userDetails').document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise Exception("User not found")
    
    doc_ref.delete()
    return {"success": True, "id": user_id}

@log_tool_call("authenticate_user")
def authenticate_user(user_id: str, password: str) -> Dict[str, Any]:
    """Authenticate a user with userId and password."""
    docs = db.collection('userDetails').where('userId', '==', user_id).stream()
    for doc in docs:
        user_data = doc.to_dict()
        if user_data.get('password') == password:
            return {
                "success": True,
                "user": dict(id=doc.id, **user_data),
                "message": "Authentication successful"
            }
        else:
            return {
                "success": False,
                "message": "Invalid password"
            }
    
    return {
        "success": False,
        "message": "User not found"
    } 
