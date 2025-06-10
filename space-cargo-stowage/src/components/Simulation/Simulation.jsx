import React, { useState } from "react";
import "../../styles/simulation1.css";  // New Design System (was "./simulation.css")
import Button from "../Parts/Buttons";
import { useToast } from '../Toast/Toast';
import { getItemsForSimulation, getSimulationResults } from './simulationApi';
import { FaSearch, FaListUl, FaCog, FaChartLine, FaPlus, FaTimes, FaPlay, FaCalendarDay, FaClock, FaExclamationTriangle, FaCheckCircle, FaBatteryEmpty } from 'react-icons/fa';

// Mock items data as fallback for when backend connection fails
const mockItems = [
    { itemId: "MOCK001", id: "MOCK001", name: "Water Bottle", usageLimit: 10, category: "Consumables" },
    { itemId: "MOCK002", id: "MOCK002", name: "Energy Bar", usageLimit: 5, category: "Food" },
    { itemId: "MOCK003", id: "MOCK003", name: "Medical Kit", usageLimit: 3, category: "Medical" },
    { itemId: "MOCK004", id: "MOCK004", name: "Oxygen Tank", usageLimit: 20, category: "Life Support" },
    { itemId: "MOCK005", id: "MOCK005", name: "Food Ration", usageLimit: 7, category: "Food" },
    { itemId: "MOCK006", id: "MOCK006", name: "Tool Kit", usageLimit: 15, category: "Equipment" },
    { itemId: "MOCK007", id: "MOCK007", name: "Battery Pack", usageLimit: 12, category: "Power" },
    { itemId: "MOCK008", id: "MOCK008", name: "Communication Device", usageLimit: 8, category: "Electronics" },
    { itemId: "MOCK009", id: "MOCK009", name: "Emergency Blanket", usageLimit: 4, category: "Safety" },
    { itemId: "MOCK010", id: "MOCK010", name: "Water Purification Tablet", usageLimit: 25, category: "Consumables" }
];

// Mock simulation function as fallback for when backend connection fails
const generateMockSimulationResults = (selectedItems, numOfDays) => {
    const currentDate = new Date();
    const newDate = new Date(currentDate.getTime() + (numOfDays * 24 * 60 * 60 * 1000));
    
    // Simulate random usage, expiration, and depletion
    const itemsUsed = selectedItems.map(item => ({
        itemId: item.itemId || item.id,
        name: item.name,
        remainingUses: Math.max(0, (item.usageLimit || 10) - Math.floor(Math.random() * 3) - numOfDays)
    })).filter(item => item.remainingUses > 0);
    
    const itemsExpired = selectedItems.filter(() => Math.random() < 0.2).map(item => ({
        itemId: item.itemId || item.id,
        name: item.name
    }));
    
    const itemsDepletedToday = selectedItems.filter(() => Math.random() < 0.1).map(item => ({
        itemId: item.itemId || item.id,
        name: item.name
    }));
    
    return {
        success: true,
        newDate: newDate.toISOString(),
        changes: {
            itemsUsed,
            itemsExpired,
            itemsDepletedToday
        }
    };
};

// Helper function to process and display simulation results
const processSimulationResults = (response, numOfDays, isMockData = false) => {
    const prefix = isMockData ? 'Mock simulation' : 'Simulation';
    const suffix = isMockData ? ' (Backend unavailable)' : '';
    
    const depletedItems = response.changes.itemsDepletedToday?.length || 0;
    const expiredItems = response.changes.itemsExpired?.length || 0;
    
    if (depletedItems > 0) {
        return {
            type: 'warning',
            message: `${prefix} complete: ${depletedItems} item${depletedItems > 1 ? 's' : ''} depleted${suffix}`
        };
    }
    
    if (expiredItems > 0) {
        return {
            type: isMockData ? 'warning' : 'info',
            message: `${prefix} complete: ${expiredItems} item${expiredItems > 1 ? 's' : ''} expired${suffix}`
        };
    }
    
    return {
        type: isMockData ? 'warning' : 'success',
        message: `${prefix} complete for ${numOfDays} day${numOfDays > 1 ? 's' : ''}${suffix}`
    };
};

