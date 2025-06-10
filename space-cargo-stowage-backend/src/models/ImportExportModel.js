// Import/Export Model - Handles CSV import/export operations
import { pool } from '../config/db.config.js';

class ImportExportModel {
    /**
     * Parse and validate CSV data for items import
     * @param {Array} itemsData - Array of item objects from CSV
     * @returns {Object} - Returns parsed items and validation errors
     */    static parseAndValidateItems(itemsData) {
        const validItems = [];
        const errors = [];

        for (let i = 0; i < itemsData.length; i++) {
            const rowNumber = i + 2; // +2 because row 1 is header, and arrays are 0-indexed
            const rawItem = itemsData[i];

            // Clean up keys and values by trimming spaces
            const item = {};
            Object.keys(rawItem).forEach(key => {
                const cleanKey = key.trim();
                const cleanValue = typeof rawItem[key] === 'string' ? rawItem[key].trim() : rawItem[key];
                item[cleanKey] = cleanValue;
            });

            // Validate required fields
            const validationError = this.validateItemData(item);
            if (validationError) {
                errors.push({
                    row: rowNumber,
                    message: validationError
                });
                continue;
            }

            // Convert to format expected by ItemsModel.addItems()
            const formattedItem = {
                itemId: item.item_id || `ITEM_${Date.now()}_${i}`,
                name: item.name,
                width: parseFloat(item.width),
                depth: parseFloat(item.depth),
                height: parseFloat(item.height),
                priority: parseInt(item.priority) || 1,
                expiryDate: item.expiry_date ? new Date(item.expiry_date) : null,
                usageLimit: parseInt(item.usage_limit) || 1,
                preferredZone: item.preferred_zone || null
            };

            validItems.push(formattedItem);
        }

        return {
            validItems,
            errors,
            totalProcessed: itemsData.length
        };
    }    /**
     * Validate item data from CSV
     * @param {Object} item - Item object to validate
     * @returns {string|null} - Error message or null if valid
     */
    static validateItemData(item) {
        if (!item.name || item.name.trim() === '') {
            return 'Item name is required';
        }

        if (!item.width || isNaN(parseFloat(item.width))) {
            return 'Valid width is required';
        }

        if (!item.depth || isNaN(parseFloat(item.depth))) {
            return 'Valid depth is required';
        }

        if (!item.height || isNaN(parseFloat(item.height))) {
            return 'Valid height is required';
        }

        if (item.priority && isNaN(parseInt(item.priority))) {
            return 'Priority must be a number';
        }

        if (item.usage_limit && isNaN(parseInt(item.usage_limit))) {
            return 'Usage limit must be a number';
        }

        if (item.expiry_date && isNaN(Date.parse(item.expiry_date))) {
            return 'Invalid expiry date format';
        }

        return null; // Valid
    }

    /**
     * Parse and validate CSV data for containers import
     * @param {Array} containersData - Array of container objects from CSV
     * @returns {Object} - Returns parsed containers and validation errors
     */    static parseAndValidateContainers(containersData) {
        const validContainers = [];
        const errors = [];

        for (let i = 0; i < containersData.length; i++) {
            const rowNumber = i + 2; // +2 because row 1 is header, and arrays are 0-indexed
            const rawContainer = containersData[i];

            // Clean up keys and values by trimming spaces
            const container = {};
            Object.keys(rawContainer).forEach(key => {
                const cleanKey = key.trim();
                const cleanValue = typeof rawContainer[key] === 'string' ? rawContainer[key].trim() : rawContainer[key];
                container[cleanKey] = cleanValue;
            });

            // Validate required fields
            const validationError = this.validateContainerData(container);
            if (validationError) {
                errors.push({
                    row: rowNumber,
                    message: validationError
                });
                continue;
            }

            // Convert to format expected by ContainersModel.addContainers()
            const formattedContainer = {
                containerId: container.container_id,
                zone: container.zone,
                width: parseFloat(container.width),
                depth: parseFloat(container.depth),
                height: parseFloat(container.height)
            };

            validContainers.push(formattedContainer);
        }

        return {
            validContainers,
            errors,
            totalProcessed: containersData.length
        };
    }

    /**
     * Validate container data from CSV
     * @param {Object} container - Container object to validate
     * @returns {string|null} - Error message or null if valid
     */
    static validateContainerData(container) {
        if (!container.container_id || container.container_id.trim() === '') {
            return 'Container ID is required';
        }

        if (!container.zone || container.zone.trim() === '') {
            return 'Zone is required';
        }

        if (!container.width || isNaN(parseFloat(container.width))) {
            return 'Valid width is required';
        }

        if (!container.depth || isNaN(parseFloat(container.depth))) {
            return 'Valid depth is required';
        }

        if (!container.height || isNaN(parseFloat(container.height))) {
            return 'Valid height is required';
        }

        // Validate dimensions are positive
        if (parseFloat(container.width) <= 0) {
            return 'Width must be greater than 0';
        }

        if (parseFloat(container.depth) <= 0) {
            return 'Depth must be greater than 0';
        }

        if (parseFloat(container.height) <= 0) {
            return 'Height must be greater than 0';
        }

        return null; // Valid
    }

    /**
     * Get all item placements for export
     * @returns {Promise<Array>} - Returns a promise that resolves to an array of placement objects
     */
    static async getAllPlacements() {
        const client = await pool.connect();
        try {
            const query = `
                SELECT 
                    p.item_id,
                    p.container_id,
                    p.xi,
                    p.yi,
                    p.zi,
                    p.xj,
                    p.yj,
                    p.zj
                FROM placements p
                ORDER BY p.container_id ASC, p.item_id ASC
            `;
            const result = await client.query(query);
            return result.rows;
        } finally {
            client.release();
        }
    }
}

export default ImportExportModel;