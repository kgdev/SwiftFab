# SwiftFab Monorepo

Complete manufacturing quote system with STEP file parsing, built as an isolated monorepo.

## 🏗️ **Monorepo Structure**

```
SwiftFab/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── railway.json        # Railway backend config
│   ├── nixpacks.toml      # Backend Nixpacks config
│   ├── Dockerfile         # Backend Docker config
│   └── ...                # Backend source files
├── frontend/               # React frontend
│   ├── package.json       # Frontend dependencies
│   ├── railway.json       # Railway frontend config
│   ├── nixpacks.toml      # Frontend Nixpacks config
│   └── ...                # Frontend source files
├── database/               # Database configuration
│   └── railway.json       # Railway database config
├── package.json           # Monorepo root configuration
├── railway.json           # Root Railway config
├── nixpacks.toml          # Root Nixpacks config
└── README.md              # This file
```

## 🚀 **Quick Start**

### **Development**
```bash
# Install all dependencies
npm run install:all

# Start both backend and frontend
npm run dev

# Start backend only
npm run dev:backend

# Start frontend only
npm run dev:frontend
```

### **Production Build**
```bash
# Build frontend
npm run build
```

## 🏢 **Services**

### **Backend Service**
- **Location**: `backend/` folder
- **Technology**: Python FastAPI + FreeCAD
- **Features**: STEP file parsing, quote generation, database blob storage
- **Health Check**: `/api/health`

### **Frontend Service**
- **Location**: `frontend/` folder
- **Technology**: React + TypeScript
- **Features**: File upload, quote management, responsive UI
- **Health Check**: `/`

### **Database Service**
- **Location**: `database/` folder
- **Technology**: PostgreSQL
- **Features**: Data storage, blob storage, user management

## 🚀 **Deployment**

### **Railway (Recommended)**
```bash
# Deploy using Railway template
npm run deploy:railway

# Or manually
railway template deploy
```

### **Vercel**
```bash
# Deploy to Vercel
npm run deploy:vercel
```

## 🔧 **Configuration**

### **Backend Configuration**
- **Railway**: `backend/railway.json`
- **Nixpacks**: `backend/nixpacks.toml`
- **Docker**: `backend/Dockerfile`
- **Dependencies**: `backend/requirements.txt`

### **Frontend Configuration**
- **Railway**: `frontend/railway.json`
- **Nixpacks**: `frontend/nixpacks.toml`
- **Dependencies**: `frontend/package.json`

### **Database Configuration**
- **Railway**: `database/railway.json`

## 📋 **Scripts**

| Script | Description |
|--------|-------------|
| `npm run dev` | Start both backend and frontend |
| `npm run dev:backend` | Start backend only |
| `npm run dev:frontend` | Start frontend only |
| `npm run build` | Build frontend for production |
| `npm run install:all` | Install all dependencies |
| `npm run deploy:railway` | Deploy to Railway |
| `npm run deploy:vercel` | Deploy to Vercel |

## 🎯 **Features**

- ✅ **STEP File Parsing**: FreeCAD-based STEP file analysis
- ✅ **Quote Generation**: Automated manufacturing quotes
- ✅ **Database Blob Storage**: File storage in PostgreSQL
- ✅ **Responsive UI**: Modern React interface
- ✅ **Health Monitoring**: Built-in health checks
- ✅ **Auto-restart**: Service restart on failure
- ✅ **Service Dependencies**: Proper startup order

## 🔍 **Health Checks**

- **Backend**: `https://your-backend-url.railway.app/api/health`
- **Frontend**: `https://your-frontend-url.railway.app/`
- **Database**: Managed by Railway

## 🛠️ **Development**

### **Backend Development**
```bash
cd backend
python3 main.py
```

### **Frontend Development**
```bash
cd frontend
npm start
```

### **Full Stack Development**
```bash
# From root directory
npm run dev
```

## 📁 **Isolated Structure**

Each service is completely isolated:
- **Backend**: All Python files, dependencies, and configs in `backend/`
- **Frontend**: All React files, dependencies, and configs in `frontend/`
- **Database**: Database configuration in `database/`
- **Root**: Monorepo coordination and deployment configs

This structure ensures clean separation of concerns and easy maintenance!