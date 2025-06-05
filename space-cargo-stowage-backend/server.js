// Server entry point - Express server initialization and port configuration
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { itemsPlacement, searchItems, retrieveItems, manualItemPlacement } from './src/controllers/itemsController.js';
import { identifyWaste, wasteReturnPlan, wasteCompleteUndocking } from './src/controllers/wasteController.js';
import { simulateDay } from './src/controllers/simulationController.js';
import { importItems, importContainers, exportArrangements } from './src/controllers/importExportController.js';
import { getSystemLogs } from './src/controllers/systemlogsController.js';
import { initDatabase } from './src/config/db.config.js';


const app = express();
const PORT = process.env.PORT || 8000;

initDatabase()
  .then(() => console.log('Database initialized successfully'))
  .catch(err => console.error('Error initializing database:', err));


// Middleware
app.use(cors());
app.use(express.json());

// Items routes
app.post('/api/placement', itemsPlacement);
app.get('/api/search', searchItems);
app.post('/api/retrieve', retrieveItems);
app.post('/api/place', manualItemPlacement);

app.get('/api/waste/identify', identifyWaste);
app.post('/api/waste/return-plan', wasteReturnPlan);
app.post('/api/waste/complete-undocking', wasteCompleteUndocking);

app.post('/api/simulate/day', simulateDay);

app.post('/api/import/items', importItems);
app.post('/api/import/containers', importContainers);

app.get('/api/export/arrangements', exportArrangements);

app.get('/api/logs', getSystemLogs);


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});