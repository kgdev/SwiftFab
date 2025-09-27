# SwiftFab Quote System

A full-stack web application for parsing STEP files and generating manufacturing quotes with material configuration and Shopify checkout integration.

## Features

- **STEP File Upload**: Upload and parse STEP/STP files to extract geometric data
- **Material Configuration**: Configure material type, grade, thickness, and finish options
- **Real-time Pricing**: Calculate quotes with live price updates and animations
- **Quote Management**: View and manage multiple quotes with session-based authentication
- **Shopify Integration**: Seamless checkout flow using Shopify's Admin API
- **File Download**: Download original uploaded files
- **Responsive UI**: Modern, mobile-friendly interface built with React and Tailwind CSS

## Tech Stack

### Backend
- **FastAPI**: Python web framework for building APIs
- **SQLAlchemy**: Database ORM with SQLite
- **Shopify Python API**: Integration with Shopify's Admin API
- **File Storage**: Permanent file storage for uploaded STEP files

### Frontend
- **React 19**: Modern React with TypeScript
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Components**: Modular, reusable UI components

### Deployment
- **Vercel**: Platform for deploying both frontend and backend
- **GitHub**: Source code repository

## Project Structure

```
SwiftFab/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── shopify_integration.py # Shopify API integration
│   ├── config.py            # Configuration management
│   ├── config.json          # Configuration file (not tracked)
│   ├── config.example.json  # Configuration template
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/             # Uploaded STEP files
│   └── quotes.db            # SQLite database
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   │   ├── Home.tsx     # Main upload page
│   │   │   ├── Quote.tsx    # Quote details page
│   │   │   └── NotFound.tsx # 404 page
│   │   ├── components/      # React components
│   │   │   ├── ui/          # Reusable UI components
│   │   │   └── quote/       # Quote-specific components
│   │   ├── config/          # API configuration
│   │   ├── types/           # TypeScript type definitions
│   │   └── hooks/           # Custom React hooks
│   ├── package.json         # Node.js dependencies
│   └── vercel.json          # Vercel configuration
├── vercel.json              # Root Vercel configuration
└── README.md               # This file
```

## API Endpoints

### Quote Management
- **POST** `/api/createQuote` - Upload STEP file and create quote
- **GET** `/api/quoteDetails/{id}` - Get quote details with parts
- **GET** `/api/quotes` - List all quotes (session-based)
- **PUT** `/api/updatePart/{id}` - Update part configuration

### File Management
- **GET** `/api/downloadFile/{id}` - Download original STEP file
- **GET** `/api/materials` - Get available materials and finishes

### Checkout
- **POST** `/api/checkout/{id}` - Create Shopify checkout session

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp config.example.json config.json
# Edit config.json with your settings
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Configuration

#### Backend Configuration
Create `backend/config.json` from `config.example.json`:

```json
{
  "shopify": {
    "shop_domain": "your-shop.myshopify.com",
    "access_token": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "api_version": "2024-01"
  },
  "app": {
    "debug": false,
    "host": "0.0.0.0",
    "port": 8000
  },
  "security": {
    "admin_key": "your-admin-key-here"
  }
}
```

#### Frontend Configuration
Create `frontend/.env`:

```bash
REACT_APP_API_BASE_URL=http://localhost:8000
```

## Shopify Integration

### Setup
1. Create a Shopify private app
2. Get Admin API access token
3. Configure required scopes:
   - `read_products`, `write_products`
   - `read_orders`, `write_orders`
   - `read_customers`, `write_customers`
   - `read_inventory`, `write_inventory`

### Features
- Automatic product creation for each quote
- Individual products for each part
- Cart-based checkout flow
- File download links in product descriptions

## Usage

1. **Upload STEP File**: Drag & drop or select a STEP/STP file
2. **Configure Materials**: Set material type, grade, thickness, and finish
3. **View Quote**: See real-time price updates and part details
4. **Download File**: Access original uploaded files
5. **Checkout**: Proceed to Shopify checkout for order processing

## Key Features

### File Upload
- Supports .step and .stp files up to 25MB
- Drag & drop interface with validation
- Automatic quote creation

### Quote Management
- Real-time material configuration
- Live price updates with animations
- Parts breakdown with dimensions
- Quantity management

### UI Components
- Modular component architecture
- Reusable UI components (Button, Card, FileUpload, etc.)
- Responsive design with Tailwind CSS
- Loading states and error handling

## Deployment

### Vercel Deployment
1. Connect GitHub repository to Vercel
2. Set environment variables:
   - `REACT_APP_API_BASE_URL` - Your backend API URL
   - `SHOPIFY_SHOP_DOMAIN` - Your Shopify domain
   - `SHOPIFY_ACCESS_TOKEN` - Your Shopify access token
   - `SECURITY_ADMIN_KEY` - Admin key for file downloads

