import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { FixedSizeList as List } from 'react-window';
import '../../styles/items1.css';  // New Design System (was "./items.css")
import Button from '../Parts/Buttons';
import { useToast } from '../Toast/Toast';
import { ClimbingBoxLoader } from 'react-spinners';
import { fetchItems, handleItemUpload } from './itemApi';

// Extracted Row component with prop validation
const Row = ({ index, style, data }) => {
    const item = data[index];
    if (!item) return null;
    
    // Handle different date formats (some might be strings, some Date objects)
    // Check for both API field names (expiry_date) and legacy field names (expiryDate)
    const expiryDateValue = item.expiry_date || item.expiryDate;
    const expiryDate = expiryDateValue ? new Date(expiryDateValue) : null;
    const daysUntilExpiry = expiryDate ? Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24)) : null;
    
    // Determine expiry status using if-else instead of nested ternary
    let expiryStatus = 'expiring-safe';
    if (daysUntilExpiry !== null) {
        if (daysUntilExpiry <= 180) {
            expiryStatus = 'expiring-soon';
        } else if (daysUntilExpiry <= 365) {
            expiryStatus = 'expiring-medium';
        }
    }

    // Support both API response format and legacy format
    const itemName = item.name || item.itemName || 'Unknown Item';
    const usageLimit = item.usage_limit || item.quantity || 0;
    const preferredZone = item.preferred_zone || 'Not specified';
    const containerId = item.container_id || 'Unassigned';

    return (
        <div className={`item-row ${expiryStatus}`} style={style}>            
            <div className="inventory-item-info">
                <span className="item-name">{itemName}</span>
                <span className="item-quantity">Usage Limit: {usageLimit}</span>
                <span className="item-expiry">
                    Expires: {expiryDate ? expiryDate.toLocaleDateString() : 'No expiry date'}
                </span>
                <span className="item-zone">Zone: {preferredZone}</span>
                <span className="item-container">Container: {containerId}</span>
            </div>
        </div>
    );
};

Row.propTypes = {
    index: PropTypes.number.isRequired,
    style: PropTypes.object.isRequired,
    data: PropTypes.array.isRequired
};

// Mock data outside component to be accessible to Row - updated to match API response format
const mockItems = [
    { item_id: 'I001', name: 'Emergency Food Pack', width: 10.5, depth: 8.2, height: 5.0, priority: 1, expiry_date: '2026-01-15T00:00:00.000Z', usage_limit: 50, preferred_zone: 'A', container_id: null },
    { item_id: 'I002', name: 'Water Filtration System', width: 15.0, depth: 12.0, height: 8.5, priority: 2, expiry_date: '2027-03-20T00:00:00.000Z', usage_limit: 25, preferred_zone: 'B', container_id: null },
    { item_id: 'I003', name: 'Medical Supplies Kit', width: 8.0, depth: 6.5, height: 4.2, priority: 1, expiry_date: '2025-12-10T00:00:00.000Z', usage_limit: 100, preferred_zone: 'A', container_id: null },
    { item_id: 'I004', name: 'Solar Power Unit', width: 12.3, depth: 9.8, height: 6.7, priority: 3, expiry_date: '2030-06-30T00:00:00.000Z', usage_limit: 75, preferred_zone: 'C', container_id: null },
    { item_id: 'I005', name: 'Communication Device', width: 9.5, depth: 7.0, height: 3.8, priority: 2, expiry_date: '2028-09-15T00:00:00.000Z', usage_limit: 40, preferred_zone: 'B', container_id: null },
    { item_id: 'I006', name: 'Oxygen Generator', width: 7.5, depth: 7.5, height: 20.0, priority: 1, expiry_date: '2026-08-22T00:00:00.000Z', usage_limit: 30, preferred_zone: 'A', container_id: null },
    { item_id: 'I007', name: 'Thermal Blanket', width: 6.0, depth: 4.5, height: 2.0, priority: 3, expiry_date: '2027-11-05T00:00:00.000Z', usage_limit: 80, preferred_zone: 'C', container_id: null },
    { item_id: 'I008', name: 'Radiation Shield', width: 11.2, depth: 8.9, height: 7.3, priority: 1, expiry_date: '2029-04-18T00:00:00.000Z', usage_limit: 160, preferred_zone: 'A', container_id: null },
    { item_id: 'I009', name: 'Space Suit Component', width: 5.5, depth: 3.8, height: 9.2, priority: 2, expiry_date: '2026-07-30T00:00:00.000Z', usage_limit: 90, preferred_zone: 'B', container_id: null },
    { item_id: 'I010', name: 'Air Filter Cartridge', width: 4.2, depth: 4.2, height: 8.5, priority: 1, expiry_date: '2025-09-12T00:00:00.000Z', usage_limit: 65, preferred_zone: 'A', container_id: null },
    { item_id: 'I011', name: 'Emergency Beacon', width: 3.0, depth: 2.5, height: 1.8, priority: 2, expiry_date: '2028-02-25T00:00:00.000Z', usage_limit: 18, preferred_zone: 'B', container_id: null },
    { item_id: 'I012', name: 'Battery Pack', width: 8.7, depth: 5.4, height: 3.2, priority: 3, expiry_date: '2026-05-14T00:00:00.000Z', usage_limit: 42, preferred_zone: 'C', container_id: null },
    { item_id: 'I013', name: 'Repair Tool Kit', width: 13.5, depth: 10.2, height: 4.8, priority: 2, expiry_date: '2029-10-08T00:00:00.000Z', usage_limit: 95, preferred_zone: 'B', container_id: null },
    { item_id: 'I014', name: 'Navigation System', width: 9.8, depth: 6.7, height: 5.5, priority: 1, expiry_date: '2027-12-31T00:00:00.000Z', usage_limit: 60, preferred_zone: 'A', container_id: null },
    { item_id: 'I015', name: 'Waste Management Unit', width: 14.2, depth: 11.8, height: 9.5, priority: 3, expiry_date: '2026-11-19T00:00:00.000Z', usage_limit: 110, preferred_zone: 'C', container_id: null },
    { item_id: 'I016', name: 'Life Support Module', width: 16.5, depth: 13.2, height: 10.8, priority: 1, expiry_date: '2028-08-03T00:00:00.000Z', usage_limit: 40, preferred_zone: 'A', container_id: null }
];

