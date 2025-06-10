import React, { useState, useEffect, useRef } from "react";
import "../../styles/search1.css";  // New Design System (was "./search.css")
import Button from "../Parts/Buttons";
import { useToast } from '../Toast/Toast';
import { searchItems, retrieveItemSteps, formatCoordinates } from './searchApi';
import { ClimbingBoxLoader } from 'react-spinners';
import { FaSearch, FaBrain, FaBox } from 'react-icons/fa';

function Search() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [selectedItem, setSelectedItem] = useState(null);
    const [retrievalSteps, setRetrievalSteps] = useState([]);
    const [searchLoading, setSearchLoading] = useState(false);
    const { success, error: showError, info } = useToast();
    const searchTimeoutRef = useRef(null);
      const handleSearch = async (query) => {
        setSearchQuery(query);
        
        // Clear previous timeout
        if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current);
        }
        
        // If query is empty, clear results immediately
        if (!query.trim()) {
            setSearchResults([]);
            setSearchLoading(false);
            return;
        }
        
        // Show loading state
        setSearchLoading(true);
        
        // Debounce the search with 300ms delay
        searchTimeoutRef.current = setTimeout(async () => {
            try {
                const results = await searchItems(query, {
                    onSuccess: success,
                    onError: showError,
                    onInfo: info
                });
                
                setSearchResults(results);
            } finally {
                setSearchLoading(false);
            }
        }, 300);
    };
    
    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (searchTimeoutRef.current) {
                clearTimeout(searchTimeoutRef.current);
            }
        };
    }, []);const handleItemSelect = (item) => {
        setSelectedItem(item);
        // Clear previous retrieval steps
        setRetrievalSteps([]);
    };
    
    const handleRetrieve = async () => {
        if (!selectedItem) return;

        const steps = await retrieveItemSteps(selectedItem, {
            onSuccess: success,
            onError: showError,
            onInfo: info
        });
        
        setRetrievalSteps(steps);
    };
      return (
        <div className="main-container grid-container grid-2x1" id="search-page">
            <div className="grid-box content-box" id="search-section">
                <h2 className="section-title">Search Items</h2>
                <div className="section-content">                      <div className="search-controls">
                        <div className="input-container">
                            <input
                                type="text"
                                placeholder="Search items, containers, or locations..."
                                value={searchQuery}
                                onChange={(e) => handleSearch(e.target.value)}
                                className="input-field search-input"
                                id="search-input-field"
                            />
                        </div>
                    </div>                    
                    <div className="search-results">
                        {searchLoading ? (
                            <div className="loading-container">
                                <ClimbingBoxLoader color="#0f766e" size={20} speedMultiplier={0.8} />
                            </div>
                        ) : (
                            <>
                                {searchResults.length > 0 ? (
                                    <div className="data-table-container">
                                        <div className="data-table-header">
                                            <span>Name</span>
                                            <span>Container</span>
                                            <span>Zone</span>
                                            <span>Uses</span>
                                        </div>                                
                                        {searchResults.map(item => (
                                            <button 
                                                key={item.itemId || item.id} 
                                                type="button"
                                                className={`btn data-row ${selectedItem && (selectedItem.itemId || selectedItem.id) === (item.itemId || item.id) ? 'is-active' : ''}`}
                                                onClick={() => handleItemSelect(item)}
                                                aria-label={`Select ${item.name} in ${item.container || item.containerName}, Zone ${item.preferredZone || item.zone}`}
                                            >
                                                <span className="item-name">{item.name}</span>
                                                <span className="container-info">{item.container || item.containerName}</span>
                                                <span className="zone-info">Zone {item.preferredZone || item.zone}</span>
                                                <span className="usage-info">{item.usageLimit || item.uses}</span>
                                            </button>
                                        ))}
                                    </div>                                ) : (
                                    <>
                                        {searchQuery && (
                                            <div className="no-results">
                                                <FaSearch className="empty-state-icon" />
                                                <span>No items found</span>
                                            </div>
                                        )}
                                        {!searchQuery && (
                                            <div className="search-prompt">
                                                <FaBrain className="empty-state-icon" />
                                                <span>Enter a search term to find items</span>
                                            </div>
                                        )}
                                    </>                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-box content-box" id="retrieval-section">
                <h2 className="section-title">Item Retrieval</h2>
                <div className="section-content">
                    {selectedItem ? (
                        <>                            
                            <div className="item-details">
                                <h3 className="item-title">{selectedItem.name}</h3>
                                <p>ID: {selectedItem.itemId || selectedItem.id}</p>
                                <p>Container: {selectedItem.container || selectedItem.containerName}</p>
                                <p>Preferred Zone: {selectedItem.preferredZone || selectedItem.zone}</p>
                                {selectedItem.coordinates && (
                                    <p>Coordinates: {formatCoordinates(selectedItem.coordinates)}</p>
                                )}
                                {/* Only show dimensions if they exist (from API data) */}
                                {(selectedItem.width && selectedItem.depth && selectedItem.height) && (
                                    <p>Dimensions: {selectedItem.width} x {selectedItem.depth} x {selectedItem.height} cm</p>
                                )}
                                {/* Only show priority if it exists (from API data) */}
                                {selectedItem.priority && (
                                    <p>Priority: {selectedItem.priority}</p>
                                )}
                                {/* Only show expiry date if it exists (from API data) */}
                                {selectedItem.expiryDate && (
                                    <p>Expiry: {new Date(selectedItem.expiryDate).toLocaleDateString()}</p>
                                )}
                                <p>Usage Limit: {selectedItem.usageLimit || selectedItem.uses}</p>
                                <Button 
                                    text="Retrieve Item"
                                    onClick={handleRetrieve}
                                    className="btn btn-primary"
                                />
                            </div>
                            {retrievalSteps.length > 0 && (
                                <div className="retrieval-steps">
                                    <h3 className="section-title">Retrieval Steps</h3>
                                    <div className="steps-list">                                        
                                        {retrievalSteps.map((step) => (
                                            <div key={step.step} className="step-item">
                                                <div className="step-number">{step.step}</div>
                                                <div className="step-content">
                                                    <h4>{step.action.charAt(0).toUpperCase() + step.action.slice(1)}</h4>
                                                    <p>{step.itemName} (ID: {step.itemId})</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>                    ) : (
                        <div className="no-selection">
                            <FaBox className="empty-state-icon" />
                            <span>Select an item from the search results to view retrieval options</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Search;