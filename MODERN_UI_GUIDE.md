# VexaAI Modern UI - React/Next.js + FastAPI Guide

## 📋 Overview

This guide covers the **modern web application** setup using React/Next.js frontend and FastAPI backend. This is separate from the original Streamlit implementation and provides a production-ready SaaS platform.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser)                          │
│                   http://localhost:3000                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Next.js Frontend (React)                        │
│  • Landing Page                                              │
│  • Authentication (Login/Register)                           │
│  • Dashboard with Sidebar Navigation                         │
│  • Data Upload & Management                                  │
│  • AI Analysis Interface                                     │
│  • Interactive Visualizations                                │
│  • Admin Panel                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Axios API Client
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                          │
│                http://localhost:8000                         │
│  • RESTful API Endpoints                                     │
│  • JWT Authentication                                        │
│  • File Upload Processing                                    │
│  • AI Query Processing                                       │
│  • CORS Middleware                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌───────────────┐      ┌──────────────┐
        │   Supabase    │      │  AI Providers │
        │  (PostgreSQL) │      │  • xAI Grok   │
        │               │      │  • Groq       │
        │  • Users      │      │  • Gemini     │
        │  • Datasets   │      └──────────────┘
        │  • History    │
        └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.13+ (for backend)
- Supabase account (free tier works)
- AI API keys (Groq/Gemini - free tiers available)

### 1. Start the Backend (Terminal 1)

```bash
# Navigate to project root
cd /home/grejoy/Projects/Data_Analysis_AI_Agent

# Activate Python virtual environment
source venv/bin/activate

# Start FastAPI server with hot reload
uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:**
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 2. Start the Frontend (Terminal 2)

```bash
# Navigate to frontend directory
cd /home/grejoy/Projects/Data_Analysis_AI_Agent/frontend

# Install dependencies (first time only)
npm install

# Start Next.js development server
npm run dev
```

**Frontend will be available at:**
- Application: http://localhost:3000

### 3. Verify Both Are Running

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check frontend (should return HTML)
curl http://localhost:3000
```

---

## 📂 Project Structure

### Frontend Structure (`/frontend`)

```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # Root layout with metadata
│   ├── page.tsx                 # Landing page (/)
│   │
│   ├── auth/                    # Authentication pages
│   │   ├── login/
│   │   │   └── page.tsx        # Login page (/auth/login)
│   │   └── register/
│   │       └── page.tsx        # Register page (/auth/register)
│   │
│   └── (dashboard)/            # Protected dashboard routes
│       ├── layout.tsx          # Dashboard layout with auth check
│       ├── dashboard/
│       │   └── page.tsx        # Main dashboard (/dashboard)
│       ├── upload/
│       │   └── page.tsx        # Upload data (/upload)
│       ├── analysis/
│       │   └── page.tsx        # AI analysis (/analysis)
│       ├── visualize/
│       │   └── page.tsx        # Visualizations (/visualize)
│       └── admin/
│           └── page.tsx        # Admin panel (/admin)
│
├── components/
│   ├── dashboard/
│   │   └── Sidebar.tsx         # Navigation sidebar
│   └── ui/                     # Shadcn UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── toast.tsx
│       └── ...
│
├── lib/
│   ├── api.ts                  # Axios API client with interceptors
│   └── utils.ts                # Utility functions
│
├── store/
│   └── useStore.ts             # Zustand state management
│
├── types/
│   └── index.ts                # TypeScript type definitions
│
├── .env.local                  # Environment variables
├── package.json                # Dependencies
├── tailwind.config.ts          # Tailwind CSS config
└── tsconfig.json              # TypeScript config
```

### Backend Structure (`/backend_api`)

```
backend_api/
└── main.py                     # FastAPI application
    ├── Authentication endpoints
    ├── Data management endpoints
    ├── AI query endpoints
    ├── Admin endpoints
    └── Health check endpoint
```

---

## 🔑 Environment Configuration

### Backend Environment (`.env` in project root)

