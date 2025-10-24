# Complete Railway Migration Guide

## Overview
This guide migrates both frontend and backend to Railway, including:
- ✅ PostgreSQL database for data storage
- ✅ Database-based blob storage (replaces Vercel Blob)
- ✅ FreeCAD support via Docker
- ✅ Frontend and backend services

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository with your code

## Step 1: Railway Project Setup

### 1.1 Create Railway Project
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your SwiftFab repository

### 1.2 Add PostgreSQL Database
1. In your project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. Note the connection details (DATABASE_URL will be auto-generated)

## Step 2: Backend Service Setup

### 2.1 Create Backend Service
1. Click "New Service" in your project
2. Select "GitHub Repo"
3. Choose your SwiftFab repository
4. Service name: `swiftfab-backend`

### 2.2 Configure Backend Service
1. **Build Settings**:
   - Root Directory: `/`
   - Build Command: Railway will auto-detect Dockerfile
   - Start Command: `python3 backend/main.py`

2. **Environment Variables**:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   PORT=8000
   ```

### 2.3 Backend Features
- ✅ **FreeCAD Support**: Dockerfile installs FreeCAD
- ✅ **Database Blob Storage**: Files stored in PostgreSQL
- ✅ **STEP File Parsing**: Full FreeCAD functionality
- ✅ **API Endpoints**: All existing endpoints work

## Step 3: Frontend Service Setup

### 3.1 Create Frontend Service
1. Click "New Service" in your project
2. Select "GitHub Repo"
3. Choose your SwiftFab repository
4. Service name: `swiftfab-frontend`

### 3.2 Configure Frontend Service
1. **Build Settings**:
   - Root Directory: `/frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`

2. **Environment Variables**:
   ```
   REACT_APP_API_URL=${{swiftfab-backend.RAILWAY_PUBLIC_DOMAIN}}
   PORT=3000
   ```

## Step 4: Database Schema Setup

### 4.1 Database Tables
The backend will automatically create these tables:
- `quotes` - Quote information
- `parts` - Part details
- `blob_storage` - File storage (replaces Vercel Blob)

### 4.2 Database Blob Storage
- Files are stored as binary data in PostgreSQL
- Blob URLs use format: `blob://{blob_id}`
- Automatic cleanup and metadata tracking

## Step 5: Environment Variables

### 5.1 Backend Environment Variables
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
PORT=8000
```

### 5.2 Frontend Environment Variables
```
REACT_APP_API_URL=${{swiftfab-backend.RAILWAY_PUBLIC_DOMAIN}}
PORT=3000
```

## Step 6: Deployment Process

### 6.1 Automatic Deployment
1. Railway detects changes in your GitHub repo
2. Automatically rebuilds and redeploys services
3. Database migrations run automatically

### 6.2 Manual Deployment
```bash
# Push changes to trigger deployment
git add .
git commit -m "Deploy to Railway"
git push origin main
```

## Step 7: Testing

### 7.1 Backend Testing
1. Check backend health: `{backend_url}/api/health`
2. Test STEP file upload: `{backend_url}/api/upload`
3. Verify FreeCAD parsing works

### 7.2 Frontend Testing
1. Check frontend: `{frontend_url}`
2. Test file upload functionality
3. Verify quote generation

### 7.3 Database Testing
1. Check database connection
2. Verify blob storage works
3. Test data persistence

## Benefits of Railway Migration

### ✅ **Complete Solution**
- **Database**: PostgreSQL for all data storage
- **Blob Storage**: Database-based file storage
- **FreeCAD**: Full Docker support
- **Frontend**: React app deployment
- **Backend**: FastAPI with FreeCAD

### ✅ **Railway Advantages**
- **Docker Support**: Full Linux environment
- **PostgreSQL**: Managed database service
- **Automatic Deployments**: Git-based deployments
- **Environment Variables**: Easy configuration
- **Health Checks**: Automatic monitoring
- **Scaling**: Easy horizontal scaling

### ✅ **Cost Benefits**
- **No Vercel Blob costs**: Database storage is included
- **Unified platform**: Everything in one place
- **Free tier**: Generous free usage limits

## Troubleshooting

### Common Issues
1. **Database Connection**: Check DATABASE_URL environment variable
2. **FreeCAD Import**: Verify Dockerfile builds correctly
3. **Frontend Build**: Check Node.js version compatibility
4. **Blob Storage**: Verify database blob storage works

### Debug Commands
```bash
# Check Railway logs
railway logs

# Check service status
railway status

# View environment variables
railway variables
```

## Migration Checklist

- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Backend service configured
- [ ] Frontend service configured
- [ ] Environment variables set
- [ ] Database blob storage working
- [ ] FreeCAD parsing working
- [ ] Frontend-backend communication working
- [ ] File upload/download working
- [ ] Quote generation working

## Next Steps

1. **Deploy to Railway**: Follow the steps above
2. **Test thoroughly**: Verify all functionality works
3. **Update DNS**: Point your domain to Railway
4. **Monitor**: Use Railway dashboard for monitoring
5. **Scale**: Add more resources as needed

This migration provides a complete, scalable solution with FreeCAD support and database-based blob storage!
