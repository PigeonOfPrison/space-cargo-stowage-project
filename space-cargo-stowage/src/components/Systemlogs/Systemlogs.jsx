import React, { useState, useEffect } from "react";
import "./systemlogs.css";

function Systemlogs() {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Function to fetch logs from PostgreSQL database
    const fetchLogs = async () => {
        try {
            // TODO: Replace with actual PostgreSQL query
            // For now, using mock data in the same format as dataLogging
            const mockLogs = [
                {
                    log_id: 1,
                    item_id: 'ITM001',
                    item_name: 'Emergency Food Pack',
                    retriever_id: 'USR001',
                    retriever_name: 'John Doe',
                    retrieval_time: '2025-06-02T10:30:00Z',
                    container_id: 'C001',
                    zone: 'A',
                    coordinates: '(12, 3, 0)',
                    uses: 5
                },
                {
                    log_id: 2,
                    item_id: 'ITM015',
                    item_name: 'Radiation Shield',
                    retriever_id: 'USR002',
                    retriever_name: 'Jane Smith',
                    retrieval_time: '2025-06-02T09:15:00Z',
                    container_id: 'C010',
                    zone: 'A',
                    coordinates: '(4, 3, 2)',
                    uses: 1000
                }
                // More logs will come from database
            ];

            setLogs(mockLogs);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching logs:', error);
            setError('Failed to fetch system logs');
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    // Function to format date for display
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(date);
    };

    if (loading) return <div className="systemlogs-loading">Loading logs...</div>;
    if (error) return <div className="systemlogs-error">{error}</div>;

    return (
        <div className="systemlogs">
            <h2>System Logs</h2>
            <div className="logs-container">
                <div className="logs-header">
                    <span>Time</span>
                    <span>User</span>
                    <span>Item</span>
                    <span>Location</span>
                    <span>Uses</span>
                </div>
                <div className="logs-list">
                    {logs.map((log) => (
                        <div key={log.log_id} className="log-item">
                            <span className="log-time">{formatDate(log.retrieval_time)}</span>
                            <span className="log-user">{log.retriever_name}</span>
                            <span className="log-item-name">
                                <strong>{log.item_name}</strong>
                                <small>{log.item_id}</small>
                            </span>                            <span className="log-location">
                                Zone {log.zone}
                            </span>
                            <span className="log-uses">{log.uses}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Systemlogs;