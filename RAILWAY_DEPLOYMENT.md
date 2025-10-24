# Railway Deployment Guide

## Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository with your code

## Deployment Steps

### 1. Connect to Railway
1. Go to https://railway.app
2. Sign in with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your SwiftFab repository

### 2. Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```
DATABASE_URL=postgresql://postgres:PhNsgTilyTBMolsu@db.auggguqxtxtidaobjpiu.supabase.co:5432/postgres
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_Wj0leTN2NCkOK2CI_9VEW1xPeKWkAg0wZzvOQJMvZWeEMys
```

### 3. Railway Configuration
The project includes:
- `railway.json` - Railway configuration
- `Dockerfile` - Docker configuration with FreeCAD
- `requirements.txt` - Python dependencies

### 4. Deploy
Railway will automatically:
1. Build the Docker image with FreeCAD
2. Install Python dependencies
3. Start the application
4. Provide a public URL

### 5. Verify Deployment
- Check the Railway logs for any errors
- Test the `/api/health` endpoint
- Upload a STEP file to test FreeCAD parsing

## Benefits of Railway
- ✅ **Docker Support**: Can run FreeCAD in containers
- ✅ **Persistent Storage**: Better for FreeCAD than serverless
- ✅ **Environment Variables**: Easy configuration
- ✅ **Automatic Deployments**: Deploys on git push
- ✅ **FreeCAD Compatible**: Full Linux environment

## Troubleshooting
- Check Railway logs if deployment fails
- Ensure environment variables are set correctly
- Verify Dockerfile builds successfully
- Test FreeCAD import in the container
