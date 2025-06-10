import axios from 'axios';
const API_URL = 'http://localhost:8000';

import { getSearchResult } from '../Search/searchApi';

export async function getItemsForSimulation(params = {}) {
    try {
        // Reuse the existing function with appropriate callbacks
        const items = await getSearchResult(params, {
            onSuccess: (data) => console.log('Items loaded for simulation:', data),
            onError: (error) => console.error('Failed to load items for simulation:', error)
        });
        
        return items;
    } 
    catch (error) {
        console.error('Simulation data loading failed:', error);
        throw error;
    }
}

export async function getSimulationResults(requestBody) {
    try {
        const response = await axios.post(`${API_URL}/api/simulate/day`, requestBody);
        
        if (response.status === 200) {
            return response.data;
        } else {
            throw new Error('Failed to fetch simulation results');
        }
    } catch(error) {
        console.error('Error fetching simulation results:', error);
        throw error;
    }
}