```env
# AI API Keys (get free keys from providers)
GROQ_API_KEY=gsk_your_groq_api_key_here
GEMINI_API_KEY=AIza_your_gemini_api_key_here
# XAI_API_KEY=xai_your_xai_api_key_here  # Optional

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

### Frontend Environment (`frontend/.env.local`)

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Important:** The `NEXT_PUBLIC_` prefix makes the variable accessible in the browser.

---

## 🔐 Authentication Flow

### 1. User Registration

```mermaid
User → Frontend (Register Page) → API Client → Backend (/api/auth/register)
Backend → Supabase (Create User) → Backend → Frontend (Success/Error)
Frontend → Redirect to Login
```

**Code Flow:**
```typescript
// frontend/app/auth/register/page.tsx
const response = await api.register(username, email, password, full_name);
// Redirects to /auth/login on success
```

### 2. User Login

```mermaid
User → Frontend (Login Page) → API Client → Backend (/api/auth/login)
Backend → Supabase (Verify) → Backend (Generate JWT) → Frontend
Frontend → Store Token → Redirect to Dashboard
```

**Code Flow:**
```typescript
// frontend/app/auth/login/page.tsx
const response = await api.login(username, password);
localStorage.setItem("token", response.token);
// Redirects to /dashboard
```

### 3. Protected Routes

```mermaid
User → Dashboard Page → Layout (Auth Check) → Has Token?
Yes → API (/api/auth/me) → Load User Data → Show Dashboard
No → Redirect to Login
```

**Code Flow:**
```typescript
// frontend/app/(dashboard)/layout.tsx
useEffect(() => {
  const token = localStorage.getItem("token");
  if (!token) router.push("/auth/login");
  // Verify token with backend
  const userData = await api.getCurrentUser();
}, []);
```

### 4. API Request Authentication

All API requests automatically include the JWT token:

```typescript
// frontend/lib/api.ts
this.client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 📊 Key Features & Usage

### 1. Landing Page (`/`)

**Purpose:** Marketing page to attract users

**Features:**
- Hero section with value proposition
- Feature cards (AI Queries, Statistics, Security, etc.)
- How it works (3-step process)
- Benefits list
- Call-to-action buttons

**Access:** Public (no authentication required)

### 2. Dashboard (`/dashboard`)

**Purpose:** Overview of user's data and quick actions

**Features:**
- Statistics cards (Total Datasets, Rows, Columns, Status)
- Quick action buttons
- Recent datasets list
- Getting started guide (for new users)

**Access:** Protected (requires login)

**Code Location:** `frontend/app/(dashboard)/dashboard/page.tsx`

### 3. Upload Data (`/upload`)

**Purpose:** Upload CSV/Excel files for analysis

**Features:**
- File selection with drag-and-drop support
- Dataset naming
- File validation (type, size < 200MB)
- Upload guidelines
- List of existing datasets

**API Endpoint:** `POST /api/data/upload`

**Code Location:** `frontend/app/(dashboard)/upload/page.tsx`

**Usage Example:**
```typescript
const response = await api.uploadDataset(file, datasetName);
// Response includes dataset info: id, name, rows, columns
```

### 4. AI Analysis (`/analysis`)

**Purpose:** Ask questions in natural language

**Features:**
- Dataset selection dropdown
- AI provider configuration (xAI/Groq/Gemini)
- Natural language query input
- Quick question templates
- Tabbed results view:
  - Results table
  - Generated SQL
  - AI interpretation
- Download results as CSV

**API Endpoints:**
- `POST /api/ai/configure` - Set AI provider
- `POST /api/ai/query` - Execute query

**Code Location:** `frontend/app/(dashboard)/analysis/page.tsx`

**Usage Flow:**
1. Select dataset
2. Configure AI (provider, model, API key)
3. Type question: "What are the top 10 customers by revenue?"
4. AI generates SQL, executes, and interprets results

### 5. Visualizations (`/visualize`)