function Items() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [items, setItems] = useState(mockItems); // Start with mock data as fallback
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { success, error: showError, warning } = useToast();

    // Load items on component mount
    useEffect(() => {
        loadItems();
    }, []);    
      const loadItems = useCallback(async () => {
        setLoading(true);
        try {
            // Try to fetch some items (first 10) from the API
            const fetchedItems = await fetchItems({ itemNumbers: 10 }, {
                onSuccess: (data) => {
                    success(`Successfully loaded ${data.items ? data.items.length : 0} items from database`);
                },
                onError: (error) => {
                    showError(`Failed to load items from database: ${error.response?.data?.message || error.message}. Using mock data instead.`);
                }
            });
            
            if (fetchedItems && fetchedItems.length > 0) {
                setItems(fetchedItems);
                setError(null);
            } else {
                // If no items from API, keep using mock data
                console.log('No items from API, displaying mock data');
                setItems(mockItems);
                setError(null);
            }
        } catch (error) {
            // If API call fails completely, use mock data and show error
            console.warn('API call failed, using mock data:', error.message);
            showError(`Could not connect to database: ${error.message}. Displaying mock data instead.`);
            setItems(mockItems);
            setError(null);
        } finally {
            setLoading(false);
        }
    }, [success, showError]);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setSelectedFile(file);
            success(`Selected file: ${file.name}`);
        } 
        else {
            showError('Please select a valid CSV file');
        }
    };    
    const handleUpload = async () => {
        if (selectedFile) {
            try {
                const result = await handleItemUpload(selectedFile);
                
                // Handle the response structure from the backend
                if (result.success) {
                    const itemsImported = result.importResults?.itemsImported || 0;
                    success(`${itemsImported} items imported successfully!`);
                    
                    // Show warnings if any
                    if (result.importResults?.errors && result.importResults.errors.length > 0) {
                        const errorCount = result.importResults.errors.length;
                        warning(`Upload completed with ${errorCount} warning${errorCount > 1 ? 's' : ''}. Check console for details.`);
                        console.warn('Upload warnings:', result.importResults.errors);
                    }
                } 
                else {
                    showError('Upload failed. Please check the file format and try again.');
                }
                
                setSelectedFile(null);
                
                // Reload items after successful upload
                await loadItems();
                
            } 
            catch (error) {
                console.error('Error uploading file:', error);
                const errorMessage = error.response?.data?.message || error.message || 'Unknown error occurred';
                showError(`Failed to upload file: ${errorMessage}`);
            }
        } 
        else {
            showError('Please select a file to upload');
        }
    };

    // Show error as toast when error state changes
    useEffect(() => {
        if (error) {
            showError(error);
        }
    }, [error, showError]);    
    
    return (
        <div className="main-container grid-container grid-2x1" id="items-page">
            {/* Top Left Box - File Upload */}
            <div className="grid-box upload-zone" id="file-upload-section">
                <h2 className="section-title">Import Items Data</h2>
                <div className="upload-area">
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        id="items-csv-upload"
                        className="file-input"
                    />
                    <label htmlFor="items-csv-upload" className="file-label">
                        Choose CSV File
                    </label>
                    <Button 
                        text="Upload File"
                        onClick={handleUpload}
                        className="btn btn-primary btn-upload"
                    />
                    {selectedFile && (
                        <p className="selected-file">Selected: {selectedFile.name}</p>
                    )}
                </div>
            </div>

            {/* Top Right Box */}                
            <div className="grid-box content-box" id="items-overview-section">
                <h2 className="section-title">Items Overview</h2>
                <div className="section-content">
                    <p>This section will contain item statistics and summary information.</p>
                </div>
            </div>                
            {/* Bottom Box */}
            <div className="grid-box content-box span-full" id="items-details-section">
                <h2 className="section-title">Items Details</h2>                    
                <div className="content-container">
                    {loading ? (
                        <div className="loading-screen">
                            <ClimbingBoxLoader 
                                color="#4f46e5" 
                                size={15}
                                speedMultiplier={0.8}
                            />
                            <p>Loading items...</p>
                        </div>                    
                        ) : (                        
                        <List
                            height={400}
                            itemCount={items.length}
                            itemSize={70}
                            itemData={items}
                            width="100%"
                        >
                            {Row}
                        </List>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Items;