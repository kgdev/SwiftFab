# SwiftFab Railway Template

This template deploys a complete SwiftFab application with three services:

## 🏗️ **Services Architecture**

### **1. Database Service (swiftfab-database)**
- **Type**: PostgreSQL database
- **Builder**: RAILWAY
- **Purpose**: Stores application data and blob storage

### **2. Backend Service (swiftfab-backend)**
- **Type**: FastAPI Python application
- **Builder**: NIXPACKS (Python 3.9 + FreeCAD)
- **Purpose**: API server with STEP file parsing
- **Dependencies**: Database service
- **Health Check**: `/api/health`

### **3. Frontend Service (swiftfab-frontend)**
- **Type**: React application
- **Builder**: NIXPACKS (Node.js + npm)
- **Purpose**: Web interface
- **Dependencies**: Backend service
- **Health Check**: `/`

## 🚀 **Deployment Options**

### **Option 1: Railway Template (Recommended)**
```bash
# Deploy using Railway template
railway template deploy
```

### **Option 2: Manual Service Deployment**
```bash
# Deploy database first
cd database && railway up

# Deploy backend
railway up

# Deploy frontend
cd frontend && railway up
```

### **Option 3: Railway Web Interface**
1. Go to https://railway.app
2. Create new project from GitHub repo
3. Railway will automatically detect the template
4. Deploy all services with dependencies

## 🔧 **Environment Variables**

### **Backend Service**
- `DATABASE_URL`: `${{swiftfab-database.DATABASE_URL}}`
- `PORT`: `8000`

### **Frontend Service**
- `REACT_APP_API_URL`: `${{swiftfab-backend.RAILWAY_PUBLIC_DOMAIN}}`
- `PORT`: `3000`

## 📁 **Service Sources**

- **Database**: `database/` directory
- **Backend**: Root directory (`.`)
- **Frontend**: `frontend/` directory

## 🔄 **Deployment Order**

1. **Database** → Created first
2. **Backend** → Waits for database, deploys with FreeCAD
3. **Frontend** → Waits for backend, builds React app

## 🎯 **Features**

- ✅ **FreeCAD Support**: Backend includes FreeCAD for STEP parsing
- ✅ **Database Blob Storage**: Files stored in PostgreSQL
- ✅ **Health Checks**: Automatic service health monitoring
- ✅ **Auto-restart**: Services restart on failure
- ✅ **Service Dependencies**: Proper startup order
- ✅ **Environment Linking**: Services automatically connect

## 📋 **Prerequisites**

- Railway account
- GitHub repository with this template
- Railway CLI (optional)

## 🚀 **Quick Start**

1. **Clone this repository**
2. **Deploy to Railway**:
   ```bash
   railway template deploy
   ```
3. **Set environment variables** (if needed)
4. **Access your application** via Railway URLs

## 🔍 **Monitoring**

- **Backend Health**: `https://your-backend-url.railway.app/api/health`
- **Frontend**: `https://your-frontend-url.railway.app`
- **Database**: Managed by Railway

## 🛠️ **Customization**

- Modify `railway.template.json` for service configuration
- Update `nixpacks.toml` files for build customization
- Adjust environment variables as needed

This template provides a complete, production-ready SwiftFab deployment on Railway!