### Environment Variables
- **Backend**: Configure via `config.json` or environment variables
- **Frontend**: Set `REACT_APP_API_BASE_URL` for API endpoint

## Architecture

### Frontend Architecture
- **Component-based**: Modular React components
- **Type-safe**: Full TypeScript implementation
- **State Management**: React hooks for local state
- **API Integration**: Centralized API configuration

### Backend Architecture
- **RESTful API**: FastAPI with automatic documentation
- **Database**: SQLAlchemy ORM with SQLite
- **File Storage**: Permanent file storage system
- **Session Management**: Session-based authentication

## Security

- Session-based authentication for quote access
- Admin key for file downloads
- Environment variable configuration
- No sensitive data in version control

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Scripts and Data Analysis

The `scripts/` directory contains powerful tools for data extraction, analysis, and pricing calculation. These scripts were developed to reverse-engineer FabWorks' pricing algorithms and create our own pricing calculator.

### Directory Structure

```
scripts/
├── extractor/           # Data extraction from FabWorks
│   ├── fabworks_api_client.py    # tRPC API client for FabWorks
│   └── permute_all_materials.py  # Material combination permutation
├── parser/              # STEP file parsing algorithms
│   └── simple_step_parser.py     # FreeCAD-based STEP parser
└── analyze/             # Pricing analysis and calculation
    ├── extract_pricing_data.py   # Data extraction from JSON files
    ├── final_price_calculator.py # Pricing calculator implementation
    └── final_pricing_analysis.py # Statistical analysis and modeling
```

### FabWorks Data Extraction

#### **tRPC API Client (`extractor/fabworks_api_client.py`)**

A sophisticated client for interacting with FabWorks' internal tRPC API:

**Key Features:**
- **Authentication**: Uses browser cookies for session management
- **Batch Operations**: Efficient batch updates for multiple parts
- **Sequential Processing**: Handles rate limiting and API constraints
- **Error Handling**: Robust error handling and retry logic

**Core Methods:**
```python
# Batch update multiple parts efficiently
client.update_parts_batch(part_updates)

# Update all parts in a quote with same parameters
client.update_all_parts_in_quote(quote_id, updates)

# Get detailed quote information
client.get_quote_details(quote_id)
```

**API Integration:**
- **Base URL**: `https://www.fabworks.com/api/trpc`
- **Authentication**: Cookie-based session management
- **Rate Limiting**: Built-in delays and batch processing
- **Proxy Support**: Configurable proxy settings for enterprise networks

#### **Material Permutation Engine (`extractor/permute_all_materials.py`)**

Systematically tests all possible material and finish combinations:

**Algorithm:**
1. **Load Materials**: Extract all material types, grades, and thicknesses
2. **Load Finishes**: Extract all available finish options
3. **Generate Combinations**: Create Cartesian product of all combinations
4. **Batch Processing**: Update quotes with each combination
5. **Data Collection**: Save results for each permutation

**Key Features:**
- **Comprehensive Coverage**: Tests all material-grade-thickness-finish combinations
- **Progress Tracking**: Real-time progress indicators and logging
- **Error Recovery**: Continues processing even if individual combinations fail
- **Data Organization**: Structured output with timestamps and metadata

**Usage:**
```bash
python permute_all_materials.py --quote-id qte_123456789
python permute_all_materials.py -q qte_123456789 --output-prefix "test_run"
```

### STEP File Parsing Algorithms

#### **FreeCAD-Based Parser (`parser/simple_step_parser.py`)**

Advanced geometric analysis using FreeCAD's CAD engine:

**Core Algorithms:**

1. **Geometric Analysis:**
   - **Volume Calculation**: `shape.Volume / (25.4**3)` (mm³ → in³)
   - **Surface Area**: `shape.Area / (25.4**2)` (mm² → in²)
   - **Bounding Box**: Length, width, height extraction

2. **Hole Detection Algorithm:**
   ```python
   def _detect_holes_freecad(self, shape):
       # Analyze each face to find inner wires (holes)
       for face in shape.Faces:
           wires = face.Wires
           if len(wires) > 1:
               # Identify outer boundary vs holes
               outer_wire = self._identify_outer_wire(wire_info)
               hole_wires = [w for w in wire_info if w['index'] != outer_wire]
   ```

3. **Wire Analysis:**
   - **Containment Detection**: Uses bounding box analysis to identify outer boundaries
   - **Shape Classification**: Circular, rectangular, slot, or irregular holes
   - **Perimeter Calculation**: Accurate cut length calculation from wire perimeters

4. **Hole Merging Algorithm:**
   ```python
   def _merge_opposite_holes(self, holes):
       # Merge front/back hole pairs into through holes
       # Uses position tolerance and diameter matching
       # Calculates average properties for merged holes
   ```

