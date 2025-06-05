import React, { useState } from "react";
import "./simulation.css";
import Button from "../Parts/Buttons";

function Simulation() {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedItems, setSelectedItems] = useState([]);
    const [usesPerDay, setUsesPerDay] = useState({});
    const [daysToSimulate, setDaysToSimulate] = useState(1);
    const [searchResults, setSearchResults] = useState([]);
    const [simulationResults, setSimulationResults] = useState([]);

    // Mock items data (replace with database fetch)
    const mockItems = [
        { id: 'ITM001', name: 'Emergency Food Pack', uses_left: 50 },
        { id: 'ITM002', name: 'Medical Supplies Kit', uses_left: 75 },
        { id: 'ITM003', name: 'Water Filtration System', uses_left: 100 },
        { id: 'ITM004', name: 'Oxygen Generator', uses_left: 200 }
    ];

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (query.trim() === '') {
            setSearchResults([]);
            return;
        }

        const results = mockItems.filter(item =>
            item.name.toLowerCase().includes(query.toLowerCase()) ||
            item.id.toLowerCase().includes(query.toLowerCase())
        );
        setSearchResults(results);
    };

    const handleSelectItem = (item) => {
        if (!selectedItems.find(i => i.id === item.id)) {
            setSelectedItems([...selectedItems, item]);
            setUsesPerDay({ ...usesPerDay, [item.id]: 1 });
        }
    };

    const handleUsesChange = (itemId, value) => {
        const uses = Math.max(1, parseInt(value) || 1);
        setUsesPerDay({ ...usesPerDay, [itemId]: uses });
    };

    const handleRemoveItem = (itemId) => {
        setSelectedItems(selectedItems.filter(item => item.id !== itemId));
        const newUsesPerDay = { ...usesPerDay };
        delete newUsesPerDay[itemId];
        setUsesPerDay(newUsesPerDay);
    };    const calculateSimulation = (days) => {
        if (selectedItems.length === 0) {
            setSimulationResults([]);
            return;
        }

        const results = selectedItems.map(item => {            const dailyUses = usesPerDay[item.id] || 0;
            const totalUsage = dailyUses * days;
            const remainingUses = Math.max(0, item.uses_left - totalUsage);
            const daysUntilDepletion = Math.floor(item.uses_left / dailyUses);
            
            let status;
            if (remainingUses === 0) {
                status = 'depleted';
            } else if (remainingUses <= item.uses_left * 0.2) {
                status = 'critical';
            } else if (remainingUses <= item.uses_left * 0.5) {
                status = 'warning';
            } else {
                status = 'good';
            }

            return {
                id: item.id,
                name: item.name,
                initialUses: item.uses_left,
                remainingUses,
                daysUntilDepletion,
                dailyUses,
                status
            };
        });

        setSimulationResults(results);
    };

    const simulateNextDay = () => {
        calculateSimulation(1);
    };

    const simulateXDays = () => {
        calculateSimulation(daysToSimulate);
    };

    return (
        <div className="simulation">            <div className="simulation-grid">
                {/* Top Left Grid - Search and Input */}
                <div className="simulation-grid-box">
                    <h3>Select Items</h3>
                    <div className="search-container">
                        <input
                            type="text"
                            placeholder="Search items..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="search-input"
                        />
                        {searchResults.length > 0 && (
                            <div className="search-results">
                                {searchResults.map(item => (
                                    <button
                                        key={item.id}
                                        onClick={() => handleSelectItem(item)}
                                        className="search-result-item"
                                    >
                                        <strong>{item.name}</strong>
                                        <span>ID: {item.id}</span>
                                        <span>Uses Left: {item.uses_left}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>                
                {/* Top Right Grid - Selected Items */}                
                <div className="simulation-grid-box">
                    <h3>Selected Items</h3>
                    <div className="selected-items-list">
                        {selectedItems.map(item => (
                            <div key={item.id} className="selected-item">                                
                                <div className="simulation-item-info">
                                    <strong>{item.name}</strong>
                                    <span>Uses Left: {item.uses_left}</span>
                                </div>
                                <div className="item-controls">                                    
                                    <label className="uses-label">
                                        <span>Uses per day:</span>
                                        <input
                                            type="number"
                                            min="1"
                                            value={usesPerDay[item.id]}
                                            onChange={(e) => handleUsesChange(item.id, e.target.value)}
                                            className="uses-input"
                                        />
                                    </label>
                                    <button
                                        onClick={() => handleRemoveItem(item.id)}
                                        className="remove-button"
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        ))}
                        {selectedItems.length === 0 && (
                            <div className="no-items">No items selected</div>
                        )}
                    </div>
                </div>

                {/* Bottom Left Grid - Simulation Controls */}                <div className="simulation-grid-box">
                    <h3>Simulation Controls</h3>
                    <div className="simulation-controls">
                        <div className="days-input-container">
                            <label htmlFor="daysInput">Number of days:</label>
                            <input
                                id="daysInput"
                                type="number"
                                min="1"
                                value={daysToSimulate}
                                onChange={(e) => setDaysToSimulate(Math.max(1, parseInt(e.target.value) || 1))}
                                className="days-input"
                            />
                        </div>
                        <div className="control-buttons">
                            <Button
                                text="Next Day"
                                onClick={simulateNextDay}
                                className="control-button"
                            />
                            <Button
                                text={`${daysToSimulate} Days`}
                                onClick={simulateXDays}
                                className="control-button"
                            />
                        </div>
                    </div>
                </div>                {/* Bottom Right Grid - Simulation Results */}                <div className="simulation-grid-box">
                    <h3>Simulation Results</h3>
                    <div className="simulation-results">
                        {simulationResults.length > 0 ? (
                            <div className="results-list">
                                {simulationResults.map(result => (                                    <div key={result.id} className={`result-item ${result.status}`}>
                                        <div className="result-grid">
                                            <div className="result-left-top">
                                                <h4>{result.name}</h4>
                                                <div className="item-id">ID: {result.id}</div>
                                            </div>
                                            <div className="result-left-bottom">
                                                <span className="status-badge">{result.status}</span>
                                                <div className="usage-bar">
                                                    <div 
                                                        className="usage-progress"
                                                        style={{ 
                                                            width: `${(result.remainingUses / result.initialUses) * 100}%`
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                            <div className="result-right">
                                                <div className="detail-row">
                                                    <span>Daily Usage:</span>
                                                    <span>{result.dailyUses} uses/day</span>
                                                </div>
                                                <div className="detail-row">
                                                    <span>Remaining Uses:</span>
                                                    <span>{result.remainingUses} / {result.initialUses}</span>
                                                </div>
                                                <div className="detail-row">
                                                    <span>Days until depletion:</span>
                                                    <span>{result.daysUntilDepletion} days</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="no-results">
                                {selectedItems.length === 0 ? (
                                    <p>Select items and configure usage to see simulation results</p>
                                ) : (
                                    <p>Click "Next Day" or "{daysToSimulate} Days" to run simulation</p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Simulation;