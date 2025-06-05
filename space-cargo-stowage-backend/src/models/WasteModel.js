import { pool } from '../config/db.config.js';

class WasteModel {
    static async addWasteItems() {
        const client = await pool.connect();
        try {
            await client.query('BEGIN');

            // Insert expired/used items into waste table
            const insertQuery = `
                INSERT INTO waste (item_id, item_name, reason, container_id)
                SELECT 
                    i.item_id,
                    i.name,
                    CASE 
                        WHEN i.expiry_date <= CURRENT_TIMESTAMP THEN 'Expired'
                        WHEN i.usage_limit <= 0 THEN 'Out of Uses'
                    END as reason,
                    i.container_id
                FROM items i
                WHERE i.expiry_date <= CURRENT_TIMESTAMP 
                OR i.usage_limit <= 0;
            `;


            await client.query(insertQuery);

            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }

    static async getWasteItems() {
        const client = await pool.connect();
        try {
            const query = `
                SELECT 
                    w.item_id,
                    w.item_name as name,
                    w.reason,
                    w.container_id,
                    p.xi as start_width,
                    p.yi as start_depth,
                    p.zi as start_height,
                    p.xj as end_width,
                    p.yj as end_depth,
                    p.zj as end_height
                FROM waste w
                LEFT JOIN placements p ON w.item_id = p.item_id
                ORDER BY w.created_at DESC;
            `;

            const result = await client.query(query);
            
            // Transform the results to match the required response format
            return result.rows.map(item => ({
                itemId: item.item_id,
                name: item.name,
                reason: item.reason,
                containerId: item.container_id,
                position: item.start_width ? {  // Only include position if coordinates exist
                    startCoordinates: {
                        width: item.start_width,
                        depth: item.start_depth,
                        height: item.start_height
                    },
                    endCoordinates: {
                        width: item.end_width,
                        depth: item.end_depth,
                        height: item.end_height
                    }
                } : null
            }));
        } finally {
            client.release();
        }
    }

    static async deleteWasteItem(itemId) {
        const client = await pool.connect();
        try {
            await client.query('BEGIN');

            // Delete from waste table
            const deleteWasteQuery = `
                DELETE FROM waste
                WHERE item_id = $1;
            `;
            await client.query(deleteWasteQuery, [itemId]);

            // Delete from placements table
            const deletePlacementQuery = `
                DELETE FROM placements
                WHERE item_id = $1;
            `;
            await client.query(deletePlacementQuery, [itemId]);

            // Log the deletion
            const logQuery = `
                INSERT INTO systemlogs (message)
                VALUES ($1)
            `;
            await client.query(logQuery, [
                `Waste item ${itemId} moved to undocking container and removed from system`
            ]);

            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }    
    
    static async completeUndocking(undockingContainerId, timestamp) {
        const client = await pool.connect();
        try {
            // Get all waste items that are assigned to the undocking container
            const getItemsQuery = `
                SELECT item_id FROM waste 
                WHERE container_id = $1
            `;
            const itemsResult = await client.query(getItemsQuery, [undockingContainerId]);
            const itemIds = itemsResult.rows.map(row => row.item_id);

            if (itemIds.length === 0) {
                return 0;
            }

            // Delete each waste item using the existing deleteWasteItem function
            for (const itemId of itemIds) {
                await this.deleteWasteItem(itemId);
            }

            // Log the undocking completion
            const logQuery = `
                INSERT INTO systemlogs (message)
                VALUES ($1)
            `;
            await client.query(logQuery, [
                `Undocking completed for container ${undockingContainerId} at ${timestamp}. Removed ${itemIds.length} items from system.`
            ]);

            return itemIds.length;
        }
        finally {
            client.release();
        }
    }

    static async assignUndockingContainer(itemIds, undockingContainerId) {
        const client = await pool.connect();
        try {
            await client.query('BEGIN');

            // Update waste items to assign them to the undocking container
            const updateQuery = `
                UPDATE waste 
                SET container_id = $1 
                WHERE item_id = ANY($2)
            `;
            await client.query(updateQuery, [undockingContainerId, itemIds]);

            // Log the assignment
            const logQuery = `
                INSERT INTO systemlogs (message)
                VALUES ($1)
            `;
            await client.query(logQuery, [
                `Assigned ${itemIds.length} waste items to undocking container ${undockingContainerId}`
            ]);

            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }
}

export default WasteModel;