**Purpose:** Create interactive charts from data

**Features:**
- Dataset selection
- Axis configuration (X and Y)
- Multiple chart types:
  - Bar Chart
  - Line Chart
  - Pie Chart
- Real-time preview
- Responsive design

**Code Location:** `frontend/app/(dashboard)/visualize/page.tsx`

**Usage:**
1. Select dataset
2. Choose X-axis (category column)
3. Choose Y-axis (value column)
4. Switch between chart types

### 6. Admin Panel (`/admin`)

**Purpose:** User management (admin users only)

**Features:**
- User statistics
- User list with details
- Role badges (Admin/User)
- Status indicators (Active/Inactive)
- System information

**API Endpoint:** `GET /api/admin/users`

**Access:** Requires `is_admin: true`

**Code Location:** `frontend/app/(dashboard)/admin/page.tsx`

---

## 🔧 API Client Architecture

### Axios Instance with Interceptors

```typescript
// frontend/lib/api.ts
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      headers: { 'Content-Type': 'application/json' }
    });

    // Request interceptor: Add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor: Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/auth/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // API methods
  async login(username: string, password: string) { ... }
  async uploadDataset(file: File, datasetName: string) { ... }
  async queryAI(query: string, datasetId: string) { ... }
}

export const api = new ApiClient();
```

### Usage in Components

```typescript
import { api } from '@/lib/api';

// In component
const handleUpload = async () => {
  try {
    const response = await api.uploadDataset(file, name);
    console.log('Upload successful:', response);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

## 🗄️ State Management

### Zustand Store

```typescript
// frontend/store/useStore.ts
interface AppState {
  user: User | null;
  currentDataset: Dataset | null;
  datasets: Dataset[];
  setUser: (user: User | null) => void;
  setCurrentDataset: (dataset: Dataset | null) => void;
  setDatasets: (datasets: Dataset[]) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  currentDataset: null,
  datasets: [],
  setUser: (user) => set({ user }),
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
  setDatasets: (datasets) => set({ datasets }),
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, currentDataset: null, datasets: [] });
  },
}));
```

### Usage in Components

```typescript
import { useStore } from '@/store/useStore';

function Dashboard() {
  const { user, datasets, setDatasets } = useStore();

  useEffect(() => {
    // Load datasets
    const loadData = async () => {
      const response = await api.getDatasets();
      setDatasets(response.datasets);
    };
    loadData();
  }, []);

  return <div>Welcome, {user?.full_name}!</div>;
}
```

---

## 🎨 UI Components (Shadcn)

### Using UI Components

All UI components are in `frontend/components/ui/`:

```typescript
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';

