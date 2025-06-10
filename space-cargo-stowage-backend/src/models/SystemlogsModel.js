// System Logs Model - Database operations for system logs
import { pool } from '../config/db.config.js';

class SystemlogsModel {    /**
     * Add a new system log entry
     * @param {Object} logData - Log data object
     * @param {string} logData.message - Log message
     * @param {string} logData.itemId - Optional item ID
     * @param {string} logData.userId - Optional user ID
     * @param {string} logData.fromContainerId - Optional source container ID
     * @param {string} logData.toContainerId - Optional destination container ID
     * @param {string} logData.actionType - Action type (placement, retrieval, rearrangement, disposal)
     * @returns {Promise<Object>} - Returns the created log entry
     */
    static async addLog(logData) {
        const { message, itemId, userId, fromContainerId, toContainerId, actionType } = logData;
        const client = await pool.connect();
        
        try {
            const query = `
                INSERT INTO systemlogs (message, item_id, user_id, from_container_id, to_container_id, actionType) 
                VALUES ($1, $2, $3, $4, $5, $6) 
                RETURNING *
            `;
            const values = [message, itemId || null, userId || null, fromContainerId || null, toContainerId || null, actionType];
            const result = await client.query(query, values);
            return result.rows[0];
        } finally {
            client.release();
        }
    }

    /**
     * Get system logs with optional filtering
     * @param {Object} filters - Filter criteria
     * @param {string} filters.startDate - Start date in ISO format
     * @param {string} filters.endDate - End date in ISO format
     * @param {string} filters.itemId - Optional item ID filter
     * @param {string} filters.userId - Optional user ID filter
     * @param {string} filters.actionType - Optional action type filter
     * @returns {Promise<Array>} - Returns an array of log entries
     */
    static async getLogs(filters) {
        const { startDate, endDate, itemId, userId, actionType } = filters;
        const client = await pool.connect();
        
        try {            let query = `
                SELECT 
                    log_id,
                    message,
                    item_id,
                    user_id,
                    from_container_id,
                    to_container_id,
                    actionType,
                    created_at
                FROM systemlogs
                WHERE created_at >= $1 AND created_at <= $2
            `;
            
            const values = [startDate, endDate];
            let paramCount = 2;
            
            // Add optional filters
            if (itemId) {
                paramCount++;
                query += ` AND item_id = $${paramCount}`;
                values.push(itemId);
            }
            
            if (userId) {
                paramCount++;
                query += ` AND user_id = $${paramCount}`;
                values.push(userId);
            }
            
            if (actionType) {
                paramCount++;
                query += ` AND actionType = $${paramCount}`;
                values.push(actionType);
            }
            
            // Add sorting
            query += ' ORDER BY created_at DESC';
            
            const result = await client.query(query, values);
            return result.rows;
        } finally {
            client.release();
        }
    }

    static async getSomeLogs(limit = 50) {
        const client = await pool.connect();
        
        try {
            const query = `
                SELECT 
                    log_id,
                    message,
                    item_id,
                    user_id,
                    from_container_id,
                    to_container_id,
                    actionType,
                    created_at
                FROM systemlogs
                ORDER BY created_at DESC
                LIMIT $1
            `;
            const result = await client.query(query, [limit]);
            return result.rows;
        } 
        finally {
            client.release();
        }
    }
}

export default SystemlogsModel;