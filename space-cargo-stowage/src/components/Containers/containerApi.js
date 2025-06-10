import axios from 'axios';

const API_URL = 'http://localhost:8000';


export async function getAllContainers() {
    try {
        const response = await axios.get(`${API_URL}/api/container/get-all`);
        return response.data.containers;
    } catch (error) {
        console.error('Error fetching containers:', error);
        throw error;
    }
}

export async function handleContainerUpload(file) {
    try {
        const formData = new FormData();
        formData.append('csvFile', file);  // Changed from 'file' to 'csvFile' to match backend

        const response = await axios.post(
            `${API_URL}/api/import/containers`,
            formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    } catch (error) {
        console.error('Error uploading container file:', error);
        throw error;
    }
}



