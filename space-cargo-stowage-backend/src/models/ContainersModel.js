// Container model - Database schema and queries for containers

import { pool } from '../config/db.config.js'; // Assuming you have a db.js file that exports your database connection pool

class ContainersModel {
    /**
     * Adds multiple containers to the database.
     * @param {Array} containers - Array of container objects to be added.
     * @returns {Promise<Array>} - Returns a promise that resolves to an array of added container objects.
     */
    static async addContainers(containers) {

        const client = await pool.connect();

        try {
            await client.query('BEGIN');
            
            const insertPromises = containers.map(container => {
                const query = `
                    INSERT INTO containers (
                        container_id, zone, width, depth, height
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                `;
                const values = [
                    container.containerId,
                    container.zone,
                    container.width,
                    container.depth,
                    container.height
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

    /**
     * Get all containers from the database
     * @returns {Promise<Array>} - Returns a promise that resolves to an array of container objects
     */
    static async getAllContainers() {
        const client = await pool.connect();
        try {
            const query = `
                SELECT container_id, zone, width, depth, height
                FROM containers
                ORDER BY zone ASC, container_id ASC
            `;
            const result = await client.query(query);
            return result.rows;
        } finally {
            client.release();
        }
    }
}

export default ContainersModel;
// Export the ContainersModel class for use in other parts of the application