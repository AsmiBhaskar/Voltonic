# Voltonic Dashboard

Modern, real-time energy monitoring dashboard for the Voltonic Campus Energy Management System.

## Features

✨ **Real-time Monitoring**
- Live campus energy load tracking
- Building-wise energy consumption
- Auto-refresh every 5 seconds

💰 **Optimization Metrics**
- Total energy savings
- Cost savings in INR
- CO₂ emission reductions

🔮 **ML-Powered Predictions**
- Next hour load prediction
- Confidence intervals
- Real-time model insights

📊 **Advanced Analytics**
- Hourly consumption charts
- Daily energy summaries
- Historical trends visualization
- Interactive charts with Recharts

🗺️ **Campus Structure Browser**
- Interactive campus hierarchy
- Building and room details
- Live room status monitoring
- Visual energy representation

## Tech Stack

- **React 18** - Modern UI framework
- **Recharts** - Data visualization
- **Axios** - API communication
- **CSS3** - Custom styling with dark theme

## Prerequisites

- Node.js 16 or higher
- npm or yarn
- Voltonic backend API running on port 5000

## Installation

### 1. Navigate to dashboard directory

```bash
cd dashboard
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the backend API

In a separate terminal, from the project root:

```bash
python run.py
```

Make sure the backend is running on `http://127.0.0.1:5000`

### 4. Start the dashboard

```bash
npm start
```

The dashboard will open automatically at `http://localhost:3000`

## Usage

### Dashboard Tab (📊)
- View real-time campus energy load
- Monitor total rooms, occupied rooms, and optimized rooms
- Check average campus temperature
- See optimization savings metrics
- View next hour load prediction

### Buildings Tab (🏢)
- Compare energy consumption across all buildings
- Click any building to view detailed information
- Buildings sorted by highest consumption
- Real-time occupancy data

### Analytics Tab (📈)
- **Hourly Consumption**: View energy trends over 12h, 24h, or 48h
- **Daily Summary**: Analyze consumption patterns over 7, 14, or 30 days
- **Campus History**: Track load, temperature, occupancy, and optimization in real-time

### Campus Map Tab (🗺️)
- Browse campus hierarchy: Faculties → Buildings → Rooms
- Expand faculties to see buildings
- Expand buildings to see rooms
- Click any room for detailed information including:
  - Location (Faculty, Building, Floor)
  - Latest energy readings
  - Occupancy and optimization status

## API Integration

The dashboard automatically connects to the backend API at `http://127.0.0.1:5000/api`.

All API endpoints are configured in `src/api.js`:

- `/dashboard/live` - Complete dashboard data
- `/live/campus` - Campus energy consumption
- `/live/buildings` - All buildings data
- `/analytics/hourly` - Hourly consumption
- `/analytics/daily` - Daily summary
- `/optimization/savings` - Savings metrics
- `/prediction/next-hour` - ML prediction
- `/campus/structure` - Campus hierarchy
- `/health` - API health check

## Auto-Refresh

All data automatically refreshes every **5 seconds** to provide real-time monitoring.

You can modify the refresh interval in each component's `useEffect` hook.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

To serve the production build:

```bash
npm install -g serve
serve -s build -p 3000
```

## Customization

### Changing Auto-Refresh Interval

Edit the interval value in component files:

```javascript
// Change from 5000ms (5 seconds) to your desired interval
const interval = setInterval(fetchData, 5000);
```

### Customizing Theme Colors

Edit `src/App.css` to modify colors:

```css
/* Primary color */
.app-header h1 {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

/* Background colors */
body {
  background: #0f172a;
}

.card {
  background: #1e293b;
}
```

### Adding New API Endpoints

1. Add the endpoint to `src/api.js`:

```javascript
export const dashboardAPI = {
  // ... existing endpoints
  myNewEndpoint: () => api.get('/my/new/endpoint'),
};
```

2. Use it in your component:

```javascript
import { dashboardAPI } from '../api';

const response = await dashboardAPI.myNewEndpoint();
```

## Troubleshooting

### CORS Issues

If you see CORS errors, ensure the backend has CORS enabled. The backend should include:

```python
from flask_cors import CORS
CORS(app)
```

### API Connection Failed

1. Verify the backend is running: `curl http://127.0.0.1:5000/api/health`
2. Check the proxy setting in `package.json` matches your backend URL
3. Look for errors in browser console (F12)

### Data Not Updating

1. Check browser console for API errors
2. Verify the backend has data by accessing API directly
3. Refresh the page (Cmd/Ctrl + R)

### Build Errors

If you encounter build errors:

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
npm install
```

## Performance

- Dashboard is optimized for real-time updates
- Charts are responsive and performant
- Auto-refresh intervals are configurable
- Production build is minified and optimized

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Part of the Voltonic Campus Energy Management System

## Support

For issues or questions about the dashboard, please check:
- API_DOCUMENTATION.md for backend API details
- Browser console for error messages
- Backend logs for API issues
