import React, { useState } from 'react';
import "./wastage.css";
import Button from '../Parts/Buttons';

function Wastage() {
    // Mock data for expired/finished items (will be replaced with DB data)
    const wastedItems = [
        { id: 'W001', name: 'Emergency Food Pack', container: 'C-123', expiryDate: '2025-05-15', usesLeft: 0 },
        { id: 'W002', name: 'Medical Supplies Kit', container: 'C-456', expiryDate: '2025-05-20', usesLeft: 0 },
        { id: 'W003', name: 'Air Filter Cartridge', container: 'C-789', expiryDate: '2025-05-25', usesLeft: 0 },
        { id: 'W004', name: 'Water Purification Tabs', container: 'C-234', expiryDate: '2025-05-30', usesLeft: 0 },
        { id: 'W005', name: 'Battery Pack', container: 'C-567', expiryDate: '2025-06-01', usesLeft: 0 }
    ];

    const handleWasteExport = () => {
        // Convert data to CSV format
        const headers = ['ID', 'Item Name', 'Container', 'Expiry Date', 'Uses Left'];
        const csvData = [
            headers.join(','),
            ...wastedItems.map(item => 
                [item.id, item.name, item.container, item.expiryDate, item.usesLeft].join(',')
            )
        ].join('\\n');

        // Create and download CSV file
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'waste_report.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="wastage">
            <div className="wastage-grid">
                {/* Left Box - Expired/Finished Items List */}
                <div className="grid-box wastage-list">
                    <h2>Expired/Finished Items</h2>
                    <div className="items-list">
                        {wastedItems.map(item => (
                            <div key={item.id} className="wastage-item">                                <div className="wastage-item-header">
                                    <span className="item-name">{item.name}</span>
                                </div>
                                <div className="wastage-item-details">
                                    <span className="item-id">{item.id}</span>
                                    <span className="container">Container: {item.container}</span>
                                    <span className="expiry">Expired: {new Date(item.expiryDate).toLocaleDateString()}</span>
                                    <span className="uses">Uses Left: {item.usesLeft}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Right Box - Export Controls */}
                <div className="grid-box export-controls">
                    <h2>Generate Waste Report</h2>
                    <div className="export-section">
                        <Button
                            text="Handle Waste"
                            onClick={handleWasteExport}
                            className="export-button"
                        />
                    </div>
                </div>

                {/* Bottom Right Box - Future Analytics */}
                <div className="grid-box analytics">
                    <h2>Wastage Analytics</h2>
                    <p>This section will contain wastage analytics and visualizations.</p>
                </div>
            </div>
        </div>
    );
}

export default Wastage;