import React, { useState, useEffect } from 'react';
import "../../styles/wastage1.css";  // New Design System (was "./wastage.css")
import Button from '../Parts/Buttons';
import { useToast } from '../Toast/Toast';
import { ClimbingBoxLoader } from 'react-spinners';
import { getWastage, handleWasteReturnPlan } from './wastageApi';
import { FaTrashAlt, FaClipboardList, FaBox, FaMapMarkerAlt, FaBarcode, FaExclamationTriangle, FaCube } from 'react-icons/fa';

function Wastage() {
    const { success, error: showError, info } = useToast();    const [wasteItems, setWasteItems] = useState([]);
    const [returnPlan, setReturnPlan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generateLoading, setGenerateLoading] = useState(false);
    
    // Form inputs for waste return plan
    const [undockingContainer, setUndockingContainer] = useState('');
    const [undockingDate, setUndockingDate] = useState('');
    const [maxVolume, setMaxVolume] = useState(1000); // default max volume    // Mock data for fallback (will be replaced with DB data)
    const mockWasteItems = [
        { itemId: 'W001', name: 'Emergency Food Pack', reason: 'Expired', containerId: 'C-123', 
          position: { startCoordinates: { width: 10, depth: 10, height: 5 }, endCoordinates: { width: 20, depth: 20, height: 10 } } },
        { itemId: 'W002', name: 'Medical Supplies Kit', reason: 'Out of Uses', containerId: 'C-456', 
          position: { startCoordinates: { width: 5, depth: 15, height: 8 }, endCoordinates: { width: 15, depth: 25, height: 15 } } },
        { itemId: 'W003', name: 'Air Filter Cartridge', reason: 'Expired', containerId: 'C-789', 
          position: { startCoordinates: { width: 20, depth: 5, height: 12 }, endCoordinates: { width: 30, depth: 15, height: 20 } } },
        { itemId: 'W004', name: 'Water Purification Tabs', reason: 'Out of Uses', containerId: 'C-234', 
          position: { startCoordinates: { width: 8, depth: 12, height: 3 }, endCoordinates: { width: 18, depth: 22, height: 8 } } },
        { itemId: 'W005', name: 'Battery Pack', reason: 'Expired', containerId: 'C-567', 
          position: { startCoordinates: { width: 15, depth: 8, height: 10 }, endCoordinates: { width: 25, depth: 18, height: 15 } } }
    ];
    
    // Load waste items on component mount
    useEffect(() => {
        loadWasteItems();
    }, []);
      const loadWasteItems = async () => {
        setLoading(true);
        try {
            const response = await getWastage();
            if (response.success && response.wasteItems) {
                setWasteItems(response.wasteItems);
                info(`Loaded ${response.wasteItems.length} waste items from server`);
            } else {
                // Fallback to mock data
                setWasteItems(mockWasteItems);
                info('Using mock waste data - server data unavailable');
            }
        } catch (error) {
            console.error('Failed to load waste items:', error);
            setWasteItems(mockWasteItems);
            showError('Failed to load waste items from server, using mock data');
        } finally {
            setLoading(false);
        }
    };
      const handleGenerateReturnPlan = async () => {
        if (!undockingContainer || !undockingDate) {
            showError('Please provide undocking container ID and date');
            return;
        }
        
        setGenerateLoading(true);
        try {
            const response = await handleWasteReturnPlan(undockingContainer, undockingDate, maxVolume);
            if (response.success) {
                setReturnPlan(response);
                success(`Generated return plan with ${response.returnPlan?.length || 0} items`);
            } else {
                showError('Failed to generate return plan');
            }
        } catch (error) {
            console.error('Error generating return plan:', error);
            showError('Failed to generate return plan');
        } finally {
            setGenerateLoading(false);
        }
    };
    const handleWasteExport = () => {
        // Convert data to CSV format
        const headers = ['ID', 'Item Name', 'Container', 'Reason'];
        const csvData = [
            headers.join(','),
            ...wasteItems.map(item => 
                [item.itemId, item.name, item.containerId, item.reason].join(',')
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
          // Show success message
        success(`Waste report exported successfully! Downloaded ${wasteItems.length} items.`);
    };    if (loading) {
        return (
            <div className="loading-screen" id="wastage-loading">
                <ClimbingBoxLoader 
                    color="#4f46e5" 
                    size={15}
                    speedMultiplier={0.8}
                />
                <p>Loading waste items...</p>
            </div>
        );
    }

    return (
        <div className="main-container grid-container grid-2x2" id="wastage-page">            {/* Left Box - Expired/Finished Items List */}
            <div className="grid-box content-box" id="waste-items-section">
                <h2 className="section-title">
                    <FaTrashAlt className="section-icon" />
                    Expired/Finished Items
                </h2>
                <div className="content-container">
                    {wasteItems.map(item => (
                        <div key={item.itemId} className="card waste-item">
                            <div className="card-header">
                                <div className="item-header-content">
                                    <FaBox className="item-icon" />
                                    <span className="item-name">{item.name}</span>
                                </div>
                                <div className="item-status">
                                    <FaExclamationTriangle className="status-icon" />
                                    <span className="status-text">{item.reason}</span>
                                </div>
                            </div>
                            <div className="card-content">
                                <div className="item-details-grid">
                                    <div className="detail-item">
                                        <FaBarcode className="detail-icon" />
                                        <div className="detail-content">
                                            <span className="detail-label">Item ID</span>
                                            <span className="detail-value item-id">{item.itemId}</span>
                                        </div>
                                    </div>                                    <div className="detail-item">
                                        <FaCube className="detail-icon" />
                                        <div className="detail-content">
                                            <span className="detail-label">Container</span>
                                            <span className="detail-value container-info">{item.containerId}</span>
                                        </div>
                                    </div>
                                    <div className="detail-item position-detail">
                                        <FaMapMarkerAlt className="detail-icon" />
                                        <div className="detail-content">
                                            <span className="detail-label">Position</span>
                                            <span className="detail-value position-info">
                                                ({item.position.startCoordinates.width}, {item.position.startCoordinates.depth}, {item.position.startCoordinates.height}) → 
                                                ({item.position.endCoordinates.width}, {item.position.endCoordinates.depth}, {item.position.endCoordinates.height})
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>            {/* Top Right Box - Return Plan Controls */}
            <div className="grid-box content-box" id="return-plan-controls">
                <h2 className="section-title">
                    <FaClipboardList className="section-icon" />
                    Generate Return Plan
                </h2>
                <div className="section-content">
                    <div className="form-group">
                        <label htmlFor="undocking-container" className="form-label">Undocking Container ID:</label>
                        <input
                            id="undocking-container"
                            type="text"
                            value={undockingContainer}
                            onChange={(e) => setUndockingContainer(e.target.value)}
                            placeholder="Enter container ID"
                            className="input-field"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="undocking-date" className="form-label">Undocking Date:</label>
                        <input
                            id="undocking-date"
                            type="date"
                            value={undockingDate}
                            onChange={(e) => setUndockingDate(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="max-volume" className="form-label">Max Volume:</label>
                        <input
                            id="max-volume"
                            type="number"
                            value={maxVolume}
                            onChange={(e) => setMaxVolume(parseInt(e.target.value) || 1000)}
                            placeholder="Max volume"
                            className="input-field"
                        />
                    </div>                        
                    <div className="buttons-container">
                        <Button
                            text={generateLoading ? "Generating..." : "Generate Return Plan"}
                            onClick={handleGenerateReturnPlan}
                            className="btn btn-primary"
                            disabled={generateLoading}
                        />
                        <Button
                            text="Export Waste Report"
                            onClick={handleWasteExport}
                            className="btn btn-secondary"
                        />
                    </div>
                </div>
            </div>                  {/* Bottom Right Box - Waste Manifest */}
            <div className="grid-box content-box span-full" id="waste-manifest-section">                    
                <h2 className="section-title">
                    <FaBox className="section-icon" />
                    Waste Return Manifest
                </h2>
                <div className="section-content">
                    {returnPlan ? (
                        <div className="manifest-content">
                            <div className="manifest-header">
                                <h3>Return Manifest</h3>
                                <p><strong>Undocking Container:</strong> {returnPlan.returnManifest.undockingContainerId}</p>
                                <p><strong>Undocking Date:</strong> {new Date(returnPlan.returnManifest.undockingDate).toLocaleDateString()}</p>
                                <p><strong>Total Volume:</strong> {returnPlan.returnManifest.totalVolume}</p>
                                <p><strong>Total Weight:</strong> {returnPlan.returnManifest.totalWeight}</p>
                            </div>
                            
                            <div className="return-items">
                                <h4>Return Items ({returnPlan.returnManifest.returnItems.length})</h4>
                                <div className="items-scroll">
                                    {returnPlan.returnManifest.returnItems.map((item) => (
                                        <div key={item.itemId} className="return-item">
                                            <span className="item-name">{item.name}</span>
                                            <span className="item-id">({item.itemId})</span>
                                            <span className="item-reason">{item.reason}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            
                            {returnPlan.returnPlan && returnPlan.returnPlan.length > 0 && (
                                <div className="return-steps">
                                    <h4>Return Plan ({returnPlan.returnPlan.length} steps)</h4>
                                    <div className="steps-scroll">
                                        {returnPlan.returnPlan.map((step) => (
                                            <div key={step.step} className="plan-step">
                                                <span className="step-number">{step.step}.</span>
                                                <span className="step-text">
                                                    Move {step.itemName} ({step.itemId}) from {step.fromContainer} to {step.toContainer}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p>Generate a return plan to view the waste manifest.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Wastage;