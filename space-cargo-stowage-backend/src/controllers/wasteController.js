import WasteModel from '../models/WasteModel.js';
import { getRetrievalSteps } from '../services/retrievalService.js';
import OptimizationService from '../services/optimizationService.js';

export async function identifyWaste(_, res) {  // Using _ to indicate unused parameter
    try {
        await WasteModel.addWasteItems();
        const wasteItems = await WasteModel.getWasteItems();
        
        return res.status(200).json({
            success: true,
            wasteItems: wasteItems
        });
    } catch (error) {
        console.error('Error in identifyWaste:', error);
        return res.status(500).json({
            success: false,
            wasteItems: [],
            message: 'Failed to identify waste items'
        });
    }
}   

    export async function wasteReturnPlan(req, res) {
        try {
            const { undockingContainerId, undockingDate, maxVolume } = req.body;

            // Validate request body
            if (!undockingContainerId || !undockingDate || !maxVolume) {
                return res.status(400).json({
                    success: false,
                    message: 'Missing required fields'
                });
            }            // Get waste items that can be loaded
            const selectedItems = await OptimizationService.getOptimalWaste(maxVolume);
            
            // Get total volume of selected items
            const totalVolume = await OptimizationService.calculateTotalVolume(selectedItems);

            // Assign the selected waste items to the undocking container
            const itemIds = selectedItems.map(item => item.item_id);
            await WasteModel.assignUndockingContainer(itemIds, undockingContainerId);

            // Generate return plan steps
            const returnPlan = selectedItems.map((item, index) => ({
                step: index + 1,
                itemId: item.item_id,
                itemName: item.item_name,
                fromContainer: item.from_container,
                toContainer: undockingContainerId
            }));

            // Generate retrieval steps
            const retrievalSteps = await getRetrievalSteps(selectedItems.map(item => item.item_id));


            // Prepare return manifest
            const returnManifest = {
                undockingContainerId,
                undockingDate,
                returnItems: selectedItems.map(item => ({
                    itemId: item.item_id,
                    name: item.item_name,
                    reason: item.reason
                })),
                totalVolume
            };

            return res.status(200).json({
                success: true,
                returnPlan,
                retrievalSteps,
                returnManifest
            });

        } catch (error) {
            console.error('Error in wasteReturnPlan:', error);
            return res.status(500).json({
                success: false,
                message: 'Failed to generate waste return plan'
            });
        }
    }
    
    export async function wasteCompleteUndocking(req, res) {
        try {
            const { undockingContainerId, timestamp } = req.body;

            // Validate request body
            if (!undockingContainerId || !timestamp) {
                return res.status(400).json({
                    success: false,
                    message: 'Missing required fields: undockingContainerId and timestamp'
                });
            }

            // Complete the undocking and get count of removed items
            const itemsRemoved = await WasteModel.completeUndocking(undockingContainerId, timestamp);

            return res.status(200).json({
                success: true,
                itemsRemoved: itemsRemoved
            });

        } catch (error) {
            console.error('Error in wasteCompleteUndocking:', error);
            return res.status(500).json({
                success: false,
                itemsRemoved: 0,
                message: 'Failed to complete undocking operation'
            });
        }
    }

export default { identifyWaste, wasteReturnPlan, wasteCompleteUndocking };


