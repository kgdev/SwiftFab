# SwiftFab - 3D Part Quoting System

A complete manufacturing quote system with STEP file parsing, automated pricing, and Shopify integration.

## 🏗️ **Project Structure**

```
SwiftFab/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Main application
│   ├── database.py            # Database models and connection
│   ├── cadquery_step_parser.py # CADQuery STEP parser
│   ├── final_price_calculator.py # Pricing calculator
│   ├── shopify_integration.py  # Shopify integration
│   ├── shopify_oauth.py       # Shopify OAuth
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   └── railway.json          # Railway deployment config
├── frontend/                  # React + TypeScript frontend
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   ├── package.json          # Frontend dependencies
│   └── railway.json          # Railway deployment config
├── scripts/                   # Utility scripts
│   ├── extractor/            # Data extraction scripts
│   │   ├── fabworks_api_client.py    # Fabworks API client
│   │   └── permute_all_materials.py  # Material permutation tester
│   └── analyze/              # Data analysis scripts
│       ├── extract_pricing_data.py   # Extract pricing data
│       └── final_pricing_analysis.py # Pricing formula analysis
├── data/                      # Data directory (local)
├── Dockerfile                 # Docker build config
├── railway.json              # Railway root config
├── uv.lock                   # UV dependency lock file
└── README.md                 # This file
```

## 🚀 **Local Development Setup (WSL)**

### **Prerequisites**
- WSL2 (Windows Subsystem for Linux)
- Python 3.11+ 
- Node.js 18+
- Docker (for PostgreSQL)
- UV (Python package manager)

### **1. Install UV**
```bash
# In WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your shell or run:
source ~/.bashrc
```

### **2. Start PostgreSQL with Docker**

Create a script `start-postgres.sh`:
```bash
#!/bin/bash
# Start PostgreSQL container for local development

docker run -d \
  --name swiftfab-postgres \
  -e POSTGRES_USER=swiftfab \
  -e POSTGRES_PASSWORD=swiftfab123 \
  -e POSTGRES_DB=swiftfab \
  -p 5432:5432 \
  --restart unless-stopped \
  postgres:15-alpine

echo "PostgreSQL started on localhost:5432"
echo "Database: swiftfab"
echo "User: swiftfab"
echo "Password: swiftfab123"
echo ""
echo "Connection string:"
echo "postgresql://swiftfab:swiftfab123@localhost:5432/swiftfab"
```

Make it executable and run:
```bash
chmod +x start-postgres.sh
./start-postgres.sh
```

**Useful Docker commands:**
```bash
# Stop PostgreSQL
docker stop swiftfab-postgres

# Start existing container
docker start swiftfab-postgres

# View logs
docker logs swiftfab-postgres

# Remove container (data will be lost)
docker rm -f swiftfab-postgres

# Access PostgreSQL CLI
docker exec -it swiftfab-postgres psql -U swiftfab -d swiftfab
```

### **3. Configure Environment Variables**

Create `backend/.env` file:
```bash
# Database Configuration
DATABASE_URL=postgresql://swiftfab:swiftfab123@localhost:5432/swiftfab
```

That's it! No other environment variables are required for local development.

**Optional: Frontend Environment Variables**

The frontend automatically uses `http://localhost:8000` for API calls in development mode.

If you need to change this, create `frontend/.env.local`:
```bash
# Only needed if backend is NOT on localhost:8000
REACT_APP_API_BASE_URL=http://your-backend-url:port
```

**Note**: Environment variables in React must use the `REACT_APP_` prefix to be included in the build.

### **4. Install Backend Dependencies**
```bash
cd backend
uv pip install -r requirements.txt
```

### **5. Start Backend**
```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### **6. Start Frontend**

In a new terminal:
```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

### **Health Checks**
- Backend health check: `http://localhost:8000/api/health`
- Frontend: `http://localhost:3000`

### **Quick Start Script**

