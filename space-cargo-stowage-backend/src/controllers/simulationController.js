// Simulation controller - Handles simulation calculations and logic
import SimulationModel from '../models/simulationModel.js';

export async function simulateDay(req, res) {
    try {
        const { numOfDays, toTimestamp, itemsToBeUsedPerDay } = req.body;

        // Validate request body
        if ((!numOfDays && !toTimestamp) || (numOfDays && toTimestamp)) {
            return res.status(400).json({
                success: false,
                message: 'Provide either numOfDays or toTimestamp, not both'
            });
        }

        if (!itemsToBeUsedPerDay || !Array.isArray(itemsToBeUsedPerDay)) {
            return res.status(400).json({
                success: false,
                message: 'itemsToBeUsedPerDay must be an array'
            });
        }

        // Validate numOfDays if provided
        if (numOfDays && (numOfDays <= 0 || !Number.isInteger(numOfDays))) {
            return res.status(400).json({
                success: false,
                message: 'numOfDays must be a positive integer'
            });
        }

        // Determine the new date and calculate days to simulate
        let newDate;
        let daysToSimulate;
        
        if (numOfDays) {
            newDate = await SimulationModel.simulateTimeProgression(numOfDays);
            daysToSimulate = numOfDays;        } else {
            newDate = await SimulationModel.simulateToTimestamp(toTimestamp);
            // Calculate days between current date and target timestamp
            const currentDate = new Date();
            daysToSimulate = Math.ceil((newDate - currentDate) / (1000 * 60 * 60 * 24));
        }

        // Track changes
        const changes = {
            itemsUsed: [],
            itemsExpired: [],
            itemsDepletedToday: []
        };

        // Process item usage (multiply by number of days)
        for (const itemToUse of itemsToBeUsedPerDay) {
            try {
                const updatedItem = await SimulationModel.useItemMultipleDays(
                    itemToUse.itemId, 
                    itemToUse.name,
                    daysToSimulate
                );

                changes.itemsUsed.push({
                    itemId: updatedItem.item_id.toString(),
                    name: updatedItem.name,
                    remainingUses: updatedItem.usage_limit
                });

                // Check if item became depleted during simulation
                if (updatedItem.usage_limit <= 0) {
                    changes.itemsDepletedToday.push({
                        itemId: updatedItem.item_id.toString(),
                        name: updatedItem.name
                    });
                }
            } catch (error) {
                console.warn(`Failed to use item: ${error.message}`);
                // Continue with other items even if one fails
            }        
        }        
        
        // Get items that expired today
        const expiredItems = await SimulationModel.getExpiredItems(newDate);
        changes.itemsExpired = expiredItems.map(item => ({
            itemId: item.item_id.toString(),
            name: item.name
        }));

        return res.status(200).json({
            success: true,
            newDate: newDate.toISOString(),
            changes
        });

    } catch (error) {
        console.error('Error in simulateDay:', error);
        return res.status(500).json({
            success: false,
            message: 'Failed to simulate day progression'
        });
    }
}

export default { simulateDay };
