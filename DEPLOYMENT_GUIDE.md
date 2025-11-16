# VexaAI Data Analyst Pro - Deployment Guide

## 🚀 Quick Start

Your VexaAI application is now fully integrated and running! Both backend and frontend are connected and working perfectly.

### Current Status
✅ **Backend API**: Running on http://localhost:8000
✅ **Frontend**: Running on http://localhost:3000
✅ **Database**: Connected to Supabase
✅ **Authentication**: Fully configured
✅ **AI Integration**: Multi-provider support (xAI Grok, Groq, Gemini)

---

## 🖥️ Running the Application

### Start Backend Server
```bash
cd /home/grejoy/Projects/Data_Analysis_AI_Agent
source venv/bin/activate
uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Server
```bash
cd /home/grejoy/Projects/Data_Analysis_AI_Agent/frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
Data_Analysis_AI_Agent/
├── backend_api/              # FastAPI REST API
│   └── main.py              # API endpoints
├── core/                    # Core business logic
│   ├── ml_engine.py        # AI query engine
│   ├── ai_client.py        # Multi-provider AI client
│   ├── auth.py             # Authentication
│   └── data_analysis.py    # Statistical analysis
├── database/
│   └── supabase_manager.py # Database operations
├── frontend/                # Next.js React frontend
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx        # Landing page
│   │   ├── auth/           # Login & Register
│   │   └── (dashboard)/    # Dashboard pages
│   ├── components/         # React components
│   ├── lib/               # API client
│   └── store/             # State management
├── Home.py                 # Streamlit app (legacy)
└── requirements.txt        # Python dependencies
```

---

## 🎯 Key Features

### 1. **Modern Landing Page**
- Professional design with feature showcase
- Call-to-action buttons
- Benefits and how-it-works sections

### 2. **Authentication System**
- User registration and login
- JWT token-based auth
- Protected dashboard routes
- Admin role support

### 3. **Dashboard Pages**
- **Dashboard**: Overview with stats and quick actions
- **Upload Data**: CSV/Excel file upload with validation
- **AI Analysis**: Natural language queries with multi-AI support
- **Visualizations**: Interactive charts (bar, line, pie)
- **Admin Panel**: User management (admin only)

### 4. **AI-Powered Analysis**
- Multi-provider support (xAI Grok, Groq, Google Gemini)
- Natural language to SQL generation
- Query execution and result interpretation
- Download results as CSV

### 5. **Data Processing**
- Automatic data cleaning
- 15+ preprocessing techniques
- Statistical tests (T-test, ANOVA, etc.)
- Interactive visualizations

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env` in root directory):
```env
# AI API Keys
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Data Management
- `POST /api/data/upload` - Upload dataset
- `GET /api/data/datasets` - List datasets
- `GET /api/data/dataset/{id}` - Get dataset details

### AI Queries
- `POST /api/ai/configure` - Configure AI provider
- `POST /api/ai/query` - Execute natural language query

### Statistics
- `POST /api/stats/ttest` - Perform T-test

### Admin
- `GET /api/admin/users` - Get all users (admin only)

### Health
- `GET /api/health` - System health check

---

## 🚀 Production Deployment

### Backend Deployment (Recommendations)

1. **Railway / Render / Heroku**
```bash
# Add Procfile
web: uvicorn backend_api.main:app --host 0.0.0.0 --port $PORT
```

2. **Update CORS in backend_api/main.py**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Deployment (Vercel)

1. **Connect GitHub repository to Vercel**
2. **Set root directory**: `frontend`
3. **Set environment variable**:
   - `NEXT_PUBLIC_API_URL=https://your-backend-api.com/api`
4. **Deploy!**

---

## 🔐 Security Checklist

- [ ] Change JWT_SECRET in production
- [ ] Use HTTPS for production
- [ ] Enable rate limiting
- [ ] Validate all user inputs
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for trusted domains
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## 📈 Monitoring & Analytics

### Backend Logs
Located in `logs/` directory:
- `app.log` - Application logs
- `error.log` - Error logs
- `performance.log` - Performance metrics
- `audit.log` - User actions audit trail

### Health Monitoring
```bash
curl http://localhost:8000/api/health
```

---

## 🎨 Customization

### Branding
- Update logo in `frontend/app/page.tsx`
- Modify colors in `frontend/tailwind.config.ts`
- Change app name in `frontend/app/layout.tsx`

### Features
- Add new dashboard pages in `frontend/app/(dashboard)/`
- Add new API endpoints in `backend_api/main.py`
- Extend AI capabilities in `core/ml_engine.py`

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (requires 3.13+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check database connection
# Verify SUPABASE_URL in .env
```

### Frontend won't start
```bash
# Clear cache
rm -rf frontend/.next
rm -rf frontend/node_modules

# Reinstall
cd frontend
npm install
npm run dev
```

### CORS errors
- Ensure backend CORS allows frontend origin
- Check `NEXT_PUBLIC_API_URL` in frontend/.env.local

---

## 📝 Next Steps

1. **Test the Application**
   - Register a new user
   - Upload a sample dataset
   - Configure an AI provider
   - Run some queries

2. **Customize Branding**
   - Update company name and logo
   - Modify color scheme
   - Add custom analytics

3. **Deploy to Production**
   - Set up hosting (Vercel + Railway/Render)
   - Configure production environment variables
   - Set up custom domain

4. **Add Features**
   - More visualization types
   - Export to PDF reports
   - Scheduled reports
   - Team collaboration features

---

## 💡 Tips for Success

1. **Start with Sample Data**: Test with small CSV files first
2. **AI API Keys**: Get free API keys from:
   - Groq: https://console.groq.com
   - Google Gemini: https://makersuite.google.com
3. **Monitor Usage**: Keep track of AI API usage to control costs
4. **User Feedback**: Gather feedback from first users to improve UX

---

## 🤝 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review API documentation at http://localhost:8000/docs
3. Inspect browser console for frontend errors

---

## 📜 License

Built by John Evans Okyere
VexaAI Data Analyst Pro v1.0.0

**Ready to transform your data analytics business!** 🚀