Create a `dev.sh` script for easy startup:
```bash
#!/bin/bash
# Quick development startup script

# Check if PostgreSQL is running
if ! docker ps | grep -q swiftfab-postgres; then
    echo "Starting PostgreSQL..."
    docker start swiftfab-postgres || ./start-postgres.sh
fi

# Start backend in background
echo "Starting backend..."
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Usage:
```bash
chmod +x dev.sh
./dev.sh
```

## 🚂 **Deploy to Railway**

### **Method 1: Railway CLI (Recommended)**

#### **1. Install Railway CLI**
```bash
# In WSL
curl -fsSL https://railway.app/install.sh | sh

# Or via npm
npm install -g @railway/cli
```

#### **2. Login to Railway**
```bash
railway login
```

#### **3. Initialize Project**
```bash
# In project root
railway init
```

#### **4. Link to Existing Project (if already created)**
```bash
railway link
```

#### **5. Deploy**
```bash
# Deploy backend
cd backend
railway up

# Deploy frontend
cd frontend
railway up
```

### **Method 2: Auto Deploy via GitHub**

#### **1. Connect GitHub Repository**
- Login to [Railway Dashboard](https://railway.app/dashboard)
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose `SwiftFab` repository

#### **2. Service Configuration**

Railway will automatically detect the `railway.json` configuration files.

**Backend Service Config:**
```json
{
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "python3 main.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Frontend Service Config:**
```json
{
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "npm run serve",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

#### **3. Configure Environment Variables**

**Backend Service:**
Set in Railway Dashboard:
- `DATABASE_URL` - PostgreSQL connection string (automatically provided)
- `PORT` - Port number (automatically set)

**Frontend Service (Optional):**
- `REACT_APP_API_BASE_URL` - Backend API URL (only if backend is on different domain)
  - If frontend and backend are on the same domain, leave this unset (uses relative URLs)
  - Example: `https://swiftfab-backend.railway.app`
  - By default, the frontend uses relative URLs which work when both services are on the same domain

That's all you need! Other services (Azure Blob, Shopify) are optional.

#### **4. Add PostgreSQL Database**
- In Railway Dashboard, click "New"
- Select "Database" → "PostgreSQL"
- Railway will automatically generate the `DATABASE_URL` environment variable

#### **5. Monitor Deployment**
```bash
# View logs
railway logs

# View backend logs
railway logs --service backend

# View frontend logs
railway logs --service frontend
```

### **Deployment Notes**

1. **Health Check Timeout**: Set to 100 seconds to accommodate CADQuery initialization
2. **Restart Policy**: Backend retries up to 10 times, frontend 5 times
3. **Railpack Builder**: Uses new Railpack instead of deprecated Nixpacks
4. **Port Configuration**: Uses `$PORT` environment variable for dynamic port binding

### **Verify Deployment**
- Backend: `https://your-backend-url.railway.app/api/health`
- Frontend: `https://your-frontend-url.railway.app/`

## 📊 **Data Extraction and Analysis Tools**

### **Extractor Scripts - Data Extraction**

Scripts located in `scripts/extractor/` directory are used to extract data from Fabworks API.

#### **1. Fabworks API Client**

`fabworks_api_client.py` provides a client for interacting with the Fabworks tRPC API.

**Basic Usage:**
```bash
cd scripts/extractor
uv run python fabworks_api_client.py
```

**Main Features:**
- Get materials list
- Get finish options
- Update quote information
- Batch API calls

**Example Code:**
```python
from fabworks_api_client import FabworksAPIClient

# Initialize client (requires browser cookies)
client = FabworksAPIClient(cookies="your_cookie_string")

# Get materials list
materials = client.get_materials()

# Get quote details
quote = client.get_quote("qte_123456789")

# Update part materials
client.update_parts_materials(
    quote_id="qte_123456789",
    material_type="Aluminum",
    material_grade="6061-T6",
    thickness=0.125
)
```

#### **2. Material Permutation Testing**

`permute_all_materials.py` tests all material combinations and saves results.

**Usage:**
```bash
cd scripts/extractor

# Basic usage
uv run python permute_all_materials.py --quote-id qte_123456789

# With output prefix
uv run python permute_all_materials.py -q qte_123456789 --output-prefix "test_run"

# With custom materials file
uv run python permute_all_materials.py -q qte_123456789 --materials-file samples/materials.json
```

**Parameters:**
- `--quote-id, -q`: Fabworks quote ID (required)
- `--output-prefix`: Output file prefix (optional)
- `--materials-file`: Materials config file path (default: `samples/materials.json`)

**Features:**
1. Read all material combinations from `materials.json`
2. Iterate through all: material type × grade × thickness × finish combinations
3. Call Fabworks API to update quote for each combination
4. Save quote results to JSON files
5. Output to `data/` directory

**Output Format:**
```
data/
├── [output_prefix]_[material]_[grade]_[thickness]_[finish].json
├── ...
```

**Example Output Filenames:**
- `test_run_Aluminum_6061-T6_0.125_Anodized-Clear.json`
- `test_run_Steel_Mild_0.25_PowderCoating-Black.json`

### **Analyze Scripts - Data Analysis**

Scripts located in `scripts/analyze/` directory analyze extracted data and derive pricing formulas.

#### **1. Extract Pricing Data**

`extract_pricing_data.py` extracts pricing data from JSON files and generates CSV.

**Usage:**
```bash
cd scripts/analyze
uv run python extract_pricing_data.py
```

**Features:**
1. Scan all JSON files in `data/` directory
2. Extract the following fields:
   - Material type (material_type)
   - Material grade (material_grade)
   - Material thickness (material_thickness)
   - Finish (finish)
   - Part dimensions (dimensions)
   - Material usage area (mat_use_sqin)
   - Number of cuts (num_cuts)
   - Price per part (price_per_part)
3. Generate `pricing_data.csv` file

**Output CSV Format:**
```csv
material_type,material_grade,material_thickness,finish,mat_use_sqin,num_cuts,price_per_part
Aluminum,6061-T6,0.125,Anodized-Clear,15.23,45,12.50
Steel,Mild,0.25,PowderCoating-Black,20.15,60,18.75
...
```

#### **2. Pricing Formula Analysis**

`final_pricing_analysis.py` uses machine learning to analyze pricing data and derive calculation formulas.

**Usage:**
```bash
cd scripts/analyze

# Basic analysis
uv run python final_pricing_analysis.py

# Specify data file
uv run python final_pricing_analysis.py --data-file pricing_data.csv
```

**Features:**
1. **Load Data**: Read `pricing_data.csv`
2. **Feature Engineering**:
   - Create combined features (material area × thickness)
   - Group by material-grade combinations
3. **Constrained Linear Regression**:
   - Fit regression model for each material combination
   - Force all coefficients to be positive (physical meaning)
4. **Parameter Extraction**:
   - Material base cost (material_base_cost)
   - Material rate (material_rate): $ / (sq in × in)
   - Cut rate (cut_rate): $ / cut
   - Finish base cost (finish_base_cost)
   - Finish surface rate (finish_surface_rate): $ / sq in
5. **Visualization Analysis**:
   - R² score heatmap
   - Predicted vs actual price scatter plot
   - Residual analysis plot
6. **Output Results**:
   - `material_parameters.json`: Material parameters
   - `finish_parameters.json`: Finish parameters
   - `pricing_analysis_report.txt`: Detailed analysis report
   - `*.png`: Visualization charts

**Pricing Formula:**

```python
# Material cost
material_cost = material_base_cost + (mat_use_sqin × thickness × material_rate) + (num_cuts × cut_rate)

# Finish cost
finish_cost = finish_base_cost + (mat_use_sqin × finish_surface_rate)

# Total price
total_price = material_cost + finish_cost
```

**Output Example:**

`material_parameters.json`:
```json
{
  "Aluminum_6061-T6": {
    "base_cost": 5.00,
    "material_rate": 0.15,
    "cut_rate": 0.05,
    "r2_score": 0.98
  },
  "Steel_Mild": {
    "base_cost": 8.00,
    "material_rate": 0.20,
    "cut_rate": 0.08,
    "r2_score": 0.96
  }
}
```

`finish_parameters.json`:
```json
{
  "Anodized-Clear": {
    "base_cost": 10.00,
    "surface_rate": 0.50,
    "r2_score": 0.95
  },
  "PowderCoating-Black": {
    "base_cost": 15.00,
    "surface_rate": 0.75,
    "r2_score": 0.94
  }
}
```

### **Complete Workflow**

```bash
# Step 1: Extract data
cd scripts/extractor
uv run python permute_all_materials.py --quote-id qte_YOUR_QUOTE_ID

# Step 2: Extract pricing data to CSV
cd ../analyze
uv run python extract_pricing_data.py

# Step 3: Analyze pricing formula
uv run python final_pricing_analysis.py

# Step 4: View results
cat material_parameters.json
cat finish_parameters.json
cat pricing_analysis_report.txt
```

### **Data Directory Structure**

```
data/
├── *.json                      # Fabworks API raw data
├── pricing_data.csv            # Extracted pricing data
├── material_parameters.json    # Material parameters
├── finish_parameters.json      # Finish parameters
├── pricing_analysis_report.txt # Analysis report
└── *.png                       # Visualization charts
```

## 🎯 **Core Features**

- ✅ **STEP File Parsing**: CADQuery-based STEP file analysis
- ✅ **Automated Quote Generation**: Intelligent manufacturing quote system
- ✅ **Shopify Integration**: Complete e-commerce integration (products, orders, checkout)
- ✅ **Azure Blob Storage**: STEP file cloud storage
- ✅ **PostgreSQL Database**: Quote and part data management
- ✅ **Responsive UI**: Modern React interface
- ✅ **Health Monitoring**: Built-in health check endpoints
- ✅ **Auto Restart**: Automatic recovery on failure
- ✅ **Data Extraction Tools**: Fabworks API data extraction
- ✅ **Pricing Analysis**: Machine learning pricing formula derivation

## 🛠️ **Tech Stack**

### **Backend**
- **Framework**: FastAPI
- **CAD Parsing**: CADQuery 2.4.0
- **Database**: PostgreSQL + SQLAlchemy
- **Storage**: Azure Blob Storage
- **E-commerce**: Shopify API
- **Deployment**: Railway (Railpack)

### **Frontend**
- **Framework**: React 18 + TypeScript
- **Routing**: React Router v6
- **HTTP**: Axios
- **Styling**: Tailwind CSS
- **Build**: React Scripts
- **Serve**: Serve

### **Tools**
- **Package Management**: UV (Python), NPM (Node.js)
- **API Client**: Fabworks tRPC
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib, Seaborn

## 📖 **API Documentation**

### **Health Check**
```bash
GET /api/health
```
Returns backend status and version information.

### **Create Quote**
```bash
POST /api/createQuote
Content-Type: multipart/form-data

file: [STEP file]
```
Upload STEP file and generate quote.

### **Get Quote**
```bash
GET /api/quotes/{quote_id}
```
Get detailed information for specified quote.

### **Checkout**
```bash
POST /api/checkout/{quote_id}
```
Create Shopify checkout link for quote.

## 🔍 **Troubleshooting**

### **CADQuery Import Error**
```bash
# Ensure NumPy version < 2.0
cd backend
uv pip install "numpy<2.0.0"
```

### **Database Connection Failed**
- Check `DATABASE_URL` environment variable
- Ensure PostgreSQL service is running
- Check firewall rules

### **Azure Blob Storage Error**
- Verify `AZURE_STORAGE_CONNECTION_STRING`
- Ensure container is created
- Check access permissions

### **Shopify API Error**
- Verify API credentials
- Check Shopify store status
- Review API rate limit logs

## 📝 **Development Tips**

1. **Local Development**: Use Railway database to avoid local PostgreSQL configuration
2. **Environment Variables**: Use `.env` file to manage sensitive information
3. **Hot Reload**: Backend uses `--reload`, frontend auto hot-reloads
4. **Log Viewing**: Use `railway logs` to monitor production environment
5. **Data Analysis**: Regularly run analysis scripts to update pricing parameters

## 🤝 **Contributing**

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 **License**

This is a private project.

## 📧 **Contact**

For questions, please contact the project maintainer.

---

**Last Updated**: 2025-01-24  
**Version**: 2.0.0  
**Builder**: Railpack (Railway)  
**Parser**: CADQuery 2.4.0  
**Development Environment**: WSL2