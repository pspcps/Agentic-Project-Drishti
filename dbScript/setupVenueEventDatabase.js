#!/usr/bin/env node

(async () => {
  // setupVenueEventDatabase.js
  // Script to initialize Firestore collections for venue, event, zone, responder, incident, eventResponder, and responder_incident_status with dummy data

  const admin = require('firebase-admin');

  // Initialize Firebase Admin
  admin.initializeApp();
  const db = admin.firestore();

  async function setupCollections() {
    // Venue Collection
    const venues = [
      {
        createdAt: new Date().toISOString(),
        createdBy: 'admin',
        crowdType: 'Seating',
        noOfGates: 4,
        name: 'RCB Match',
        layoutImageUrl: null,
        area: 718740,
        type: 'Stadium',
        description: 'IPL Cricket Match',
      },
      {
        createdAt: new Date().toISOString(),
        createdBy: 'admin',
        crowdType: 'Standing',
        noOfGates: 2,
        name: 'Music Fest',
        layoutImageUrl: null,
        area: 50000,
        type: 'Ground',
        description: 'Outdoor music festival',
      },
      {
        createdAt: new Date().toISOString(),
        createdBy: 'user1',
        crowdType: 'Mixed',
        noOfGates: 3,
        name: 'Tech Expo',
        layoutImageUrl: null,
        area: 120000,
        type: 'Others',
        description: 'Technology exhibition',
      },
    ];

    // Event Collection
    const events = [
      {
        venuedocumentID: '', // to be filled after venue creation
        name: 'RCB Match',
        eventAdmin: 'admin',
        createdBy: 'admin',
        createdAt: new Date().toISOString(),
        startDate: '2025-07-26T10:00:00Z',
        endDate: '2025-07-26T18:00:00Z',
        metadata: { tags: ['cricket', 'sports'] },
      },
      {
        venuedocumentID: '',
        name: 'Music Fest',
        eventAdmin: 'user1',
        createdBy: 'user1',
        createdAt: new Date().toISOString(),
        startDate: '2025-08-01T16:00:00Z',
        endDate: '2025-08-01T23:00:00Z',
        metadata: { tags: ['music', 'festival'] },
      },
    ];

    // Zone Collection
    const zones = [
      {
        venuedocumentID: '', // to be filled after venue creation
        name: 'ZoneA',
        capacity: 1234,
        crowdType: 'Seating',
        assignedGates: [1, 2],
        metadata: { tags: ['VIP', 'music show'] },
      },
      {
        venuedocumentID: '',
        name: 'ZoneB',
        capacity: 2000,
        crowdType: 'Standing',
        assignedGates: [3, 4],
        metadata: { tags: ['general', 'fire show'] },
      },
    ];

    // Responder Collection
    const responders = [
      {
        name: 'Sarah Johnson',
        type: 'Medical',
        contact: { phone: '+91-9876543211', radio: 'Channel 2', email: 'sarah.johnson@medical.gov' },
        equipment: { medicalKit: true },
        skillLevel: 5,
        metadata: { tags: ['Emergency Medicine', 'Trauma Care'] },
        status: 'active',
        createdAt: new Date().toISOString(),
      },
      {
        name: 'John Smith',
        type: 'Security',
        contact: { phone: '+91-9876543222', radio: 'Channel 1', email: 'john.smith@security.gov' },
        equipment: { baton: true },
        skillLevel: 4,
        metadata: { tags: ['Crowd Control'] },
        status: 'active',
        createdAt: new Date().toISOString(),
      },
      {
        name: 'Priya Patel',
        type: 'Fire',
        contact: { phone: '+91-9876543233', radio: 'Channel 3', email: 'priya.patel@fire.gov' },
        equipment: { fireExtinguisher: true },
        skillLevel: 5,
        metadata: { tags: ['Fire Safety'] },
        status: 'inactive',
        createdAt: new Date().toISOString(),
      },
    ];

    // Incident Collection
    const incidents = [
      {
        description: 'Incident at north gate',
        lastUpdated: new Date().toISOString(),
        reportedBy: 'agent_001',
        resolvedAt: null,
        severity: 'High',
        status: 'active',
        metadata: { tags: ['overcrowding', 'exit_blocked'] },
        createdAt: new Date().toISOString(),
        eta: '',
        type: 'crowd',
        currentOccupancy: '',
        zoneId: '', // to be filled after zone creation
        eventId: '', // to be filled after event creation
        venueId: '', // to be filled after venue creation
      },
      {
        description: 'Medical emergency in ZoneB',
        lastUpdated: new Date().toISOString(),
        reportedBy: 'agent_002',
        resolvedAt: null,
        severity: 'Critical',
        status: 'pending',
        metadata: { tags: ['medical', 'injury'] },
        createdAt: new Date().toISOString(),
        eta: '',
        type: 'medical',
        currentOccupancy: '',
        zoneId: '',
        eventId: '',
        venueId: '',
      },
    ];

    // eventResponder Collection
    const eventResponders = [
      {
        eventId: '', // to be filled after event creation
        responderID: '', // to be filled after responder creation
        assignedateTime: new Date().toISOString(),
      },
    ];

    // responder_incident_status Collection
    const responderIncidentStatuses = [
      {
        incidentId: '', // to be filled after incident creation
        responderId: '', // to be filled after responder creation
        status: 'en_route',
        timestamp: new Date().toISOString(),
      },
    ];

    // UserDetails Collection
    const userDetails = [
      {
        accessCode: 127,
        password: 'admin123',
        userId: 'admin',
        // No responder_id for admin
      },
      {
        accessCode: 1,
        password: '123',
        userId: 'responder_001',
        responder_id: '', // to be filled after responder creation
      },
      {
        accessCode: 1,
        password: '123',
        userId: 'responder_002',
        responder_id: '',
      },
      {
        accessCode: 1,
        password: '123',
        userId: 'responder_003',
        responder_id: '',
      },
    ];

    // Add venues
    const venueRefs = [];
    for (const venue of venues) {
      const ref = await db.collection('venue').add(venue);
      venueRefs.push(ref);
    }

    // Add events (link to first venue)
    const eventRefs = [];
    for (let i = 0; i < events.length; i++) {
      events[i].venuedocumentID = venueRefs[i % venueRefs.length].id;
      const ref = await db.collection('event').add(events[i]);
      eventRefs.push(ref);
    }

    // Add zones (link to first venue)
    const zoneRefs = [];
    for (let i = 0; i < zones.length; i++) {
      zones[i].venuedocumentID = venueRefs[i % venueRefs.length].id;
      const ref = await db.collection('zone').add(zones[i]);
      zoneRefs.push(ref);
    }

    // Add responders
    const responderRefs = [];
    for (const responder of responders) {
      const ref = await db.collection('responder').add(responder);
      responderRefs.push(ref);
    }

    // Add userDetails (link responder_id to responderRefs)
    for (let i = 0; i < userDetails.length; i++) {
      if (userDetails[i].accessCode === 1) {
        // Map responder_id to responderRefs (by order)
        userDetails[i].responder_id = responderRefs[i - 1] ? responderRefs[i - 1].id : '';
      }
      await db.collection('userDetails').add(userDetails[i]);
    }

    // Add incidents (link to first zone, event, venue)
    const incidentRefs = [];
    for (let i = 0; i < incidents.length; i++) {
      incidents[i].zoneId = zoneRefs[i % zoneRefs.length].id;
      incidents[i].eventId = eventRefs[i % eventRefs.length].id;
      incidents[i].venueId = venueRefs[i % venueRefs.length].id;
      const ref = await db.collection('incident').add(incidents[i]);
      incidentRefs.push(ref);
    }

    // Add eventResponder (link to first event and responder)
    for (let i = 0; i < eventResponders.length; i++) {
      eventResponders[i].eventId = eventRefs[0].id;
      eventResponders[i].responderID = responderRefs[0].id;
      await db.collection('eventResponder').add(eventResponders[i]);
    }

    // Add responder_incident_status (link to first incident and responder)
    for (let i = 0; i < responderIncidentStatuses.length; i++) {
      responderIncidentStatuses[i].incidentId = incidentRefs[0].id;
      responderIncidentStatuses[i].responderId = responderRefs[0].id;
      await db.collection('responder_incident_status').add(responderIncidentStatuses[i]);
    }

    console.log('Firestore collections and dummy data created successfully!');
  }

  setupCollections().then(() => process.exit(0)).catch(e => { console.error(e); process.exit(1); });
})(); 