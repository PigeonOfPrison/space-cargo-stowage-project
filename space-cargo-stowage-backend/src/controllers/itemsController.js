// Items controller - Handles business logic for item operations

import ItemsModel from '../models/ItemsModel.js';
import ContainersModel from '../models/ContainersModel.js';
import OptimizationServices from '../services/optimizationService.js';
import { getRetrievalSteps } from '../services/retrievalService.js';

export async function itemsPlacement(req, res) {
    try {
        // Extract the request body
        const { items, containers } = req.body;

        // Validate input
        if (!items || !containers) {
            return res.status(400).json({ error: 'Items and containers are required.' });
        }

        // Save the items and containers to the database
        try {
            await ContainersModel.addContainers(containers);
            console.log('Containers saved to database successfully');

            await ItemsModel.addItems(items);
            console.log('Data saved to database successfully');
        } 
        catch (dbError) {
            console.error('Database error:', dbError);
            return res.status(500).json({ error: 'Failed to save data to database' });
        }
        
        // Return the placement result
        const placementResult = await OptimizationServices.optimizePlacement(items, containers);
        if (!placementResult) {
            return res.status(500).json({ error: 'Failed to optimize placement.' });
        }

        await ItemsModel.assignContainers(placementResult.placements);
        console.log('Successfully assigned optimal containers to items');
        return res.status(200).json(placementResult);
    } 
    catch (error) {
        console.error('Error in itemsPlacement:', error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
}

export async function searchItems(req, res) {
    try {
        const { itemId, itemName, userId } = req.query;

        if (!itemId && !itemName) {
            return res.status(400).json({ success: false });
        }

        const items = await ItemsModel.searchItems(itemId, itemName, userId);
        const retrievalSteps = await getRetrievalSteps(itemId);

        if (items.length === 0) {
            return res.status(404).json({ success: true, found : false, item: [], retrievalSteps: [] });
        }

        return res.status(200).json({
            success: true,
            found: true,
            item: items,
            retrievalSteps: retrievalSteps
        });
    } 
    catch (error) {
        console.error('Error in searchItems:', error);
        return res.status(500).json({ success: false });
    }
}

export async function retrieveItems(req, res) {
    try {
        const { itemId, userId, timestamp} = req.query;
        const item = await ItemsModel.retrieveItem(itemId, userId, timestamp);
        if (!item || item.length === 0) {
            return res.status(404).json({ success: false });
        }
        
        return res.status(200).json({ success : true });
    } catch (error) {
        console.error('Error in retrieveItems:', error);
        return res.status(500).json({ success: false });
    }
}

export async function manualItemPlacement(req, res) {
    try {
        const { itemId, userId, timestamp, containerId, position } = req.body;

        // Validate request body
        if (!itemId || !containerId || !position || !position.startCoordinates || !position.endCoordinates) {
            return res.status(400).json({ 
                success: false,
                message: 'Missing required fields'
            });
        }

        // Check if space is available
        const isSpaceAvailable = await ItemsModel.checkSpaceAvailability(
            containerId,
            position.startCoordinates,
            position.endCoordinates
        );

        if (!isSpaceAvailable) {
            return res.status(400).json({
                success: false,
                message: 'Space not available in container'
            });
        }

        // Place the item
        await ItemsModel.placeItem(itemId, containerId, position, userId, timestamp);
        
        return res.status(200).json({ 
            success: true
        });
    } catch (error) {
        console.error('Error in manualItemPlacement:', error);
        return res.status(500).json({ 
            success: false, 
            message: 'Internal server error' 
        });
    }
}

export default { itemsPlacement, searchItems, retrieveItems, manualItemPlacement };