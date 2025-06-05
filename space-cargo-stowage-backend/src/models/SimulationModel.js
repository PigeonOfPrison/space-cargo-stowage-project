// filepath: c:\Users\Mohammad Hammad\web development projects\My own projects\space-cargo-stowage-backend\src\models\SimulationModel.js
import { pool } from '../config/db.config.js';

class SimulationModel {
    static async getExpiredItems(currentDate) {
        const client = await pool.connect();
        try {
            const query = `
                SELECT item_id, name, expiry_date
                FROM items
                WHERE expiry_date <= $1
                AND expiry_date > $1 - INTERVAL '1 day'
                ORDER BY expiry_date DESC
            `;
            
            const result = await client.query(query, [currentDate]);
            return result.rows;
        } 
        finally {
            client.release();
        }    
    }

    static async simulateTimeProgression(numDays) {
        // Calculate the new date without storing it
        const currentDate = new Date();
        const newDate = new Date(currentDate);
        newDate.setDate(newDate.getDate() + numDays);

        // Return the simulated new date without database changes
        return newDate;
    }

    static async simulateToTimestamp(targetTimestamp) {
        const targetDate = new Date(targetTimestamp);
        const currentDate = new Date();
        
        if (targetDate <= currentDate) {
            throw new Error('Target timestamp must be in the future');
        }

        // Return the target date without database changes
        return targetDate;
    }  
      
    static async useItemMultipleDays(itemId, itemName, numDays) {
        const client = await pool.connect();
        try {
            // Find item by ID or name, excluding depleted items
            let findQuery;
            let params;
            
            if (itemId) {
                findQuery = 'SELECT * FROM items WHERE item_id = $1 AND usage_limit > 0';
                params = [itemId];
            } else {
                findQuery = 'SELECT * FROM items WHERE name = $1 AND usage_limit > 0 LIMIT 1';
                params = [itemName];
            }

            const findResult = await client.query(findQuery, params);
            
            if (findResult.rows.length === 0) {
                throw new Error(`Item not found or already depleted: ${itemId || itemName}`);
            }

            const item = findResult.rows[0];

            // Calculate new usage limit after multiple days
            const newUsageLimit = Math.max(0, item.usage_limit - numDays);

            // Simulate usage by returning item with decremented usage_limit
            // No actual database update - just simulation
            const simulatedItem = {
                ...item,
                usage_limit: newUsageLimit
            };

            return simulatedItem;
        } finally {
            client.release();
        }
    }
}

export default SimulationModel;