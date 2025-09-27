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

## Support

For support and questions, please open an issue in the repository.

## Repository

GitHub: https://github.com/kgdev/SwiftFab