# SwiftFab Quote System

A full-stack web application for parsing STEP files and generating manufacturing quotes with material and finish options.

## Features

- **STEP File Upload**: Upload and parse STEP/STP files to extract geometric data
- **Material Configuration**: Configure material type, grade, thickness, and finish options
- **Real-time Pricing**: Calculate quotes based on material properties and dimensions
- **Quote Management**: View and manage multiple quotes
- **Responsive UI**: Modern, mobile-friendly interface built with Nuxt.js and Tailwind CSS

## Tech Stack

### Backend
- **FastAPI**: Python web framework for building APIs
- **uv**: Fast Python package manager and virtual environment tool
- **SQLAlchemy**: Database ORM
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL for production)
- **FreeCAD**: CAD library for STEP file parsing (with fallback mock parser)

### Frontend
- **Nuxt.js 3**: Vue.js framework with SSR capabilities
- **Tailwind CSS**: Utility-first CSS framework
- **Headless UI**: Accessible UI components
- **Heroicons**: Beautiful SVG icons

### Deployment
- **Vercel**: Platform for deploying both frontend and backend

## Project Structure

```
swiftfab-quote-system/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── step_parser.py       # STEP file parser
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── pages/
│   │   └── index.vue        # Main application page
│   ├── assets/
│   │   └── css/
│   │       └── main.css     # Global styles
│   ├── nuxt.config.ts       # Nuxt configuration
│   ├── package.json         # Node.js dependencies
│   └── vercel.json          # Vercel configuration
├── vercel.json              # Root Vercel configuration
├── package.json             # Root package.json for scripts
└── README.md               # This file
```

## API Endpoints

### 1. Create Quote
- **POST** `/api/createQuote`
- **Body**: Multipart form data with STEP file
- **Response**: Quote ID and basic information

### 2. Update Parts
- **PUT** `/api/updateParts/{quote_id}`
- **Body**: JSON with material configuration
- **Response**: Updated quote with new pricing

### 3. Get Quote Details
- **GET** `/api/quoteDetails/{quote_id}`
- **Response**: Complete quote information including parts and pricing

### 4. List Quotes
- **GET** `/api/quotes`
- **Response**: List of all quotes

## Development Setup

### Prerequisites
- Node.js 18+ 
- uv (fast Python package manager) - [Install here](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.8+ (or let uv install it: `uv python install`)
- npm or yarn

### Backend Setup
```bash
cd backend
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Full Development
```bash
# From root directory
npm install
npm run dev
```

## Deployment on Vercel

### 1. Environment Variables
Set the following environment variables in Vercel:
- `DATABASE_URL`: PostgreSQL connection string for production

### 2. Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### 3. Configuration
The `vercel.json` file configures:
- Backend API routes (`/api/*`) to Python FastAPI
- Frontend routes to Nuxt.js static build
- Build commands and output directories

## Usage

1. **Upload STEP File**: Select a STEP or STP file and click "Upload & Create Quote"
2. **Configure Materials**: Set material type, grade, thickness, and finish
3. **Update Quote**: Click "Update Quote" to recalculate pricing
4. **View Details**: See part dimensions, hole count, and pricing information
5. **Manage Quotes**: View all quotes and switch between them

## STEP File Support

The system supports:
- **File Formats**: .step, .stp
- **Geometric Analysis**: Volume, surface area, dimensions
- **Hole Detection**: Automatic detection of holes and cutouts
- **Material Calculation**: Cut length, material usage, bend data

## Pricing Calculation

Pricing is calculated based on:
- **Material Type**: Different multipliers for steel, aluminum, stainless steel
- **Finish Options**: Additional costs for powder coating, anodizing, etc.
- **Dimensions**: Volume, surface area, and cut length
- **Complexity**: Number of cuts, holes, and bends

## Limitations

- **FreeCAD Dependency**: Requires FreeCAD for full STEP parsing (fallback mock parser available)
- **File Size**: Limited to 10MB uploads
- **Material Database**: Limited material options (can be expanded)
- **Pricing**: Simplified pricing model (can be enhanced with real pricing APIs)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
