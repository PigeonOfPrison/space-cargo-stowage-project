import axios from 'axios';
const API_URL = 'http://localhost:8000';

export async function getWastage() {
    try {
        const response = await axios.get(`${API_URL}/api/waste/identify`);
        return response.data;
    } catch (error) {
        console.error('Error fetching waste items:', error);
        throw error;
    }
}

export async function handleWasteReturnPlan(undockingContainerId, undockingDate, maxVolume) {
    try {
        const response = await axios.post(`${API_URL}/api/waste/return-plan`, {
            undockingContainerId,
            undockingDate,
            maxVolume
        });
        
        return response.data;
    } catch (error) {
        console.error('Error creating waste return plan:', error);
        throw error;
    }
}

export async function completeWasteUndocking(undockingContainerId, wasteItems) {
    try {
        const response = await axios.post(`${API_URL}/api/waste/complete-undocking`, {
            undockingContainerId,
            wasteItems
        });
        
        return response.data;
    } catch (error) {
        console.error('Error completing waste undocking:', error);
        throw error;
    }
}