function MyComponent() {
  const { toast } = useToast();

  const handleClick = () => {
    toast({
      title: "Success!",
      description: "Action completed successfully",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>My Card</CardTitle>
      </CardHeader>
      <CardContent>
        <Input placeholder="Enter text" />
        <Button onClick={handleClick}>Submit</Button>
      </CardContent>
    </Card>
  );
}
```

### Toast Notifications

```typescript
// Success toast
toast({
  title: "Upload successful!",
  description: "Dataset uploaded with 1,000 rows",
});

// Error toast
toast({
  title: "Upload failed",
  description: "File size exceeds 200MB limit",
  variant: "destructive",
});
```

---

## 🔄 Complete User Journey

### New User Flow

1. **Landing Page** (`/`)
   - User sees features and benefits
   - Clicks "Get Started"

2. **Registration** (`/auth/register`)
   - Fills form: name, username, email, password
   - Backend creates user in Supabase
   - Redirects to login

3. **Login** (`/auth/login`)
   - Enters credentials
   - Backend verifies and issues JWT token
   - Token stored in localStorage
   - Redirects to dashboard

4. **Dashboard** (`/dashboard`)
   - Sees empty state with "Getting Started" guide
   - Clicks "Upload Dataset"

5. **Upload Data** (`/upload`)
   - Selects CSV file
   - Names dataset (e.g., "Sales Q4 2024")
   - Uploads (backend processes and stores)
   - Sees dataset in list

6. **AI Analysis** (`/analysis`)
   - Selects uploaded dataset
   - Configures AI provider (Groq)
   - Enters API key
   - Types question: "What are the top 5 products by revenue?"
   - AI generates SQL, executes, shows results
   - Can download as CSV

7. **Visualizations** (`/visualize`)
   - Selects dataset
   - Chooses Product (X-axis) and Revenue (Y-axis)
   - Views bar chart
   - Switches to pie chart

### Returning User Flow

1. **Login** (`/auth/login`)
   - Enters credentials
   - JWT token issued

2. **Dashboard** (`/dashboard`)
   - Sees recent datasets
   - Views statistics
   - Quick actions available

3. **Continue Analysis**
   - AI config persists in backend
   - Can immediately query any dataset

---

## 🛠️ Development Workflow

### Adding a New Page

1. **Create page file:**
```bash
touch frontend/app/(dashboard)/reports/page.tsx
```

2. **Add to navigation:**
```typescript
// frontend/components/dashboard/Sidebar.tsx
const routes = [
  // ... existing routes
  {
    label: "Reports",
    icon: FileText,
    href: "/reports",
    color: "text-green-500",
  },
];
```

3. **Implement page:**
```typescript
// frontend/app/(dashboard)/reports/page.tsx
"use client";

import { Card } from "@/components/ui/card";

export default function ReportsPage() {
  return (
    <div>
      <h1 className="text-4xl font-bold mb-4">Reports</h1>
      <Card>
        {/* Your content */}
      </Card>
    </div>
  );
}
```

### Adding a New API Endpoint

1. **Backend endpoint:**
```python
# backend_api/main.py
@app.get("/api/reports")
async def get_reports(payload: Dict = Depends(verify_token)):
    # Your logic
    return {"reports": [...]}
```

2. **Frontend API client:**
```typescript
// frontend/lib/api.ts
async getReports() {
  const response = await this.client.get('/reports');
  return response.data;
}
```

3. **Use in component:**
```typescript
const reports = await api.getReports();
```

---

## 🚀 Production Deployment

### Backend Deployment (Railway/Render)

1. **Create `Procfile`:**
```
web: uvicorn backend_api.main:app --host 0.0.0.0 --port $PORT
```

2. **Update CORS:**
```python
# backend_api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-app.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Set environment variables** in Railway/Render dashboard

4. **Deploy:**
```bash
# Railway
railway up

# Render
git push
```

### Frontend Deployment (Vercel)

1. **Push to GitHub**

2. **Import to Vercel:**
   - Select repository
   - Set root directory: `frontend`
   - Framework: Next.js

3. **Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
```

4. **Deploy** (automatic on git push)

### Custom Domain Setup

1. **Backend:** Add custom domain in Railway/Render
2. **Frontend:** Add custom domain in Vercel
3. **Update CORS** to include custom domain

---

## 📊 Monitoring & Logs

### Backend Logs

```bash
# View logs directory
ls -l logs/

# Watch application logs
tail -f logs/app.log

# Watch error logs
tail -f logs/error.log

# Watch audit logs (user actions)
tail -f logs/audit.log
```

### Frontend Logs

```bash
# Browser console (F12)
# Shows API calls, errors, state changes

# Next.js terminal
# Shows build errors, API routes
```

---

## 🐛 Common Issues & Solutions

### Issue: Frontend can't connect to backend

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Verify NEXT_PUBLIC_API_URL
cat frontend/.env.local

# Should be: NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Issue: 401 Unauthorized on dashboard

**Solution:**
```javascript
// Clear localStorage and login again
localStorage.clear();
// Go to /auth/login
```

### Issue: CORS errors

**Solution:**
```python
# backend_api/main.py
# Ensure localhost:3000 is in allow_origins
allow_origins=["http://localhost:3000"]
```

### Issue: File upload fails

**Solution:**
```bash
# Check file size (< 200MB)
# Verify file type (.csv, .xlsx, .xls)
# Check backend logs for errors
```

### Issue: AI queries fail

**Solution:**
```bash
# Verify AI API key is correct
# Check .env file has valid keys
# Test API key directly with provider
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] **Landing page** loads without errors
- [ ] **Registration** creates new user
- [ ] **Login** with valid credentials works
- [ ] **Login** with invalid credentials fails
- [ ] **Dashboard** shows after login
- [ ] **Upload** CSV file succeeds
- [ ] **Upload** validates file size/type
- [ ] **AI Analysis** can be configured
- [ ] **AI Query** returns results
- [ ] **Visualizations** render correctly
- [ ] **Logout** clears session
- [ ] **Admin panel** only accessible to admins
- [ ] **Protected routes** redirect to login when not authenticated

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"testpass123"}'

