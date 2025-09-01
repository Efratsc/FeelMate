# FeelMate 💙

> Your AI companion for emotional support and mental wellness

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

FeelMate is an intelligent emotional support chatbot that provides personalized mental health assistance using advanced emotion detection and contextual response generation. Built with modern technologies and designed for accessibility, FeelMate offers a safe space for users to express their feelings and receive supportive guidance.

## ✨ Features

### 🧠 **Intelligent Emotion Detection**
- Real-time emotion analysis using HuggingFace models
- Detects 7+ emotions: joy, sadness, anger, fear, surprise, disgust, and neutral
- Contextual understanding of emotional states

### 💬 **Personalized Conversations**
- LLM-free LangGraph pipeline for smart responses
- In-memory conversation history for continuity
- Context-aware response generation
- Crisis detection and intervention

### 🎨 **Beautiful Modern UI**
- Full-screen ChatGPT-like interface
- Responsive design for all devices
- Real-time streaming responses
- Clean, accessible design

### 🛡️ **Safety & Support**
- Crisis detection and emergency resource recommendations
- Help-seeking behavior recognition
- Professional mental health resource links
- Severity assessment and appropriate responses

### 🔧 **Technical Excellence**
- FastAPI backend with async processing
- Next.js frontend with TypeScript
- LangGraph for intelligent conversation flow
- No external LLM dependencies

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

#### Prerequisites
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**

#### 1. Clone and Run with Docker
```bash
git clone https://github.com/Efratsc/FeelMate.git
cd FeelMate

# Production mode
docker-compose up --build

# Or development mode with hot reloading
docker-compose -f docker-compose.dev.yml up --build
```

#### 2. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

📖 **For detailed Docker instructions, see [DOCKER.md](DOCKER.md)**

### Option 2: Manual Setup

#### Prerequisites
- **Node.js** 18+ 
- **Python** 3.8+
- **Git**

#### 1. Clone the Repository
```bash
git clone https://github.com/Efratsc/FeelMate.git
cd FeelMate
```

#### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp env.template .env
# Edit .env and set USE_LANGRAPH=true
python start_production.py
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
```
frontend/
├── components/          # React components
│   └── ChatBox.tsx     # Main chat interface
├── app/                # Next.js app directory
│   ├── api/           # API routes
│   └── chat/          # Chat page
└── styles/            # CSS and styling
```

### Backend (FastAPI + LangGraph)
```
backend/
├── app/
│   ├── ml/
│   │   └── graph_pipeline.py  # LangGraph conversation pipeline
│   └── api/                   # API endpoints
├── server.py                  # Main server
└── requirements.txt           # Python dependencies
```

## 🧠 How It Works

### 1. **Emotion Detection**
- Uses HuggingFace's text classification pipeline
- Analyzes user input for emotional content
- Provides confidence scores for detected emotions

### 2. **Contextual Response Generation**
- LangGraph pipeline processes conversation flow
- Maintains conversation history in memory
- Generates contextually appropriate responses

### 3. **Safety Monitoring**
- Crisis detection using keyword analysis
- Severity assessment based on emotion and content
- Automatic resource recommendations

### 4. **Real-time Streaming**
- Frontend displays responses with typewriter effect
- Backend processes requests asynchronously
- Smooth, responsive user experience

## 🎯 Use Cases

- **Daily Emotional Support**: Chat about your day and receive empathetic responses
- **Crisis Intervention**: Get immediate support and resources during difficult times
- **Mood Tracking**: Understand your emotional patterns over time
- **Mental Health Education**: Learn about emotions and coping strategies
- **Therapeutic Conversation**: Practice expressing feelings in a safe environment

## 🐳 Docker Deployment

FeelMate includes comprehensive Docker support for easy deployment and development.

### Quick Docker Commands
```bash
# Production deployment
docker-compose up --build

# Development with hot reloading
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Features
- **Multi-stage builds** for optimized production images
- **Development environment** with hot reloading
- **Health checks** for service monitoring
- **Security best practices** with non-root users
- **Resource optimization** with Alpine Linux images

📖 **Complete Docker guide: [DOCKER.md](DOCKER.md)**

## 🔧 Configuration

### Environment Variables
```bash
# Backend (.env)
USE_LANGRAPH=true          # Enable LangGraph mode
LOG_LEVEL=info            # Logging level
PORT=8000                 # Server port
```

### Docker Environment Variables
```bash
# Backend (Docker)
USE_LANGRAPH=true
LOG_LEVEL=info
PORT=8000

# Frontend (Docker)
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Customization
- **Emotion Models**: Replace HuggingFace models in `graph_pipeline.py`
- **Response Templates**: Modify response patterns in the LangGraph pipeline
- **UI Styling**: Customize colors and layout in `ChatBox.tsx`
- **Resource Links**: Update mental health resources in the pipeline

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
python -m pytest
```

### Manual Testing
1. Start both frontend and backend
2. Send various emotional messages
3. Test crisis detection with keywords
4. Verify resource recommendations

## 📊 Performance

- **Response Time**: < 2 seconds for most queries
- **Concurrent Users**: Supports multiple simultaneous conversations
- **Memory Usage**: Efficient in-memory conversation storage
- **Scalability**: Stateless design allows horizontal scaling

## 🔒 Security & Privacy

- **No Data Persistence**: Conversations are not stored permanently
- **Local Processing**: All analysis happens on your server
- **No External APIs**: No data sent to third-party services
- **Input Validation**: All user input is validated and sanitized

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines

## 🏆 Roadmap

- [ ] **Multi-language Support**: Add support for multiple languages
- [ ] **Voice Interface**: Speech-to-text and text-to-speech capabilities
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Analytics Dashboard**: Conversation insights and patterns
- [ ] **Integration APIs**: Connect with other mental health platforms
- [ ] **Advanced AI Models**: Integration with more sophisticated emotion models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace** for emotion detection models
- **LangGraph** for conversation flow management
- **FastAPI** for the robust backend framework
- **Next.js** for the modern frontend experience
- **Contributors** who help improve FeelMate

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/FeelMate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/FeelMate/discussions)
- **Email**: support@feelmate.ai

## ⚠️ Disclaimer

FeelMate is designed to provide emotional support and is not a replacement for professional mental health care. If you're experiencing a mental health crisis, please contact emergency services or a mental health professional immediately.

---

**Made with ❤️ for better mental health support**
