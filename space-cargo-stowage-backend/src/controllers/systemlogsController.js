import SystemlogsModel from '../models/SystemlogsModel.js';

/**
 * Get system logs with optional filtering
 * @param {Object} req - Express request object with query parameters
 * @param {Object} req.query - Query parameters
 * @param {string} req.query.startDate - Start date in ISO format
 * @param {string} req.query.endDate - End date in ISO format
 * @param {string} req.query.itemId - Optional item ID filter
 * @param {string} req.query.userId - Optional user ID filter
 * @param {string} req.query.actionType - Optional action type filter
 * @param {Object} res - Express response object
 */
export async function getSystemLogs(req, res) {
    try {
        const { startDate, endDate, itemId, userId, actionType } = req.query;
        
        // Validate required date parameters
        if (!startDate || !endDate) {
            return res.status(400).json({
                success: false,
                message: 'Start date and end date are required'
            });
        }

        // Validate date formats
        if (isNaN(Date.parse(startDate)) || isNaN(Date.parse(endDate))) {
            return res.status(400).json({
                success: false,
                message: 'Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            });
        }

        // Validate actionType if provided
        if (actionType && !['placement', 'retrieval', 'rearrangement', 'disposal'].includes(actionType)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid actionType. Must be one of: placement, retrieval, rearrangement, disposal'
            });
        }
        // Get logs with filters
        const logs = await SystemlogsModel.getLogs({
            startDate,
            endDate,
            itemId,
            userId,
            actionType
        });

        // Format the response according to the required structure
        const formattedLogs = logs.map(log => ({
            timestamp: log.created_at,
            userId: log.user_id || null,
            actionType: log.actionType,
            itemId: log.item_id || null,
            details: {
                fromContainer: log.from_container_id || null,
                toContainer: log.to_container_id || null,
                reason: log.message
            }
        }));

        return res.status(200).json({
            logs: formattedLogs
        });

    } catch (error) {
        console.error('Error retrieving system logs:', error);
        return res.status(500).json({
            success: false,
            message: 'Failed to retrieve system logs',
            error: error.message
        });
    }
}

export async function getSomeLogs(req, res) {
    try {
        const logs = await SystemlogsModel.getSomeLogs();
        return res.status(200).json({
            logs: logs
        });
    } catch (error) {
        console.error('Error retrieving some system logs:', error);
        return res.status(500).json({
            success: false,
            message: 'Failed to retrieve some system logs',
            error: error.message
        });
    }
}

export default { getSystemLogs };