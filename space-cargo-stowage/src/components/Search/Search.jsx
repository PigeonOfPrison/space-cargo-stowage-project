import React, { useState } from "react";
import "./search.css";
import Button from "../Parts/Buttons";

function Search() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [selectedItem, setSelectedItem] = useState(null);
    const [retrievalSteps, setRetrievalSteps] = useState([]);

    // Mock user data (will come from authentication system)
    const mockCurrentUser = {
        id: "USR001",
        name: "John Doe"
    };

    // Function to log retrieval data to database
    const dataLogging = async (retrievalData) => {
        try {
            // TODO: Implement PostgreSQL connection and queries
            /* 
            Expected PostgreSQL table structure:
            CREATE TABLE retrieval_logs (
                log_id SERIAL PRIMARY KEY,
                item_id VARCHAR(10) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                retriever_id VARCHAR(10) NOT NULL,
                retriever_name VARCHAR(100) NOT NULL,
                retrieval_time TIMESTAMP NOT NULL,
                container_id VARCHAR(10) NOT NULL,
                zone VARCHAR(1) NOT NULL,
                coordinates VARCHAR(50) NOT NULL,
                uses INTEGER NOT NULL
            );
            */

            // TODO: Replace with actual PostgreSQL query
            /* 
            const query = `
                INSERT INTO retrieval_logs 
                (item_id, item_name, retriever_id, retriever_name, retrieval_time, container_id, zone, coordinates, uses)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            `;
            */

            console.log('Logging retrieval:', retrievalData);
            return true;
        } catch (error) {
            console.error('Error logging retrieval:', error);
            return false;
        }
    };    // Mock data for items
    const mockItems = [
        { id: 'ITM001', name: 'Emergency Food Pack', containerId: 'C001', containerName: 'Container Alpha', zone: 'A', coordinates: { x: 12, y: 3, z: 0 }, uses: 5 },
        { id: 'ITM002', name: 'Medical Supplies Kit', containerId: 'C002', containerName: 'Container Beta', zone: 'B', coordinates: { x: 5, y: 2, z: 1 }, uses: 10 },
        { id: 'ITM003', name: 'Water Filtration System', containerId: 'C003', containerName: 'Container Gamma', zone: 'A', coordinates: { x: 8, y: 1, z: 2 }, uses: 100 },
        { id: 'ITM004', name: 'Solar Panel Array', containerId: 'C004', containerName: 'Container Delta', zone: 'C', coordinates: { x: 15, y: 4, z: 0 }, uses: 50 },
        { id: 'ITM005', name: 'Oxygen Generator', containerId: 'C001', containerName: 'Container Alpha', zone: 'A', coordinates: { x: 12, y: 4, z: 1 }, uses: 75 },
        { id: 'ITM006', name: 'Communication Device', containerId: 'C005', containerName: 'Container Epsilon', zone: 'B', coordinates: { x: 10, y: 3, z: 2 }, uses: 200 },
        { id: 'ITM007', name: 'Battery Pack', containerId: 'C006', containerName: 'Container Zeta', zone: 'D', coordinates: { x: 3, y: 2, z: 0 }, uses: 30 },
        { id: 'ITM008', name: 'Spare Parts Kit', containerId: 'C002', containerName: 'Container Beta', zone: 'B', coordinates: { x: 5, y: 4, z: 1 }, uses: 15 },
        { id: 'ITM009', name: 'Navigation System', containerId: 'C007', containerName: 'Container Eta', zone: 'C', coordinates: { x: 9, y: 2, z: 2 }, uses: 1000 },
        { id: 'ITM010', name: 'Air Filter Set', containerId: 'C003', containerName: 'Container Gamma', zone: 'A', coordinates: { x: 8, y: 3, z: 0 }, uses: 25 },
        { id: 'ITM011', name: 'Tool Kit', containerId: 'C008', containerName: 'Container Theta', zone: 'D', coordinates: { x: 7, y: 1, z: 1 }, uses: 150 },
        { id: 'ITM012', name: 'First Aid Kit', containerId: 'C004', containerName: 'Container Delta', zone: 'C', coordinates: { x: 15, y: 2, z: 2 }, uses: 20 },
        { id: 'ITM013', name: 'Emergency Beacon', containerId: 'C009', containerName: 'Container Iota', zone: 'B', coordinates: { x: 12, y: 4, z: 0 }, uses: 500 },
        { id: 'ITM014', name: 'Thermal Blanket', containerId: 'C005', containerName: 'Container Epsilon', zone: 'B', coordinates: { x: 10, y: 1, z: 1 }, uses: 40 },
        { id: 'ITM015', name: 'Radiation Shield', containerId: 'C010', containerName: 'Container Kappa', zone: 'A', coordinates: { x: 4, y: 3, z: 2 }, uses: 1000 },
        { id: 'ITM016', name: 'Space Suit', containerId: 'C006', containerName: 'Container Zeta', zone: 'D', coordinates: { x: 3, y: 4, z: 0 }, uses: 100 },
        { id: 'ITM017', name: 'Water Recycler', containerId: 'C011', containerName: 'Container Lambda', zone: 'C', coordinates: { x: 11, y: 2, z: 1 }, uses: 300 },
        { id: 'ITM018', name: 'Power Converter', containerId: 'C007', containerName: 'Container Eta', zone: 'C', coordinates: { x: 9, y: 4, z: 2 }, uses: 250 },
        { id: 'ITM019', name: 'Fuel Cell', containerId: 'C012', containerName: 'Container Mu', zone: 'D', coordinates: { x: 14, y: 3, z: 0 }, uses: 50 },
        { id: 'ITM020', name: 'Life Support Module', containerId: 'C008', containerName: 'Container Theta', zone: 'D', coordinates: { x: 7, y: 3, z: 1 }, uses: 500 }
    ];

    // Mock retrieval steps data
    const mockRetrievalSteps = [
        { step: 1, action: 'Navigate to Zone', details: 'Go to Zone {zone}' },
        { step: 2, action: 'Locate Container', details: 'Find Container {container} at coordinates {coordinates}' },
        { step: 3, action: 'Open Container', details: 'Use access code to open {container}' },
        { step: 4, action: 'Retrieve Item', details: 'Take out {item} from position {coordinates}' },
        { step: 5, action: 'Verify Item', details: 'Confirm item ID: {itemId}' },
        { step: 6, action: 'Close Container', details: 'Secure {container} properly' },
        { step: 7, action: 'Update System', details: 'Mark {item} as retrieved' }
    ];

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (query.trim() === '') {
            setSearchResults([]);
            return;
        }

        // Filter items based on search query
        const results = mockItems.filter(item =>
            item.name.toLowerCase().includes(query.toLowerCase()) ||
            item.id.toLowerCase().includes(query.toLowerCase()) ||
            item.containerId.toLowerCase().includes(query.toLowerCase()) ||
            item.containerName.toLowerCase().includes(query.toLowerCase()) ||
            item.zone.toLowerCase().includes(query.toLowerCase()) ||
            // Search in all coordinate dimensions
            Object.values(item.coordinates).some(coord => coord.toString().includes(query)) ||
            // Search in uses field
            item.uses.toString().includes(query)
        );

        setSearchResults(results);
    };

    // Function to format coordinates for display
    const formatCoordinates = (coords) => {
        return `(${coords.x}, ${coords.y}, ${coords.z})`;
    };

    const handleItemSelect = (item) => {
        setSelectedItem(item);
        // Clear previous retrieval steps
        setRetrievalSteps([]);
    };    const handleRetrieve = async () => {
        if (!selectedItem) return;

        // Generate retrieval steps by replacing placeholders with actual values
        const steps = mockRetrievalSteps.map(step => ({
            ...step,
            details: step.details
                .replace('{zone}', selectedItem.zone)
                .replace('{container}', selectedItem.containerName)
                .replace('{coordinates}', formatCoordinates(selectedItem.coordinates))
                .replace('{item}', selectedItem.name)
                .replace('{itemId}', selectedItem.id)
        }));

        // Create retrieval log data
        const retrievalData = {
            item_id: selectedItem.id,
            item_name: selectedItem.name,
            retriever_id: mockCurrentUser.id,
            retriever_name: mockCurrentUser.name,
            retrieval_time: new Date().toISOString(),
            container_id: selectedItem.containerId,
            zone: selectedItem.zone,
            coordinates: formatCoordinates(selectedItem.coordinates),
            uses: selectedItem.uses
        };

        // Log the retrieval action
        const logged = await dataLogging(retrievalData);
        if (!logged) {
            console.error('Failed to log retrieval action');
            // TODO: Add user feedback for logging failure
        }

        setRetrievalSteps(steps);
    };

    return (
        <div className="search-container">
            <div className="search-grid left-grid">
                <h2>Search Items</h2>
                <div className="search-content">
                    <div className="search-controls">
                        <div className="search-input-container">
                            <input
                                type="text"
                                placeholder="Search items, containers, or locations..."
                                value={searchQuery}
                                onChange={(e) => handleSearch(e.target.value)}
                                className="search-input"
                            />
                        </div>
                    </div>

                    <div className="search-results">
                        {searchResults.length > 0 ? (
                            <div className="results-list">
                                <div className="results-header">
                                    <span>Name</span>
                                    <span>Container</span>
                                    <span>Zone</span>
                                    <span>Uses</span>
                                </div>
                                {searchResults.map(item => (
                                    <button 
                                        key={item.id} 
                                        type="button"
                                        className={`result-item ${selectedItem && selectedItem.id === item.id ? 'selected' : ''}`}
                                        onClick={() => handleItemSelect(item)}
                                        aria-label={`Select ${item.name} in ${item.containerName}, Zone ${item.zone}`}
                                    >
                                        <span className="item-name">{item.name}</span>
                                        <span className="container-info">{item.containerName}</span>
                                        <span className="zone">Zone {item.zone}</span>
                                        <span className="uses">{item.uses}</span>
                                    </button>
                                ))}
                            </div>                        ) : (
                            <>
                                {searchQuery && (
                                    <div className="no-results">No items found</div>
                                )}
                                {!searchQuery && (
                                    <div className="search-prompt">Enter a search term to find items</div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>

            <div className="search-grid right-grid">
                <h2>Item Retrieval</h2>
                <div className="retrieval-content">
                    {selectedItem ? (
                        <>
                            <div className="selected-item-info">
                                <h3>{selectedItem.name}</h3>
                                <p>ID: {selectedItem.id}</p>
                                <p>Location: Zone {selectedItem.zone}, {selectedItem.containerName}</p>
                                <p>Coordinates: {formatCoordinates(selectedItem.coordinates)}</p>
                                <p>Usage Count: {selectedItem.uses}</p>
                                <Button 
                                    text="Retrieve Item"
                                    onClick={handleRetrieve}
                                    className="retrieve-button"
                                />
                            </div>
                            {retrievalSteps.length > 0 && (
                                <div className="retrieval-steps">
                                    <h3>Retrieval Steps</h3>
                                    <div className="steps-list">
                                        {retrievalSteps.map((step) => (
                                            <div key={step.step} className="step-item">
                                                <div className="step-number">{step.step}</div>
                                                <div className="step-content">
                                                    <h4>{step.action}</h4>
                                                    <p>{step.details}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="no-selection">
                            Select an item from the search results to view retrieval options
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Search;