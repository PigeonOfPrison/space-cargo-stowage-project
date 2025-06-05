import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { FixedSizeList as List } from 'react-window';
import './items.css';
import Button from '../Parts/Buttons';

// Extracted Row component with prop validation
const Row = ({ index, style }) => {
    const item = mockItems[index];
    const daysUntilExpiry = Math.ceil((new Date(item.expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
    
    // Determine expiry status using if-else instead of nested ternary
    let expiryStatus;
    if (daysUntilExpiry <= 180) {
        expiryStatus = 'expiring-soon';
    } else if (daysUntilExpiry <= 365) {
        expiryStatus = 'expiring-medium';
    } else {
        expiryStatus = 'expiring-safe';
    }

    return (
        <div className={`item-row ${expiryStatus}`} style={style}>            
        <div className="inventory-item-info">
                <span className="item-name">{item.name}</span>
                <span className="item-quantity">Quantity: {item.quantity}</span>
                <span className="item-expiry">Expires: {new Date(item.expiryDate).toLocaleDateString()}</span>
            </div>
        </div>
    );
};

Row.propTypes = {
    index: PropTypes.number.isRequired,
    style: PropTypes.object.isRequired
};

// Mock data outside component to be accessible to Row
const mockItems = [
    { id: 'I001', name: 'Emergency Food Pack', quantity: 1500, expiryDate: '2026-01-15' },
    { id: 'I002', name: 'Water Filtration System', quantity: 200, expiryDate: '2027-03-20' },
    { id: 'I003', name: 'Medical Supplies Kit', quantity: 350, expiryDate: '2025-12-10' },
    { id: 'I004', name: 'Solar Power Unit', quantity: 75, expiryDate: '2030-06-30' },
    { id: 'I005', name: 'Communication Device', quantity: 120, expiryDate: '2028-09-15' },
    { id: 'I006', name: 'Oxygen Generator', quantity: 45, expiryDate: '2026-08-22' },
    { id: 'I007', name: 'Thermal Blanket', quantity: 800, expiryDate: '2027-11-05' },
    { id: 'I008', name: 'Radiation Shield', quantity: 160, expiryDate: '2029-04-18' },
    { id: 'I009', name: 'Space Suit Component', quantity: 90, expiryDate: '2026-07-30' },
    { id: 'I010', name: 'Air Filter Cartridge', quantity: 650, expiryDate: '2025-09-12' },
    { id: 'I011', name: 'Emergency Beacon', quantity: 180, expiryDate: '2028-02-25' },
    { id: 'I012', name: 'Battery Pack', quantity: 420, expiryDate: '2026-05-14' },
    { id: 'I013', name: 'Repair Tool Kit', quantity: 95, expiryDate: '2029-10-08' },
    { id: 'I014', name: 'Navigation System', quantity: 60, expiryDate: '2027-12-31' },
    { id: 'I015', name: 'Waste Management Unit', quantity: 110, expiryDate: '2026-11-19' },
    { id: 'I016', name: 'Life Support Module', quantity: 40, expiryDate: '2028-08-03' }
];

function Items() {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setSelectedFile(file);
        } else {
            alert('Please select a valid CSV file');
        }
    };

    const handleUpload = () => {
        if (selectedFile) {
            // Handle file upload logic here
            console.log('Uploading file:', selectedFile.name);
        }
    };

    return (
        <div className="items">
            <div className="items-grid">
                {/* Top Left Box - File Upload */}
                <div className="grid-box file-upload">
                    <h2>Import Items Data</h2>
                    <div className="upload-section">
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
                            className="upload-button"
                        />
                        {selectedFile && (
                            <p className="selected-file">Selected: {selectedFile.name}</p>
                        )}
                    </div>
                </div>

                {/* Top Right Box */}                
                <div className="grid-box item-stats">
                    <h2>Items Overview</h2>
                    <p>This section will contain item statistics and summary information.</p>
                </div>

                {/* Bottom Box */}
                <div className="grid-box bottom-section">
                    <h2>Items Details</h2>
                    <div className="items-list-container">
                        <List
                            height={400}
                            itemCount={mockItems.length}
                            itemSize={70}
                            width="100%"
                        >
                            {Row}
                        </List>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Items;