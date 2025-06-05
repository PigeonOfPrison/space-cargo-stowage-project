import { pool } from '../config/db.config.js';
import ItemsPlacer from '../services/itemsPlacer.js';

class ItemsModel {
    /**
     * Adds multiple items to the database.
     * @param {Array} items - Array of item objects to be added.
     * @returns {Promise<Array>} - Returns a promise that resolves to an array of added item objects.
     */
    static async addItems(items) {

        const client = await pool.connect();

        try {
            await client.query('BEGIN');
            
            const insertPromises = items.map(item => {
                const query = `
                    INSERT INTO items (
                        item_id, name, width, depth, height, 
                        priority, expiry_date, usage_limit, preferred_zone
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING *
                `;
                const values = [
                    item.itemId,
                    item.name,
                    item.width,
                    item.depth,
                    item.height,
                    item.priority,
                    item.expiryDate,
                    item.usageLimit,
                    item.preferredZone
                ];
                return client.query(query, values);
            });

            const results = await Promise.all(insertPromises);
            await client.query('COMMIT');
            
            return results.map(result => result.rows[0]);
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }


    /**function to update the container id where each item is placed */
    static async assignContainers(placements) {
        const client = await pool.connect();

        try {
            await client.query('BEGIN');

            const updatePromises = placements.map(placement => {
                const query = `
                    UPDATE items 
                    SET container_id = $1 
                    WHERE item_id = $2
                `;
                const values = [placement.containerId, placement.itemId];
                return client.query(query, values);
            });

            await Promise.all(updatePromises);
            await client.query('COMMIT');
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }

    static async searchItems(query) {
        const client = await pool.connect();

        try {
            const { itemId, itemName, userId } = query;
            let sqlQuery = 'SELECT * FROM items WHERE 1=1';
            const values = [];

            if (itemId) {
                sqlQuery += ' AND item_id = $1';
                values.push(itemId);
            }
            if (itemName) {
                sqlQuery += ' AND name ILIKE $2';
                values.push(`%${itemName}%`);
            }
            sqlQuery += ` 
            ORDER BY 
                usage_limit ASC,  -- Least number of uses first
                expiry_date ASC   -- Closest expiry date first
            LIMIT 1               -- Get only one item
            `;
            


            // Log the search query if userId is provided
            if (userId) {
                const logQuery = `
                    INSERT INTO systemlogs (message)
                    VALUES ($1)
                `;
                await client.query(logQuery, [
                    `User ${userId} searched for items with itemId: ${itemId}, itemName: ${itemName}`
                ]);
            }

            const result = await client.query(sqlQuery, values);
            return result.rows;
        } finally {
            client.release();
        }
    }

    static async retrieveItem(itemId, userId, timestamp) {
        const client = await pool.connect();
        
        try {
            await client.query('BEGIN');

            // First get the item to check its current usage limit
            const getItemQuery = `SELECT * FROM items WHERE item_id = $1`;
            const item = await client.query(getItemQuery, [itemId]);

            if (item.rows.length === 0) {
                throw new Error('Item not found');
            }

            // Update the item's usage limit
            const updateQuery = `
                UPDATE items 
                SET usage_limit = usage_limit - 1 
                WHERE item_id = $1
            `;
            await client.query(updateQuery, [itemId]);

            // Log the retrieval action
            const logQuery = `
                INSERT INTO systemlogs (message)
                VALUES ($1)
            `;
            await client.query(logQuery, [
                `User ${userId} retrieved ${item.rows[0].name} with (ID: ${itemId})`
            ]);

            // If usage limit is 1, this will be the last use, so move to waste and delete
            if (item.rows[0].usage_limit <= 1) {
                // Move to waste table
                const wasteQuery = `
                    INSERT INTO waste (item_id, item_name, reason, container_id)
                    VALUES ($1, $2, $3, $4)
                `;
                await client.query(wasteQuery, [
                    itemId,
                    item.rows[0].name,
                    'Item usage limit reached zero',
                    item.rows[0].container_id || null
                ]);

                // Delete from items table
                const deleteQuery = `DELETE FROM items WHERE item_id = $1`;
                await client.query(deleteQuery, [itemId]);
            }

            await client.query('COMMIT');
            return item.rows[0];
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }

    static async checkSpaceAvailability(containerId, startCoords, endCoords) {
        const client = await pool.connect();
        try {
            // Check if container exists
            const containerQuery = `SELECT * FROM containers WHERE container_id = $1`;
            const containerResult = await client.query(containerQuery, [containerId]);
            
            if (containerResult.rows.length === 0) {
                throw new Error('Container not found');
            }

            // Query existing placements in the container to check for overlaps
            const placementsQuery = `
                SELECT * FROM placements 
                WHERE container_id = $1
            `;
            const placements = await client.query(placementsQuery, [containerId]);

            // Delegate actual space checking to the ItemsPlacer service
            const itemsPlacer = new ItemsPlacer();
            return itemsPlacer.checkSpace(
                
                placements.rows,
                startCoords,
                endCoords
            );
        } finally {
            client.release();
        }
    }

    static async placeItem(itemId, containerId, position, userId, timestamp) {
        const client = await pool.connect();
        try {
            await client.query('BEGIN');

            // Insert into placements table
            const placementQuery = `
                UPDATE placements
                SET container_id = $1,
                xi = $2,
                yi = $3,
                zi = $4,
                xj = $5,
                yj = $6,
                zj = $7
                WHERE item_id = $8
            `;
            const placementValues = [
                itemId,
                containerId,
                position.startCoordinates.width,
                position.startCoordinates.depth,
                position.startCoordinates.height,
                position.endCoordinates.width,
                position.endCoordinates.depth,
                position.endCoordinates.height
            ];
            await client.query(placementQuery, placementValues);

            // Update item's container_id
            const updateItemQuery = `
                UPDATE items 
                SET container_id = $1 
                WHERE item_id = $2
            `;
            await client.query(updateItemQuery, [containerId, itemId]);

            // Log the placement
            const logQuery = `
                INSERT INTO systemlogs (message)
                VALUES ($1)
            `;
            await client.query(logQuery, [
                `User ${userId} placed item ${itemId} in container ${containerId}`
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

export default ItemsModel;
