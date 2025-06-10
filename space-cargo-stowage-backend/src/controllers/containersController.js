// Containers controller - Handles business logic for container operations
import ContainersModel from '../models/ContainersModel.js';

export async function getAllContainers(req, res) {
    try {
        const containers = await ContainersModel.getAllContainers();
        
        res.status(200).json({
            containers: containers.map(container => ({
                containerId: container.container_id,
                zone: container.zone,
                width: container.width,
                depth: container.depth,
                height: container.height
            }))
        });
    } catch (error) {
        console.error('Error fetching containers:', error);
        res.status(500).json({
            error: 'Failed to fetch containers',
            message: error.message
        });
    }
}