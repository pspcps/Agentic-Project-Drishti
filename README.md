# Project Drishti - AI-Powered Crowd Safety & Event Management System

A comprehensive, full-stack application that leverages AI agents for real-time crowd safety monitoring, incident management, and event coordination. Built with modern web technologies and Google Cloud Platform services.

## 🚀 Features

### AI-Powered Agents
- **Situational Summary Agent**: Real-time analysis and summarization of crowd situations
- **Emergency Escalation Agent**: Intelligent incident escalation and priority management
- **Crowd Notification Agent**: Automated alert systems for safety personnel
- **Response Dispatcher Agent**: Smart resource allocation and responder coordination
- **Chat Agent**: Interactive AI assistant for incident management
- **Incident Agent**: Specialized incident analysis and response coordination

### Frontend Dashboard
- **Real-time Monitoring**: Live incident tracking and crowd analytics
- **Interactive Maps**: Google Maps integration with incident markers and zone management
- **Incident Management**: Comprehensive incident lifecycle management
- **Analytics & Reports**: Data visualization and historical analysis
- **Venue Management**: Multi-venue support with custom configurations
- **Mobile-Responsive**: Optimized for desktop and mobile devices

### Backend Services
- **RESTful API**: FastAPI-based backend with JWT authentication
- **Real-time Communication**: Pub/Sub messaging between agents
- **Data Persistence**: Firestore database for scalable data storage
- **AI Integration**: Google Cloud AI Platform and Gemini for LLM tasks
- **Vision Analysis**: Computer vision for crowd monitoring and incident detection

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Agents     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (GCP)         │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • Summary       │
│ • Maps          │    │ • JWT Auth      │    │ • Escalation    │
│ • Incidents     │    │ • Pub/Sub       │    │ • Notification  │
│ • Analytics     │    │ • Firestore     │    │ • Dispatcher    │
│ • Reports       │    │ • Vision AI     │    │ • Chat          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 19** with Vite for fast development
- **Tailwind CSS** for modern, responsive styling
- **Material-UI** components for consistent design
- **React Router** for navigation
- **Google Maps API** for interactive mapping
- **Recharts** for data visualization
- **Firebase** for real-time features

### Backend
- **FastAPI** for high-performance API
- **Google Cloud Platform** services:
  - **Firestore** for database
  - **Pub/Sub** for messaging
  - **Vertex AI** for machine learning
  - **Cloud Vision** for image analysis
  - **Text-to-Speech** for audio alerts
- **JWT** for secure authentication
- **Redis** for caching
- **SQLAlchemy** for database ORM

### AI & ML
- **Google Gemini** for natural language processing
- **Custom AI Agents** for specialized tasks
- **Computer Vision** for crowd analysis
- **Predictive Analytics** for incident forecasting

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Google Cloud Platform account
- Firebase project

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Agentic-Project-Drishti/backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with:
   ```env
   GOOGLE_CLOUD_PROJECT=your-project-id
   JWT_SECRET=your-secret-key
   FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
   ```

5. **Set up Google Cloud services**
   - Enable Firestore, Pub/Sub, Vertex AI, and Cloud Vision APIs
   - Create service account and download credentials
   - Set up Pub/Sub topics for agent communication

6. **Run the backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure Firebase**
   - Create a Firebase project
   - Add Firebase configuration to `src/firebase.js`

4. **Run the frontend**
   ```bash
   npm run dev
   ```

### Database Setup

1. **Set up Firestore database**
   ```bash
   cd ../dbScript
   npm install
   node setupDatabase.js
   ```

2. **Initialize agent database**
   ```bash
   node setupAgentDatabase.js
   ```

## 🚀 Deployment

### Docker Deployment

1. **Backend deployment**
   ```bash
   cd backend
   docker build -t drishti-backend .
   docker run -p 8000:8000 drishti-backend
   ```

2. **Frontend deployment**
   ```bash
   cd frontend
   docker build -t drishti-frontend .
   docker run -p 3000:80 drishti-frontend
   ```

### Google Cloud Platform Deployment

Use the provided deployment scripts:
```bash
# Backend deployment
./backend/deploy.sh

# MCP deployment
./backend/deploy-mcp.sh
```

## 📚 API Documentation

The API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/login` - User authentication
- `POST /summary` - Run situational summary agent
- `POST /escalation` - Run emergency escalation agent
- `POST /notification` - Run crowd notification agent
- `POST /dispatcher` - Run response dispatcher agent
- `POST /chat` - Interactive AI chat
- `GET /api/incidents` - Get incident data
- `POST /api/venues` - Venue management
- `GET /api/zones` - Zone management

## 🤖 AI Agents

### Situational Summary Agent
- Analyzes real-time crowd data
- Generates situational awareness reports
- Identifies potential safety concerns

### Emergency Escalation Agent
- Monitors incident severity levels
- Automatically escalates critical situations
- Manages response priorities

### Crowd Notification Agent
- Sends automated alerts to relevant personnel
- Manages communication channels
- Tracks notification delivery status

### Response Dispatcher Agent
- Allocates resources based on incident type
- Coordinates responder assignments
- Optimizes response times

### Chat Agent
- Provides interactive AI assistance
- Answers queries about incidents and procedures
- Supports natural language interaction

## 🔧 Development

### Project Structure
```
Agentic-Project-Drishti/
├── backend/                 # FastAPI backend
│   ├── agents/             # AI agent implementations
│   ├── api/                # REST API endpoints
│   ├── tools/              # Utility tools and services
│   ├── utils/              # Helper utilities
│   └── main.py            # Main application entry
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Frontend utilities
│   └── package.json
├── dbScript/               # Database setup scripts
└── README.md
```

### Adding New Features

1. **New AI Agent**
   - Create agent class in `backend/agents/`
   - Implement required methods
   - Add to agent registry

2. **New API Endpoint**
   - Create router in `backend/api/`
   - Add to main app in `main.py`
   - Update documentation

3. **New Frontend Component**
   - Create component in `frontend/src/components/`
   - Add to appropriate page
   - Update routing if needed

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📊 Monitoring & Analytics

- **Real-time dashboards** for incident monitoring
- **Historical analytics** for trend analysis
- **Performance metrics** for system optimization
- **Alert systems** for critical events

## 🔒 Security

- **JWT authentication** for API access
- **Role-based access control** (RBAC)
- **Secure communication** via HTTPS
- **Data encryption** at rest and in transit
- **Input validation** and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation at `/docs`

## 🔄 Version History

- **v1.0.0** - Initial release with core AI agents and dashboard
- **v1.1.0** - Added real-time monitoring and analytics
- **v1.2.0** - Enhanced security and multi-venue support

---

**Project Drishti** - Empowering crowd safety through intelligent AI agents and real-time monitoring.