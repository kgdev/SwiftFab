# SwiftFab Monorepo Structure

## 📁 **Complete Directory Structure**

```
SwiftFab/
├── backend/                          # 🐍 Python Backend Service
│   ├── main.py                      # FastAPI application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── railway.json                 # Railway backend configuration
│   ├── nixpacks.toml               # Backend Nixpacks configuration
│   ├── Dockerfile                   # Backend Docker configuration
│   ├── Dockerfile.minimal          # Minimal backend Docker config
│   ├── build-vercel.sh             # Vercel build script
│   ├── install-freecad.sh          # FreeCAD installation script
│   ├── database_blob_storage.py    # Database blob storage implementation
│   ├── simple_step_parser.py       # FreeCAD STEP file parser
│   ├── final_price_calculator.py   # Price calculation logic
│   ├── freecad_api_client.py       # FreeCAD API client
│   ├── shopify_integration.py      # Shopify integration
│   ├── shopify_oauth.py            # Shopify OAuth handling
│   ├── config.py                   # Configuration management
│   ├── config.json                 # Configuration file
│   ├── __init__.py                 # Python package marker
│   └── uploads/                     # File upload directory
├── frontend/                        # ⚛️ React Frontend Service
│   ├── package.json                # Frontend dependencies
│   ├── package-lock.json           # Locked dependency versions
│   ├── railway.json                # Railway frontend configuration
│   ├── nixpacks.toml               # Frontend Nixpacks configuration
│   ├── vercel.json                 # Vercel frontend configuration
│   ├── tsconfig.json               # TypeScript configuration
│   ├── public/                     # Static assets
│   ├── src/                        # React source code
│   │   ├── components/             # React components
│   │   ├── pages/                 # Page components
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── types/                 # TypeScript type definitions
│   │   └── config/               # Frontend configuration
│   └── build/                      # Production build output
├── database/                        # 🗄️ Database Service
│   └── railway.json                # Railway database configuration
├── data/                           # 📊 Data Files
│   ├── materials.json              # Materials database
│   └── quote_*/                    # Quote data directories
├── scripts/                        # 🔧 Utility Scripts
│   ├── analyze/                    # Analysis scripts
│   └── extractor/                  # Data extraction scripts
├── package.json                    # 📦 Monorepo root configuration
├── railway.json                    # 🚂 Root Railway configuration
├── nixpacks.toml                   # 🔨 Root Nixpacks configuration
├── railway.template.json           # 📋 Railway template (JSON)
├── railway.template.yaml           # 📋 Railway template (YAML)
├── railway.template.toml            # 📋 Railway template (TOML)
├── vercel.json                     # ▲ Vercel configuration
├── render.yaml                     # 🚀 Render.com configuration
├── .gitignore                      # 🚫 Git ignore rules
├── README.md                       # 📖 Main documentation
├── RAILWAY_TEMPLATE.md             # 📋 Railway template documentation
├── RAILWAY_DEPLOYMENT.md           # 🚂 Railway deployment guide
├── RAILWAY_FULL_MIGRATION.md      # 🔄 Complete migration guide
└── MONOREPO_STRUCTURE.md          # 📁 This file
```

## 🎯 **Service Isolation**

### **Backend Service (`backend/`)**
- **Complete Python environment** with all dependencies
- **FastAPI application** with STEP file parsing
- **FreeCAD integration** for 3D file processing
- **Database blob storage** implementation
- **Shopify integration** for e-commerce
- **All backend configurations** (Railway, Docker, Vercel)

### **Frontend Service (`frontend/`)**
- **Complete React environment** with all dependencies
- **TypeScript configuration** and type definitions
- **Component-based architecture** with hooks
- **Production build** configuration
- **All frontend configurations** (Railway, Vercel)

### **Database Service (`database/`)**
- **PostgreSQL configuration** for Railway
- **Database-specific settings**

## 🚀 **Deployment Configurations**

### **Railway Deployment**
- **Root**: `railway.json` + `nixpacks.toml` (backend service)
- **Backend**: `backend/railway.json` + `backend/nixpacks.toml`
- **Frontend**: `frontend/railway.json` + `frontend/nixpacks.toml`
- **Database**: `database/railway.json`
- **Templates**: Multiple format support (JSON, YAML, TOML)

### **Vercel Deployment**
- **Root**: `vercel.json` (full-stack configuration)
- **Frontend**: `frontend/vercel.json` (frontend-only)

### **Other Platforms**
- **Render.com**: `render.yaml`
- **Docker**: `backend/Dockerfile` + `backend/Dockerfile.minimal`

## 🔧 **Monorepo Scripts**

```json
{
  "dev": "Start both backend and frontend",
  "dev:backend": "Start backend only",
  "dev:frontend": "Start frontend only", 
  "build": "Build frontend for production",
  "install:all": "Install all dependencies",
  "deploy:railway": "Deploy to Railway",
  "deploy:vercel": "Deploy to Vercel"
}
```

## ✅ **Benefits of Isolated Monorepo**

1. **Complete Isolation**: Each service is self-contained
2. **Independent Deployment**: Services can be deployed separately
3. **Clear Separation**: Backend and frontend are completely separate
4. **Easy Maintenance**: Each service has its own dependencies and configs
5. **Flexible Deployment**: Choose which services to deploy where
6. **Team Collaboration**: Different teams can work on different services
7. **Technology Independence**: Backend and frontend can use different tech stacks

## 🎯 **Deployment Options**

### **Option 1: Full Stack Railway**
```bash
railway template deploy
```

### **Option 2: Service-by-Service Railway**
```bash
# Deploy backend
cd backend && railway up

# Deploy frontend  
cd frontend && railway up

# Deploy database
cd database && railway up
```

### **Option 3: Mixed Platform**
- **Backend**: Railway (for FreeCAD support)
- **Frontend**: Vercel (for React optimization)
- **Database**: Railway PostgreSQL

This monorepo structure provides complete isolation while maintaining easy coordination and deployment!
