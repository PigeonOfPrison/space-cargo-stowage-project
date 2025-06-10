import axios from 'axios';
const API_URL = 'http://localhost:8000';

// Mock data for items (cleaned up - essential fields only)
export const mockItems = [
    { itemId: 'ITM001', name: 'Emergency Food Pack', usageLimit: 5, preferredZone: 'A', container: 'Container Alpha' },
    { itemId: 'ITM002', name: 'Medical Supplies Kit', usageLimit: 10, preferredZone: 'B', container: 'Container Beta' },
    { itemId: 'ITM003', name: 'Water Filtration System', usageLimit: 100, preferredZone: 'A', container: 'Container Gamma' },
    { itemId: 'ITM004', name: 'Solar Panel Array', usageLimit: 50, preferredZone: 'C', container: 'Container Delta' },
    { itemId: 'ITM005', name: 'Oxygen Generator', usageLimit: 75, preferredZone: 'A', container: 'Container Alpha' },
    { itemId: 'ITM006', name: 'Communication Device', usageLimit: 200, preferredZone: 'B', container: 'Container Epsilon' },
    { itemId: 'ITM007', name: 'Battery Pack', usageLimit: 30, preferredZone: 'D', container: 'Container Zeta' },
    { itemId: 'ITM008', name: 'Spare Parts Kit', usageLimit: 15, preferredZone: 'B', container: 'Container Beta' },
    { itemId: 'ITM009', name: 'Navigation System', usageLimit: 1000, preferredZone: 'C', container: 'Container Eta' },
    { itemId: 'ITM010', name: 'Air Filter Set', usageLimit: 25, preferredZone: 'A', container: 'Container Gamma' },
    { itemId: 'ITM011', name: 'Tool Kit', usageLimit: 150, preferredZone: 'D', container: 'Container Theta' },
    { itemId: 'ITM012', name: 'First Aid Kit', usageLimit: 20, preferredZone: 'C', container: 'Container Delta' },
    { itemId: 'ITM013', name: 'Emergency Beacon', usageLimit: 500, preferredZone: 'B', container: 'Container Iota' },
    { itemId: 'ITM014', name: 'Thermal Blanket', usageLimit: 40, preferredZone: 'B', container: 'Container Epsilon' },
    { itemId: 'ITM015', name: 'Radiation Shield', usageLimit: 1000, preferredZone: 'A', container: 'Container Kappa' },
    { itemId: 'ITM016', name: 'Space Suit', usageLimit: 100, preferredZone: 'D', container: 'Container Zeta' },
    { itemId: 'ITM017', name: 'Water Recycler', usageLimit: 300, preferredZone: 'C', container: 'Container Lambda' },
    { itemId: 'ITM018', name: 'Power Converter', usageLimit: 250, preferredZone: 'C', container: 'Container Eta' },
    { itemId: 'ITM019', name: 'Fuel Cell', usageLimit: 50, preferredZone: 'D', container: 'Container Mu' },
    { itemId: 'ITM020', name: 'Life Support Module', usageLimit: 500, preferredZone: 'D', container: 'Container Theta' }
];

// Mock retrieval steps data - matching backend format
export const mockRetrievalSteps = [
    { step: 1, action: 'remove', itemId: 'ITM999', itemName: 'Blocking Item A' },
    { step: 2, action: 'setAside', itemId: 'ITM998', itemName: 'Blocking Item B' },
    { step: 3, action: 'remove', itemId: 'ITM997', itemName: 'Blocking Item C' },
    { step: 4, action: 'retrieve', itemId: '{itemId}', itemName: '{itemName}' },
    { step: 5, action: 'placeBack', itemId: 'ITM997', itemName: 'Blocking Item C' },
    { step: 6, action: 'placeBack', itemId: 'ITM998', itemName: 'Blocking Item B' },
    { step: 7, action: 'placeBack', itemId: 'ITM999', itemName: 'Blocking Item A' }
];

// Utility function to format coordinates for display
export function formatCoordinates(coords) {
    return `(${coords.x}, ${coords.y}, ${coords.z})`;
}

// Format mock retrieval steps with actual item data
export function formatMockSteps(steps, selectedItem) {
    const itemId = selectedItem.itemId || selectedItem.id;
    return steps.map(step => ({
        ...step,
        itemId: step.itemId === '{itemId}' ? itemId : step.itemId,
        itemName: step.itemName === '{itemName}' ? selectedItem.name : step.itemName
    }));
}

