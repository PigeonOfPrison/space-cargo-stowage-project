// Import/Export Controller - Handles CSV import/export operations
import multer from 'multer';
import csv from 'csv-parser';
import fs from 'fs';
import ImportExportModel from '../models/ImportExportModel.js';
import ItemsModel from '../models/ItemsModel.js';
import ContainersModel from '../models/ContainersModel.js';
import OptimizationService from '../services/optimizationService.js';

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) {
            cb(null, true);
        } else {
            cb(new Error('Only CSV files are allowed'), false);
        }
    }
});

/**
 * Handle CSV file upload and parse items data
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export async function importItems(req, res) {
    // Use multer middleware to handle file upload
    upload.single('csvFile')(req, res, async (err) => {
        if (err) {
            return res.status(400).json({
                success: false,
                message: `Upload error: ${err.message}`
            });
        }

        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'No CSV file uploaded'
            });
        }

        const filePath = req.file.path;
        const itemsData = [];

        try {
            // Parse CSV file
            await new Promise((resolve, reject) => {
                fs.createReadStream(filePath)
                    .pipe(csv())
                    .on('data', (row) => {
                        itemsData.push(row);
                    })
                    .on('end', resolve)
                    .on('error', reject);
            });   

            // Parse and validate CSV data
            const parseResults = ImportExportModel.parseAndValidateItems(itemsData);
            
            if (parseResults.validItems.length === 0) {
                // Clean up uploaded file
                fs.unlinkSync(filePath);
                
                return res.status(400).json({
                    success: false,
                    message: 'No valid items found in CSV',
                    importResults: {
                        itemsImported: 0,
                        errors: parseResults.errors,
                        totalProcessed: parseResults.totalProcessed
                    }
                });
            }            
            // Add items to database using existing ItemsModel method
            const addedItems = await ItemsModel.addItems(parseResults.validItems);

            // Get containers for optimization using existing ContainersModel method
            const containers = await ContainersModel.getAllContainers();

            if (containers.length === 0) {
                // Clean up uploaded file
                fs.unlinkSync(filePath);
                
                return res.status(400).json({
                    success: false,
                    message: 'No containers available for placement optimization',
                    importResults: {
                        itemsImported: addedItems.length,
                        errors: parseResults.errors,
                        totalProcessed: parseResults.totalProcessed
                    }
                });
            }

            // Optimize placement
            let optimizationResults = null;
            if (parseResults.validItems.length > 0) {
                try {
                    optimizationResults = await OptimizationService.optimizePlacement(
                        parseResults.validItems, 
                        containers
                    );                    
                    // Update items with container assignments using existing method
                    if (optimizationResults && optimizationResults.placements) {
                        await ItemsModel.assignContainers(optimizationResults.placements);
                    }
                } catch (optimizationError) {
                    console.warn('Optimization failed:', optimizationError.message);
                    // Continue without optimization
                }
            }

            // Clean up uploaded file
            fs.unlinkSync(filePath);            
            return res.status(200).json({
                success: true,
                message: 'Items imported successfully',
                importResults: {
                    itemsImported: addedItems.length,
                    errors: parseResults.errors,
                    totalProcessed: parseResults.totalProcessed
                },
                optimizationResults: optimizationResults ? {
                    totalItemsPlaced: optimizationResults.placements?.length || 0,
                    unplacedItems: optimizationResults.unplacedItems?.length || 0
                } : null
            });
        } 
        catch (error) {
            // Clean up uploaded file in case of error
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }

            console.error('Error importing items:', error);
            return res.status(500).json({
                success: false,
                message: 'Failed to import items',
                error: error.message
            });
        }
    });
}

/**
 * Handle container import from CSV
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export async function importContainers(req, res) {
    // Use multer middleware to handle file upload
    upload.single('csvFile')(req, res, async (err) => {
        if (err) {
            return res.status(400).json({
                success: false,
                message: `Upload error: ${err.message}`
            });
        }

        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'No CSV file uploaded'
            });
        }

        const filePath = req.file.path;
        const containersData = [];

        try {
            // Parse CSV file
            await new Promise((resolve, reject) => {
                fs.createReadStream(filePath)
                    .pipe(csv())
                    .on('data', (row) => {
                        containersData.push(row);
                    })
                    .on('end', resolve)
                    .on('error', reject);
            });

            // Parse and validate CSV data
            const parseResults = ImportExportModel.parseAndValidateContainers(containersData);
            
            let addedContainers = [];
            if (parseResults.validContainers.length > 0) {
                // Add containers to database using existing ContainersModel method
                addedContainers = await ContainersModel.addContainers(parseResults.validContainers);
            }

            // Clean up uploaded file
            fs.unlinkSync(filePath);

            return res.status(200).json({
                success: true,
                containersImported: addedContainers.length,
                errors: parseResults.errors
            });

        } catch (error) {
            // Clean up uploaded file in case of error
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }

            console.error('Error importing containers:', error);
            return res.status(500).json({
                success: false,
                containersImported: 0,
                errors: [{
                    row: 0,
                    message: `Failed to import containers: ${error.message}`
                }]
            });
        }
    });
}

/**
 * Export current arrangements to CSV
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export async function exportArrangements(req, res) {
    try {
        // Get all placements with item and container information
        const placements = await ImportExportModel.getAllPlacements();
        
        if (placements.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'No item placements found to export'
            });
        }

        // Create CSV content
        const csvHeader = 'Item ID,Container ID,Coordinates (W1,D1,H1),(W2,D2,H2)\n';
        const csvRows = placements.map(placement => {
            const w1 = parseFloat(placement.xi).toFixed(1);
            const d1 = parseFloat(placement.yi).toFixed(1);
            const h1 = parseFloat(placement.zi).toFixed(1);
            const w2 = parseFloat(placement.xj).toFixed(1);
            const d2 = parseFloat(placement.yj).toFixed(1);
            const h2 = parseFloat(placement.zj).toFixed(1);
            
            return `${placement.item_id},${placement.container_id},"(${w1},${d1},${h1})","(${w2},${d2},${h2})"`;
        }).join('\n');

        const csvContent = csvHeader + csvRows;

        // Set response headers for CSV download
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const filename = `cargo-arrangements-${timestamp}.csv`;
        
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Length', Buffer.byteLength(csvContent));

        return res.status(200).send(csvContent);

    } catch (error) {
        console.error('Error exporting arrangements:', error);
        return res.status(500).json({
            success: false,
            message: 'Failed to export arrangements',
            error: error.message
        });
    }
}

export default { importItems, importContainers, exportArrangements };