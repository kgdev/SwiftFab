# SwiftFab React Frontend

A modern quote system built with React and TypeScript that provides a FabWorks-inspired interface for manufacturing quotes.

## Features

- **File Upload**: Drag & drop STEP file upload with validation
- **Quote Management**: View and edit quotes with material configuration
- **Shopify Integration**: Seamless checkout flow using Shopify Storefront API
- **Responsive Design**: Mobile-first design matching FabWorks aesthetic
- **Real-time Updates**: Live quote updates with backend integration

## Design Inspiration

This frontend is inspired by the [FabWorks quote interface](https://www.fabworks.com/quotes/qte_33ESlACsku2y4SbM7zfv7ybgu3d), featuring:

- Clean, professional layout
- Intuitive file upload interface
- Clear quote summary and parts breakdown
- Streamlined checkout process

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- SwiftFab backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── App.tsx              # Main application component
├── App.css              # Global styles
├── index.tsx            # Application entry point
└── index.css            # Base styles
```

## API Integration

The frontend integrates with the SwiftFab backend API:

- **POST** `/api/createQuote` - Upload STEP files and create quotes
- **GET** `/api/quoteDetails/{id}` - Fetch quote details
- **PUT** `/api/updateParts/{id}` - Update material configuration
- **POST** `/api/checkout/{id}` - Create Shopify checkout

## Key Features

### File Upload
- Drag and drop STEP/STP files
- File validation (up to 25MB)
- Real-time upload progress
- Automatic quote creation

### Quote Management
- Material configuration (type, grade, thickness, finish)
- Real-time price updates
- Parts breakdown with dimensions
- Quantity management

### Checkout Integration
- Shopify Storefront API integration
- Customer information collection
- Shipping address management
- Order processing

## Styling

The design system uses:

- **Colors**: Professional grays and blues with green accents
- **Typography**: System fonts for optimal performance
- **Layout**: CSS Grid and Flexbox for responsive design
- **Components**: Reusable button and form components

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Structure

The application is built as a single-page application with:

- **State Management**: React hooks for local state
- **API Integration**: Fetch API for backend communication
- **File Handling**: FormData for file uploads
- **Type Safety**: TypeScript for type checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

ISC License - see LICENSE file for details.