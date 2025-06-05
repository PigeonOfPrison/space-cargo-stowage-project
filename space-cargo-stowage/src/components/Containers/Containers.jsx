import React, { useState } from 'react';
import "./containers.css";
import Button from '../Parts/Buttons';
import { containerApi } from './containerApi';

function Containers() {
    const [selectedFile, setSelectedFile] = useState(null);    // Mock data for container cards
    const containerCards = [
        { id: 'C001', name: 'Container Alpha', location: 'Bay A-12', fillPercentage: 75, items: 145 },
        { id: 'C002', name: 'Container Beta', location: 'Bay B-03', fillPercentage: 92, items: 230 },
        { id: 'C003', name: 'Container Gamma', location: 'Bay A-05', fillPercentage: 45, items: 89 },
        { id: 'C004', name: 'Container Delta', location: 'Bay C-08', fillPercentage: 88, items: 176 },
        { id: 'C005', name: 'Container Epsilon', location: 'Bay B-11', fillPercentage: 33, items: 67 },
        { id: 'C006', name: 'Container Zeta', location: 'Bay D-02', fillPercentage: 95, items: 190 },
        { id: 'C007', name: 'Container Eta', location: 'Bay C-15', fillPercentage: 52, items: 104 },
        { id: 'C008', name: 'Container Theta', location: 'Bay A-09', fillPercentage: 68, items: 136 },
        { id: 'C009', name: 'Container Iota', location: 'Bay D-07', fillPercentage: 81, items: 162 },
        { id: 'C010', name: 'Container Kappa', location: 'Bay B-14', fillPercentage: 59, items: 118 },
        { id: 'C011', name: 'Container Lambda', location: 'Bay C-01', fillPercentage: 94, items: 188 },
        { id: 'C012', name: 'Container Mu', location: 'Bay A-16', fillPercentage: 27, items: 54 },
        { id: 'C013', name: 'Container Nu', location: 'Bay D-10', fillPercentage: 73, items: 146 },
        { id: 'C014', name: 'Container Xi', location: 'Bay B-08', fillPercentage: 86, items: 172 },
        { id: 'C015', name: 'Container Omicron', location: 'Bay C-13', fillPercentage: 41, items: 82 },
        { id: 'C016', name: 'Container Pi', location: 'Bay A-04', fillPercentage: 98, items: 196 }
    ];

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setSelectedFile(file);
        } else {
            alert('Please select a valid CSV file');
        }
    };    
    
    const handleUpload = async () => {
        if (selectedFile) {
            try {
                const formData = new FormData();
                formData.append('file', selectedFile);

                const response = await fetch('http://localhost:3000/api/containers/upload', {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    throw new Error('Upload failed');
                }

                const result = await response.json();
                alert('File uploaded successfully');
                setSelectedFile(null);
                
                // TODO: Uncomment the following when backend is ready
                // const updatedContainers = await containerApi.getAllContainers();
                // setContainerCards(updatedContainers);
                
            } catch (error) {
                console.error('Error uploading file:', error);
                alert('Failed to upload file');
            }
        }
    };

    return (
        <div className="containers">
            <div className="containers-grid">
                {/* Top Left Box - File Upload */}                
                <div className="container-grid-box file-upload">
                    <h2>Import Container Data</h2>
                    <div className="upload-section">
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            id="csv-upload"
                            className="file-input"
                        />
                        <label htmlFor="csv-upload" className="file-label">
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
                </div>                {/* Top Right Box */}            <div className="container-grid-box container-stats">
                    <h2>Zone Overview</h2>                    <div className="fill-rates-list">
                        {['A', 'B', 'C', 'D'].map(zone => {
                            const zoneContainers = containerCards.filter(container => 
                                container.location.includes(`Bay ${zone}-`)
                            );
                            
                            const totalCapacity = zoneContainers.length * 100; // Each container has 100% capacity
                            const totalFilled = zoneContainers.reduce((sum, container) => 
                                sum + container.fillPercentage, 0
                            );
                            const fillPercentage = totalCapacity > 0 
                                ? Math.round((totalFilled / totalCapacity) * 100) 
                                : 0;
                            
                            let status;
                            if (fillPercentage >= 90) status = 'full';
                            else if (fillPercentage >= 60) status = 'loading';
                            else status = 'active';

                            return (
                                <div key={zone} className="fill-rate-item">
                                    <span className="container-name">Zone {zone}</span>
                                    <div className="fill-rate-bar">
                                        <div 
                                            className="fill-rate-progress"
                                            style={{ width: `${fillPercentage}%` }}
                                        ></div>
                                    </div>
                                    <span className="fill-rate-text">{fillPercentage}%</span>
                                    <span className={`status ${status}`}>
                                        {zoneContainers.length} containers
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>                {/* Bottom Box */}
                <div className="container-grid-box bottom-section">
                    <h2>Container Details</h2>
                    <div className="container-cards-grid">
                        {containerCards.map(container => (
                            <div key={container.id} className="container-card">
                                <h3 className="container-card-title">{container.name}</h3>
                                <div className="container-card-content">
                                    <p className="container-location">
                                        <span className="label">Location:</span> {container.location}
                                    </p>
                                    <div className="container-fill-info">
                                        <div className="fill-bar-wrapper">
                                            <div 
                                                className="fill-bar"
                                                style={{ width: `${container.fillPercentage}%` }}
                                            ></div>
                                        </div>
                                        <span className="fill-percentage">{container.fillPercentage}%</span>
                                    </div>
                                    <p className="items-count">
                                        <span className="label">Items:</span> {container.items}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Containers;