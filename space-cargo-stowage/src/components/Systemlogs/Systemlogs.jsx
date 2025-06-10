import React, { useState, useEffect } from "react";
import "../../styles/systemlogs1.css";  // New Design System (was "./systemlogs.css")
import { useToast } from '../Toast/Toast';
import { ClimbingBoxLoader } from 'react-spinners';
import { 
    FaSearch, 
    FaFilter, 
    FaCalendarAlt, 
    FaUser, 
    FaBox, 
    FaCog, 
    FaTrashAlt,
    FaArrowRight,
    FaArrowLeft,
    FaExchangeAlt,
    FaClock,
    FaFileAlt
} from 'react-icons/fa';
import { 
    getSomeLogsWithFallback, 
    getSystemLogsWithFallback, 
    formatTimestamp,
    getActionTypeColor,
    getActionTypeIcon
} from './systemlogsApi';

function Systemlogs() {
    const [logs, setLogs] = useState([]);
    const [filteredLogs, setFilteredLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // Search and filter states
    const [searchQuery, setSearchQuery] = useState('');
    const [dateFilter, setDateFilter] = useState({
        startDate: '',
        endDate: ''
    });
    const [actionTypeFilter, setActionTypeFilter] = useState('');
    const [userIdFilter, setUserIdFilter] = useState('');
    const [itemIdFilter, setItemIdFilter] = useState('');
    
    const { success, warning, error: showError } = useToast();

    // Load initial logs on component mount
    useEffect(() => {
        loadInitialLogs();
    }, []);

    // Apply filters whenever search criteria change
    useEffect(() => {
        applyFilters();
    }, [logs, searchQuery, dateFilter, actionTypeFilter, userIdFilter, itemIdFilter]);

    const loadInitialLogs = async () => {
        setLoading(true);
        try {
            const result = await getSomeLogsWithFallback(50);
              if (result.success) {
                setLogs(result.logs);
                
                if (result.isMockData) {
                    warning(`Loaded ${result.logs.length} mock system log entries (Backend unavailable)`);
                } else {
                    success(`Loaded ${result.logs.length} system log entries`);
                }
            }
        } catch (error) {
            console.error('Error loading initial logs:', error);
            showError('Failed to load system logs');
            setLogs([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery && !dateFilter.startDate && !dateFilter.endDate && 
            !actionTypeFilter && !userIdFilter && !itemIdFilter) {
            // If no filters, reload initial logs
            await loadInitialLogs();
            return;
        }

        setLoading(true);
        try {
            const filters = {};
            
            if (dateFilter.startDate) filters.startDate = dateFilter.startDate;
            if (dateFilter.endDate) filters.endDate = dateFilter.endDate;
            if (actionTypeFilter) filters.actionType = actionTypeFilter;
            if (userIdFilter) filters.userId = userIdFilter;
            if (itemIdFilter) filters.itemId = itemIdFilter;

            const result = await getSystemLogsWithFallback(filters);
              if (result.success) {
                setLogs(result.logs);
                
                if (result.isMockData) {
                    warning(`Found ${result.logs.length} mock log entries (Backend unavailable)`);
                } else {
                    success(`Found ${result.logs.length} log entries`);
                }
            }
        } catch (error) {
            console.error('Error searching logs:', error);
            showError('Failed to search system logs');
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        let filtered = [...logs];

        // Apply text search across multiple fields
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            filtered = filtered.filter(log => 
                log.itemId.toLowerCase().includes(query) ||
                log.userId.toLowerCase().includes(query) ||
                log.actionType.toLowerCase().includes(query) ||
                log.details.reason.toLowerCase().includes(query) ||
                (log.details.fromContainer && log.details.fromContainer.toLowerCase().includes(query)) ||
                (log.details.toContainer && log.details.toContainer.toLowerCase().includes(query))
            );
        }

        setFilteredLogs(filtered);
    };

    const clearAllFilters = () => {
        setSearchQuery('');
        setDateFilter({ startDate: '', endDate: '' });
        setActionTypeFilter('');
        setUserIdFilter('');
        setItemIdFilter('');
        loadInitialLogs();
    };    const renderActionDetails = (log) => {
        const { actionType, details } = log;
        
        switch (actionType) {
            case 'placement':
                return (
                    <span className="movement-details">
                        <FaArrowRight className="movement-icon" /> {details.toContainer}
                    </span>
                );
            case 'retrieval':
                return (
                    <span className="movement-details">
                        {details.fromContainer} <FaArrowLeft className="movement-icon" />
                    </span>
                );
            case 'rearrangement':
                return (
                    <span className="movement-details">
                        {details.fromContainer} <FaExchangeAlt className="movement-icon" /> {details.toContainer}
                    </span>
                );
            case 'disposal':
                return (
                    <span className="movement-details">
                        {details.fromContainer} <FaTrashAlt className="movement-icon disposal-icon" />
                    </span>
                );
            default:
                return '';
        }
    };
      if (loading) {
        return (
            <div className="loading-screen" id="systemlogs-loading">
                <ClimbingBoxLoader 
                    color="#4f46e5" 
                    size={15}
                    speedMultiplier={0.8}
                />
                <p>Loading system logs...</p>
            </div>
        );
    }    return (        
        <div className="main-container grid-container grid-single" id="systemlogs-page">
            <div className="grid-box content-box" id="logs-section">
                <h2 className="section-title">
                    <FaFileAlt className="section-icon" />
                    System Logs
                </h2>

                {/* Search and Filter Section */}
                <div className="section-content">
                    <div className="filters-container" id="logs-filters">
                        <div className="form-row">
                            <div className="form-group search-group">
                                <FaSearch className="input-icon" />
                                <input
                                    type="text"
                                    placeholder="Search logs (Item ID, User ID, Action, Reason, Container)..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="input-field search-input"
                                    id="logs-search-input"
                                />
                            </div>
                            
                            <div className="date-filters">
                                <div className="date-input-group">
                                    <FaCalendarAlt className="input-icon" />
                                    <input
                                        type="date"
                                        value={dateFilter.startDate}
                                        onChange={(e) => setDateFilter(prev => ({ ...prev, startDate: e.target.value }))}
                                        className="input-field"
                                        placeholder="Start Date"
                                    />
                                </div>
                                <div className="date-input-group">
                                    <FaCalendarAlt className="input-icon" />
                                    <input
                                        type="date"
                                        value={dateFilter.endDate}
                                        onChange={(e) => setDateFilter(prev => ({ ...prev, endDate: e.target.value }))}
                                        className="input-field"
                                        placeholder="End Date"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="select-group">
                                <FaFilter className="input-icon" />
                                <select
                                    value={actionTypeFilter}
                                    onChange={(e) => setActionTypeFilter(e.target.value)}
                                    className="select-field"
                                >
                                    <option value="">All Actions</option>
                                    <option value="placement">Placement</option>
                                    <option value="retrieval">Retrieval</option>
                                    <option value="rearrangement">Rearrangement</option>
                                    <option value="disposal">Disposal</option>
                                </select>
                            </div>

                            <div className="input-group">
                                <FaUser className="input-icon" />
                                <input
                                    type="text"
                                    placeholder="User ID"
                                    value={userIdFilter}
                                    onChange={(e) => setUserIdFilter(e.target.value)}
                                    className="input-field"
                                />
                            </div>

                            <div className="input-group">
                                <FaBox className="input-icon" />
                                <input
                                    type="text"
                                    placeholder="Item ID"
                                    value={itemIdFilter}
                                    onChange={(e) => setItemIdFilter(e.target.value)}
                                    className="input-field"
                                />
                            </div>

                            <button onClick={handleSearch} className="btn btn-primary">
                                <FaSearch />
                                Search
                            </button>
                            
                            <button onClick={clearAllFilters} className="btn btn-secondary">
                                <FaCog />
                                Clear All
                            </button>
                        </div>
                    </div>                    {/* Results Summary */}
                    <div className="results-summary" id="logs-summary">
                        <p>
                            <FaFileAlt className="summary-icon" />
                            Showing {filteredLogs.length} of {logs.length} log entries
                            {searchQuery && <span> (filtered by: "{searchQuery}")</span>}
                        </p>
                    </div>

                    {/* Logs Table */}
                    <div className="data-table-container" id="logs-table-container">
                        <div className="data-table">
                            <div className="data-table-header">
                                <span><FaClock /> Time</span>
                                <span><FaCog /> Action</span>
                                <span><FaUser /> User ID</span>
                                <span><FaBox /> Item ID</span>
                                <span><FaArrowRight /> Movement</span>
                                <span><FaFileAlt /> Reason</span>
                            </div>
                            
                            <div className="data-table-body">
                                {filteredLogs.length > 0 ? (
                                    filteredLogs.map((log, index) => (
                                        <div key={`${log.timestamp}-${index}`} className="data-row">
                                            <span className="log-timestamp">
                                                {formatTimestamp(log.timestamp)}
                                            </span>
                                              <span className="log-action">
                                                <span 
                                                    className="status-badge"
                                                    style={{ backgroundColor: getActionTypeColor(log.actionType) }}
                                                >
                                                    {React.createElement(getActionTypeIcon(log.actionType), { 
                                                        style: { marginRight: '6px', fontSize: '14px' } 
                                                    })}
                                                    {log.actionType}
                                                </span>
                                            </span>
                                            
                                            <span className="log-user-id">{log.userId}</span>
                                            
                                            <span className="log-item-id">{log.itemId}</span>
                                            
                                            <span className="log-movement">
                                                {renderActionDetails(log)}
                                            </span>
                                            
                                            <span className="log-reason">{log.details.reason}</span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="no-results">
                                        {logs.length === 0 ? (
                                            <p>No system logs found</p>
                                        ) : (
                                            <p>No logs match the current filters</p>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Systemlogs;