# Get datasets (with token)
curl http://localhost:8000/api/data/datasets \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 💡 Best Practices

### Frontend

1. **Always use TypeScript types**
```typescript
interface User {
  username: string;
  email: string;
  full_name: string;
  is_admin: boolean;
}
```

2. **Handle loading states**
```typescript
const [loading, setLoading] = useState(false);
// Show spinner when loading
```

3. **Handle errors gracefully**
```typescript
try {
  await api.uploadDataset(file, name);
} catch (error) {
  toast({ title: "Error", description: error.message });
}
```

4. **Use environment variables**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

### Backend

1. **Always validate inputs**
```python
if not username or not password:
    raise HTTPException(status_code=400, detail="Missing fields")
```

2. **Log important events**
```python
logger.info(f"User {username} uploaded dataset")
```

3. **Use proper HTTP status codes**
```python
return JSONResponse(status_code=201, content={"id": dataset_id})
```

4. **Secure endpoints with authentication**
```python
async def protected_route(payload: Dict = Depends(verify_token)):
    # Only authenticated users can access
```

---

## 📚 Additional Resources

### Frontend (Next.js/React)
- Next.js Docs: https://nextjs.org/docs
- React Docs: https://react.dev
- Tailwind CSS: https://tailwindcss.com
- Shadcn UI: https://ui.shadcn.com
- Zustand: https://github.com/pmndrs/zustand

### Backend (FastAPI)
- FastAPI Docs: https://fastapi.tiangolo.com
- Python Type Hints: https://docs.python.org/3/library/typing.html

### Database
- Supabase Docs: https://supabase.com/docs

### AI Providers
- Groq: https://console.groq.com
- Google Gemini: https://ai.google.dev

---

## 🎯 What Makes This Different from Streamlit

| Feature | Streamlit Version | Modern UI Version |
|---------|------------------|-------------------|
| **Technology** | Python monolith | Separated frontend/backend |
| **UI Framework** | Streamlit widgets | React + Tailwind CSS |
| **Routing** | Pages in sidebar | Full Next.js routing |
| **Authentication** | Session-based | JWT token-based |
| **API** | No separate API | RESTful FastAPI |
| **Deployment** | Single server | Frontend (Vercel) + Backend (Railway) |
| **Scalability** | Limited | Highly scalable |
| **Customization** | Streamlit constraints | Fully customizable |
| **Mobile** | Limited | Responsive design |
| **Production Ready** | Demo/prototype | Enterprise SaaS |

---

## ✅ You're All Set!

Your modern VexaAI platform is ready to use and sell! Key points:

1. **Two Versions:** Streamlit (original) and Modern UI (new) - both work independently
2. **Production Ready:** Modern UI is built for SaaS with proper auth, API, and deployment strategy
3. **Fully Documented:** This guide covers everything from development to deployment
4. **Monetization Ready:** Add Stripe, usage limits, and start selling!

**Start both servers and test your application:**
```bash
# Terminal 1: Backend
uvicorn backend_api.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Then visit http://localhost:3000 and start building your analytics empire! 🚀
