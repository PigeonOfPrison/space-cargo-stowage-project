import React, { useState, useEffect, useCallback } from 'react';
import "../../styles/containers1.css";  // New Design System (was "./containers.css")
import Button from '../Parts/Buttons';
import { getAllContainers, handleContainerUpload } from './containerApi';
import { useToast } from '../Toast/Toast';
import { ClimbingBoxLoader } from 'react-spinners';

function Containers() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [containerCards, setContainerCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);    const { success, error: showError, warning } = useToast();
    
    const loadContainers = useCallback(async () => {
        try {
            setLoading(true);
            const containers = await getAllContainers();
            
            // Transform API data to match UI format
            const transformedContainers = containers.map(container => ({
                id: container.containerId,
                name: `Container ${container.containerId}`,
                location: `Zone ${container.zone}`,
                dimensions: `${container.width}×${container.depth}×${container.height}`,
                width: container.width,
                depth: container.depth,
                height: container.height,
                zone: container.zone,
                // Mock data for fields not provided by API yet
                fillPercentage: Math.floor(Math.random() * 100),
                items: Math.floor(Math.random() * 200)
            }));
            
            setContainerCards(transformedContainers);
            setError(null);

        }        
        catch (err) {
            console.error('Failed to load containers:', err);
            setError('Failed to load containers');

            // Fallback to mock data if API fails
            setContainerCards([
                { id: 'C001', name: 'Container Alpha', location: 'Bay A-12', fillPercentage: 75, items: 145 },
                { id: 'C002', name: 'Container Beta', location: 'Bay B-03', fillPercentage: 92, items: 230 },
                { id: 'C003', name: 'Container Gamma', location: 'Bay A-05', fillPercentage: 45, items: 89 },
            ]);        }
        finally {
            setLoading(false);
        }    
    }, []);    

    // Load containers on component mount
    useEffect(() => {
        loadContainers();
    }, [loadContainers]);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'text/csv') {
            setSelectedFile(file);
            success(`Selected file: ${file.name}`);
        } else {
            showError('Please select a valid CSV file');
        }
    };    
    
    const handleUpload = async () => {
        if (selectedFile) {
            try {
                const result = await handleContainerUpload(selectedFile);
                
                // Handle the response
                if (result.success) {
                    success(`${result.containersImported} containers imported successfully!`);
                    
                    // Show warnings if any
                    if (result.errors && result.errors.length > 0) {
                        const errorCount = result.errors.length;
                        warning(`Upload completed with ${errorCount} warning${errorCount > 1 ? 's' : ''}. Check console for details.`);
                        console.warn('Upload warnings:', result.errors);
                    }
                } else {
                    showError('Upload failed. Please check the file format and try again.');
                }
                
                setSelectedFile(null);
                
                // Reload containers after successful upload
                await loadContainers();
                
            } catch (error) {
                console.error('Error uploading file:', error);
                showError('Failed to upload file. Please try again.');
            }
        } else {
            showError('Please select a file to upload');
        }    };    

    // Show error as toast when error state changes
    useEffect(() => {
        if (error) {
            showError(error);
        }
    }, [error, showError]);    // Show simple loader during initial load
    if (loading && containerCards.length === 0) {
        return (
            <div className="loading-screen" id="containers-loading">
                <ClimbingBoxLoader 
                    color="#4f46e5" 
                    size={15}
                    speedMultiplier={0.8}
                />
                <p>Loading containers...</p>
            </div>
        );
    }
      return (
        <div className="main-container grid-container grid-2x1" id="containers-page">            {/* Top Left Box - File Upload */}                
            <div className="grid-box upload-zone" id="file-upload-section">
                <h2 className="section-title">Import Container Data</h2>                
                <div className="upload-section">
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        id="containers-csv-upload"
                        className="file-input"
                    />
                    <label htmlFor="containers-csv-upload" className="file-label">
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
            
            {/* Top Right Box - Zone Overview */}            
            <div className="grid-box content-box" id="zone-overview-section">
                <h2 className="section-title">Zone Overview</h2>                    
                {loading ? (
                    <div className="zone-loading">
                        <div className="skeleton-line skeleton-text"></div>
                        <div className="skeleton-line skeleton-text"></div>
                        <div className="skeleton-line skeleton-text"></div>
                    </div>
                ) : (
                    <div className="zone-stats-list">
                        {['A', 'B', 'C', 'D'].map(zone => {
                            const zoneContainers = containerCards.filter(container => 
                                container.zone === zone || container.location.includes(`Bay ${zone}-`)
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
                                <div key={zone} className="zone-stat-item">
                                    <span className="zone-name">Zone {zone}</span>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill"
                                            style={{ width: `${fillPercentage}%` }}
                                        ></div>
                                    </div>
                                    <span className="progress-text">{fillPercentage}%</span>
                                    <span className={`status-badge variant-${status}`}>
                                        {zoneContainers.length} containers
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Bottom Box - Container Details */}
            <div className="grid-box content-box span-full" id="container-details-section">
                <h2 className="section-title">Container Details</h2>
                <div className="container-cards-grid">
                    {containerCards.map(container => (
                        <div key={container.id} className="card container-card">
                            <h3 className="card-title">{container.name}</h3>
                            <div className="card-content">
                                <p className="container-location">
                                    <span className="label">Location:</span> {container.location}
                                </p>
                                <p className="container-dimensions">
                                    <span className="label">Dimensions:</span> {container.dimensions}
                                </p>
                                <div className="container-fill-display">
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill"
                                            style={{ width: `${container.fillPercentage}%` }}
                                        ></div>
                                    </div>
                                    <span className="progress-text">{container.fillPercentage}%</span>
                                </div>
                                <p className="container-items">
                                    <span className="label">Items:</span> {container.items}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Containers;