function Simulation() {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedItems, setSelectedItems] = useState([]);
    const [daysToSimulate, setDaysToSimulate] = useState(1);
    const [searchResults, setSearchResults] = useState([]);
    const [simulationResults, setSimulationResults] = useState(null);
    const [loading, setLoading] = useState(false);    
    const { success, info, warning, error: showError } = useToast();    
    // Handle search with API integration and fallback to mock data
    const handleSearch = async (query) => {
        setSearchQuery(query);
        if (query.trim() === '') {
            setSearchResults([]);
            return;
        }

        try {
            const results = await getItemsForSimulation({
                itemName: query,
                limit: 20
            });
            
            setSearchResults(results || []);
            if (results && results.length > 0) {
                info(`Found ${results.length} item${results.length > 1 ? 's' : ''}`);
            } else {
                info('No items found');
            }
        } catch (error) {
            console.error('Search failed, falling back to mock data:', error);
            
            // Fallback to mock data when API fails
            const filteredMockItems = mockItems.filter(item => 
                item.name.toLowerCase().includes(query.toLowerCase()) ||
                item.category.toLowerCase().includes(query.toLowerCase())
            );
            
            setSearchResults(filteredMockItems);
            if (filteredMockItems.length > 0) {
                warning(`Backend unavailable. Showing ${filteredMockItems.length} mock item${filteredMockItems.length > 1 ? 's' : ''}`);
            } else {
                info('No mock items found matching your search');
            }
        }
    };
    
    const handleSelectItem = (item) => {
        const itemId = item.itemId || item.id;
        if (!selectedItems.find(i => (i.itemId || i.id) === itemId)) {
            setSelectedItems([...selectedItems, item]);
            success(`Added ${item.name} to simulation`);
        } else {
            info(`${item.name} is already selected`);
        }
    };    
    const handleRemoveItem = (itemId) => {
        const item = selectedItems.find(i => (i.itemId || i.id) === itemId);
        setSelectedItems(selectedItems.filter(item => (item.itemId || item.id) !== itemId));
        
        if (item) {
            info(`Removed ${item.name} from simulation`);
        }
    };    
    const runSimulation = async (numOfDays) => {
        if (selectedItems.length === 0) {
            warning('Please select items before running simulation');
            return;
        }

        setLoading(true);
        try {
            const requestBody = {
                numOfDays: numOfDays,
                itemsToBeUsedPerDay: selectedItems.map(item => ({
                    itemId: item.itemId || item.id,
                    name: item.name
                }))
            };

            const response = await getSimulationResults(requestBody);
              if (response.success) {
                setSimulationResults(response);
                const result = processSimulationResults(response, numOfDays, false);
                
                if (result.type === 'success') success(result.message);
                else if (result.type === 'info') info(result.message);
                else warning(result.message);
            } else {
                showError('Simulation failed');
            }        
        } catch (error) {
            console.error('Simulation error, falling back to mock simulation:', error);
            
            // Fallback to mock simulation when API fails
            const mockResponse = generateMockSimulationResults(selectedItems, numOfDays);
            setSimulationResults(mockResponse);
            
            // Show simulation results summary with warning about mock data
            const result = processSimulationResults(mockResponse, numOfDays, true);
            warning(result.message);
        } 
        finally {
            setLoading(false);
        }
    };    
    const simulateNextDay = () => {
        runSimulation(1);
    };    const simulateXDays = () => {
        runSimulation(daysToSimulate);
    };    
      return (
        <div className="main-container grid-container grid-2x2" id="simulation-page">            {/* Top Left Grid - Search and Input */}
            <div className="grid-box content-box" id="items-selection-section">
                <h3 className="section-title">
                    <FaSearch className="section-icon" />
                    Select Items
                </h3>
                <div className="section-content">
                    <div className="search-container">
                        <FaSearch className="search-icon" />
                        <input
                            type="text"
                            placeholder="Search items..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="input-field search-input"
                            id="simulation-search-input"
                        />
                    </div>
                    {searchResults.length > 0 && (
                        <div className="search-results">
                            {searchResults.map(item => (                                <button
                                    key={item.itemId || item.id}
                                    onClick={() => handleSelectItem(item)}
                                    className="btn search-result-item"
                                >
                                    <div className="item-content">
                                        <div className="item-header">
                                            <FaPlus className="add-icon" />
                                            <strong className="item-name">{item.name}</strong>
                                        </div>
                                        <div className="item-details">
                                            <span className="item-id">ID: {item.itemId || item.id}</span>
                                        </div>
                                    </div>
                                    {item.usageLimit && <span className="usage-limit">Usage Limit: {item.usageLimit}</span>}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>            
            
            {/* Top Right Grid - Selected Items */}                
            <div className="grid-box content-box" id="selected-items-section">
                <h3 className="section-title">
                    <FaListUl className="section-icon" />
                    Selected Items
                </h3>
                <div className="section-content">                    
                    {selectedItems.map(item => (
                        <div key={item.itemId || item.id} className="card selected-item">                                
                            <div className="card-content">
                                <div className="item-info">
                                    <div className="item-header">
                                        <strong className="item-name">{item.name}</strong>
                                        <button
                                            onClick={() => handleRemoveItem(item.itemId || item.id)}
                                            className="btn btn-icon remove-btn"
                                            title="Remove item"
                                        >
                                            <FaTimes />
                                        </button>
                                    </div>
                                    <div className="item-details">
                                        <span className="item-id">ID: {item.itemId || item.id}</span>
                                        {item.usageLimit && <span className="usage-limit">Usage Limit: {item.usageLimit}</span>}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                    {selectedItems.length === 0 && (
                        <div className="no-items">
                            <FaListUl className="empty-icon" />
                            <p>No items selected</p>
                        </div>
                    )}
                </div>
            </div>            {/* Bottom Left Grid - Simulation Controls */}                
            <div className="grid-box content-box" id="simulation-controls-section">
                <h3 className="section-title">
                    <FaCog className="section-icon" />
                    Simulation Controls
                </h3>
                <div className="section-content">
                    <div className="form-group">
                        <label htmlFor="simulation-daysInput" className="form-label">
                            <FaCalendarDay className="label-icon" />
                            Number of days:
                        </label>
                        <input
                            id="simulation-daysInput"
                            type="number"
                            min="1"
                            value={daysToSimulate}
                            onChange={(e) => setDaysToSimulate(Math.max(1, parseInt(e.target.value) || 1))}
                            className="input-field"
                        />
                    </div>
                    <div className="buttons-container">
                        <Button
                            text={
                                <span className="button-content">
                                    {loading ? <FaClock className="spin" /> : <FaPlay />}
                                    {loading ? "Running..." : "Next Day"}
                                </span>
                            }
                            onClick={simulateNextDay}
                            className="btn btn-primary"
                            disabled={loading}
                        />
                        <Button
                            text={
                                <span className="button-content">
                                    {loading ? <FaClock className="spin" /> : <FaCalendarDay />}
                                    {loading ? "Running..." : `${daysToSimulate} Days`}
                                </span>
                            }
                            onClick={simulateXDays}
                            className="btn btn-primary"
                            disabled={loading}
                        />
                    </div>
                </div>
            </div>            {/* Bottom Right Grid - Simulation Results */}                
            <div className="grid-box content-box" id="simulation-results-section">
                <h3 className="section-title">
                    <FaChartLine className="section-icon" />
                    Simulation Results
                </h3>
                <div className="section-content">
                    {simulationResults ? (
                        <div className="results-content">
                            <div className="results-header">
                                <h4>Simulation Complete</h4>
                                <p><strong>New Date:</strong> {new Date(simulationResults.newDate).toLocaleDateString()}</p>
                            </div>
                            
                            {/* Items Used Section */}
                            {simulationResults.changes.itemsUsed && simulationResults.changes.itemsUsed.length > 0 && (
                                <div className="results-section">
                                    <h5>
                                        <FaCheckCircle className="section-icon used" />
                                        Items Used ({simulationResults.changes.itemsUsed.length})
                                    </h5>
                                    <div className="items-scroll">
                                        {simulationResults.changes.itemsUsed.map(item => (
                                            <div key={item.itemId} className="result-item item-used">
                                                <div className="item-info">
                                                    <span className="item-name">{item.name}</span>
                                                    <span className="item-id">({item.itemId})</span>
                                                </div>
                                                <span className="remaining-uses">Remaining: {item.remainingUses}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Items Expired Section */}
                            {simulationResults.changes.itemsExpired && simulationResults.changes.itemsExpired.length > 0 && (
                                <div className="results-section">
                                    <h5>
                                        <FaExclamationTriangle className="section-icon expired" />
                                        Items Expired ({simulationResults.changes.itemsExpired.length})
                                    </h5>
                                    <div className="items-scroll">
                                        {simulationResults.changes.itemsExpired.map(item => (
                                            <div key={item.itemId} className="result-item item-expired">
                                                <div className="item-info">
                                                    <span className="item-name">{item.name}</span>
                                                    <span className="item-id">({item.itemId})</span>
                                                </div>
                                                <span className="status-badge variant-error">EXPIRED</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                            {/* Items Depleted Section */}
                            {simulationResults.changes.itemsDepletedToday && simulationResults.changes.itemsDepletedToday.length > 0 && (
                                <div className="results-section">
                                    <h5>
                                        <FaBatteryEmpty className="section-icon depleted" />
                                        Items Depleted Today ({simulationResults.changes.itemsDepletedToday.length})
                                    </h5>
                                    <div className="items-scroll">
                                        {simulationResults.changes.itemsDepletedToday.map(item => (
                                            <div key={item.itemId} className="result-item item-depleted">
                                                <div className="item-info">
                                                    <span className="item-name">{item.name}</span>
                                                    <span className="item-id">({item.itemId})</span>
                                                </div>
                                                <span className="status-badge variant-warning">DEPLETED</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="no-results">
                            <FaChartLine className="empty-icon" />
                            {selectedItems.length === 0 ? (
                                <p>Select items and run simulation to see results</p>
                            ) : (
                                <p>Click "Next Day" or "{daysToSimulate} Days" to run simulation</p>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Simulation;