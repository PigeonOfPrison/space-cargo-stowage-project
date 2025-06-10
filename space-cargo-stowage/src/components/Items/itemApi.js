import axios from 'axios';

const API_URL = 'http://localhost:8000';

export async function fetchItems(params = {}, { onSuccess, onError } = {}) {
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

export async function handleItemUpload(file) {
    try {
        const formData = new FormData();
        formData.append('csvFile', file); // Change 'file' to 'csvFile' to match backend expectation

        const response = await axios.post(
            `${API_URL}/api/import/items`,
            formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    } catch (error) {
        
        console.error('Error uploading item file:', error);
        throw error;
    }
}

export async function placeItems(items) {
    try {
        const response = await axios.post(`${API_URL}/api/placement`, {
            items
        });
        
        return response.data;
    } catch (error) {
        console.error('Error placing items automatically:', error);
        throw error;
    }
}

export async function placeItemManually(itemId, containerId, coordinates) {
    try {
        const response = await axios.post(`${API_URL}/api/place`, {
            itemId,
            containerId,
            coordinates
        });
        
        return response.data;
    } catch (error) {
        console.error('Error placing item manually:', error);
        throw error;
    }
}