# API Configuration

## Environment Variables

The frontend application uses environment variables to configure the backend API URL.

### Setting the API Base URL

Create a `.env` file in the `frontend` directory with the following content:

```bash
# Development
REACT_APP_API_BASE_URL=http://localhost:8000

# Production example
# REACT_APP_API_BASE_URL=https://api.yourdomain.com
```

### Default Configuration

If no environment variable is set, the application will default to:
- `http://localhost:8000` (for development)

### Available Endpoints

The following API endpoints are configured:

- `CREATE_QUOTE` - Create a new quote
- `GET_QUOTES` - Get all quotes
- `GET_QUOTE_DETAILS(id)` - Get quote details by ID
- `UPDATE_PART(id)` - Update a part
- `GET_MATERIALS` - Get materials and finishes
- `DOWNLOAD_FILE(id)` - Download original file
- `CHECKOUT(id)` - Create checkout session

### Usage in Code

```typescript
import API_ENDPOINTS from '../config/api';

// Use the configured endpoints
const response = await fetch(API_ENDPOINTS.CREATE_QUOTE, {
  method: 'POST',
  body: formData,
});
```

### Production Deployment

For production deployment, set the environment variable to your production API URL:

```bash
REACT_APP_API_BASE_URL=https://your-production-api.com
```