**Advanced Features:**
- **Multi-Face Analysis**: Handles complex parts with multiple faces
- **Wire Topology**: Analyzes wire relationships within faces
- **Shape Recognition**: Classifies holes by geometric properties
- **Cut Length Optimization**: Accurate perimeter calculation for pricing

### Pricing Analysis and Calculation

#### **Data Extraction (`analyze/extract_pricing_data.py`)**

Extracts structured pricing data from JSON files:

**Data Processing Pipeline:**
1. **File Discovery**: Recursively finds all JSON files in data directory
2. **Data Parsing**: Extracts combination info and quote details
3. **Part Mapping**: Creates part_id to part_data mapping
4. **Pricing Extraction**: Extracts pricing data for each part
5. **CSV Generation**: Creates structured CSV for analysis

**Output Format:**
```csv
part_id,material_type,material_grade,material_thickness,finish,
cut_len_in,num_cuts,mat_use_sqin,surf_area_sqin,price_per_part
```

#### **Statistical Analysis (`analyze/final_pricing_analysis.py`)**

Advanced statistical modeling of pricing algorithms:

**Pricing Formula:**
```
Total Price = Material Base + (Material Rate × Material Area×Thickness) + 
              (Cut Count Rate × Number of Cuts) + 
              Finish Base + (Surface Rate × Surface Area)
```

**Modeling Techniques:**

1. **Constrained Linear Regression:**
   ```python
   def constrained_linear_regression(self, X, y):
       # Ensures all rate coefficients are positive
       # Uses SLSQP optimization with inequality constraints
       # Fallback to simple linear regression if optimization fails
   ```

2. **Material-Grade Analysis:**
   - **Baseline**: Uses "No Deburring" finish as baseline
   - **Features**: Material area×thickness, number of cuts
   - **Parameters**: Base cost, material rate, cut count rate

3. **Finish Analysis:**
   - **Offset Method**: Calculates price difference from baseline
   - **Surface Metrics**: Different surface area calculations per finish type
   - **Parameters**: Finish base cost, surface rate

**Statistical Metrics:**
- **R² Score**: Model fit quality
- **RMSE**: Root mean square error
- **MAE**: Mean absolute error
- **MAPE**: Mean absolute percentage error

#### **Price Calculator (`analyze/final_price_calculator.py`)**

Production-ready pricing calculator:

**Core Algorithm:**
```python
def calculate_price(self, material_type, material_grade, finish, 
                   material_area, thickness, num_cuts, surface_area):
    # Material cost calculation
    material_cost = material_params['material_rate'] * material_area * thickness
    cut_count_cost = material_params['cut_count_rate'] * num_cuts
    
    # Surface cost based on finish type
    if finish == 'Deburred':
        surface_cost = finish_params['surface_rate'] * material_area
    else:
        surface_cost = finish_params['surface_rate'] * surface_area
    
    total_price = material_cost + cut_count_cost + surface_cost
```

**Key Features:**
- **Parameter Loading**: Auto-detects parameter files
- **Error Handling**: Graceful fallbacks for missing parameters
- **Accuracy Tracking**: Returns R² and MAPE for each calculation
- **Flexible Input**: Handles various material and finish combinations

### Algorithm Complexity

**Time Complexity:**
- **STEP Parsing**: O(n×m) where n = faces, m = wires per face
- **Hole Detection**: O(w²) where w = total wires (containment analysis)
- **Material Permutation**: O(m×f) where m = materials, f = finishes
- **Pricing Calculation**: O(1) - constant time lookup

**Space Complexity:**
- **Geometric Data**: O(p) where p = parts in quote
- **Pricing Parameters**: O(m×f) for material-finish combinations
- **Analysis Results**: O(c) where c = total combinations tested

### Data Flow

```
STEP File → FreeCAD Parser → Geometric Analysis → Quote Structure
     ↓
FabWorks API → Material Permutation → Price Collection → CSV Export
     ↓
Statistical Analysis → Parameter Extraction → Price Calculator
     ↓
Production Integration → Real-time Pricing
```

### Usage Examples

**Extract Data from FabWorks:**
```bash
cd scripts/extractor
python permute_all_materials.py --quote-id qte_123456789 --dry-run
```

**Analyze Pricing Data:**
```bash
cd scripts/analyze
python final_pricing_analysis.py
```

**Calculate Prices:**
```python
from final_price_calculator import FinalPriceCalculator
calculator = FinalPriceCalculator()
result = calculator.calculate_price(
    material_type="Aluminum",
    material_grade="5052-H32", 
    finish="Deburred",
    material_area=10.0,
    thickness=0.125,
    num_cuts=5,
    surface_area=20.0
)
```

## Support

For support and questions, please open an issue in the repository.

## Repository

GitHub: https://github.com/kgdev/SwiftFab