// Helper function to try API search
async function tryApiSearch(query) {
    // Try to fetch from API first - search by item name
    let apiResults = await getSearchResult({
        itemName: query,
        limit: 20
    });
    
    // If no results with itemName, try searching by itemId
    if (!apiResults || apiResults.length === 0) {
        apiResults = await getSearchResult({
            itemId: query,
            limit: 20
        });
    }
    
    return apiResults;
}

// Helper function to filter mock data
function filterMockData(query) {
    return mockItems.filter(item =>
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.itemId.toLowerCase().includes(query.toLowerCase()) ||
        item.container.toLowerCase().includes(query.toLowerCase()) ||
        item.preferredZone.toLowerCase().includes(query.toLowerCase()) ||
        item.usageLimit.toString().includes(query)
    );
}

// Helper function to handle search feedback
function handleSearchFeedback(results, query, callbacks) {
    const { onInfo } = callbacks;
    if (!onInfo) return;
    
    let message;
    if (results.length === 0) {
        message = `No items found for "${query}" in offline data`;
    } else {
        message = `Found ${results.length} item${results.length > 1 ? 's' : ''} in offline data`;
    }
    onInfo(message);
}

// Perform search with API fallback to mock data
export async function searchItems(query, callbacks = {}) {
    const { onSuccess, onError } = callbacks;
    
    if (query.trim() === '') {
        return [];
    }

    try {
        const apiResults = await tryApiSearch(query);
        
        if (apiResults && apiResults.length > 0) {
            if (onSuccess) {
                onSuccess(`Found ${apiResults.length} item${apiResults.length > 1 ? 's' : ''} from server`);
            }
            return apiResults;
        }
    } 
    catch (error) {
        console.error('API search failed, falling back to mock data:', error);
        if (onError) {
            onError('Server search failed, using offline data');
        }
    }

    // Fallback to mock data filtering
    const results = filterMockData(query);
    handleSearchFeedback(results, query, callbacks);
    return results;
}

// Handle item retrieval with API call and fallback
export async function retrieveItemSteps(selectedItem, callbacks = {}) {
    const { onSuccess, onError, onInfo } = callbacks;
    
    if (!selectedItem) return [];

    try {
        const itemId = selectedItem.itemId || selectedItem.id;
        const apiSteps = await getRetrievalSteps(itemId);
        
        if (apiSteps && apiSteps.length > 0) {
            if (onSuccess) {
                onSuccess(`Retrieved ${selectedItem.name} - API steps loaded`);
            }
            return apiSteps;
        } 
        
        // Fallback to mock steps
        const steps = formatMockSteps(mockRetrievalSteps, selectedItem);
        if (onInfo) {
            onInfo(`Using mock retrieval steps for ${selectedItem.name}`);
        }
        return steps;
        
    } catch (error) {
        console.error('Error getting retrieval steps:', error);
        if (onError) {
            onError('Failed to get retrieval steps from API');
        }
        
        return formatMockSteps(mockRetrievalSteps, selectedItem);
    }
}

export async function getSearchResult(params = {}, { onSuccess, onError } = {}) {
    try {
        const response = await axios.get(`${API_URL}/api/item/get-some`, {
            params
        });
        
        if (onSuccess) {
            onSuccess(response.data);
        }
        
        return response.data.items;
    } 
    catch (error) {
        console.error('Error fetching items:', error);
        
        if (onError) {
            onError("hmmm", error);
        }
        
        throw error;
    }
}

export async function getRetrievalSteps(itemId) {
    try {
        // Use the /api/search endpoint to get retrieval steps for a specific item
        const searchParams = { itemId: itemId };
        const response = await axios.get(`${API_URL}/api/search`, {
            params: searchParams
        });
        
        if (response.data?.found && response.data?.retrievalSteps) {
            // Call the retrieve endpoint to decrement usage limit
            await callRetrieveEndpoint(itemId);
            
            return response.data.retrievalSteps;
        }
        
        return [];
    } catch (error) {
        console.error('Error getting retrieval steps:', error);
        throw error;
    }
}

// Helper function to call the retrieve endpoint for usage limit decrement
async function callRetrieveEndpoint(itemId) {
    try {
        // Generate a random user ID for demonstration
        const userId = `user_${Math.floor(Math.random() * 1000)}`;
        
        const requestBody = {
            itemId: itemId,
            userId: userId,
            timestamp: new Date().toISOString()
        };

        await axios.post(`${API_URL}/api/retrieve`, requestBody);
    } catch (error) {
        console.error('Error calling retrieve endpoint:', error);
        // Don't throw error here as this is just for usage limit decrement
        // The main functionality (getting retrieval steps) should still work
    }
}