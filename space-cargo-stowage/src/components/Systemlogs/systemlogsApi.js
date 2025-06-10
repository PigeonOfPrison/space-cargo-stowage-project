import axios from "axios";
import { 
    MdAdd, 
    MdGetApp, 
    MdSwapHoriz, 
    MdDelete
} from "react-icons/md";

const API_URL = "http://localhost:8000";

export async function getSomeLogs(limit = 50) {
    try {
        const response = await axios.get(`${API_URL}/api/logs/some-logs`, {
            params: { limit }
        });
        
        if (response.status === 200) {
            return response.data.logs;
        } else {
            throw new Error("Failed to fetch system logs");
        }
    } catch (error) {
        console.error("Error fetching system logs:", error);
        throw error;
    }
}

export async function getSystemLogs(filters = {}) {
    try {
        const response = await axios.get(`${API_URL}/api/logs`, {
            params: {
                startDate: filters.startDate,
                endDate: filters.endDate,
                itemId: filters.itemId,
                userId: filters.userId,
                actionType: filters.actionType
            }
        });
        
        if (response.status === 200) {
            return response.data.logs;
        } else {
            throw new Error("Failed to fetch system logs");
        }
    } catch (error) {
        console.error("Error fetching system logs:", error);
        throw error;
    }
}

// Mock data for fallback
const mockSystemLogs = [
    {
        timestamp: "2025-06-06T10:30:00Z",
        userId: "USR001",
        actionType: "placement",
        itemId: "ITM001",
        details: {
            fromContainer: null,
            toContainer: "C001",
            reason: "Initial stowage"
        }
    },
    {
        timestamp: "2025-06-06T09:15:00Z",
        userId: "USR002",
        actionType: "retrieval",
        itemId: "ITM015",
        details: {
            fromContainer: "C010",
            toContainer: null,
            reason: "Mission requirement"
        }
    },
    {
        timestamp: "2025-06-06T08:45:00Z",
        userId: "USR003",
        actionType: "rearrangement",
        itemId: "ITM007",
        details: {
            fromContainer: "C005",
            toContainer: "C003",
            reason: "Optimization"
        }
    },
    {
        timestamp: "2025-06-05T16:20:00Z",
        userId: "USR001",
        actionType: "disposal",
        itemId: "ITM025",
        details: {
            fromContainer: "C007",
            toContainer: null,
            reason: "Expired item"
        }
    },
    {
        timestamp: "2025-06-05T14:10:00Z",
        userId: "USR004",
        actionType: "placement",
        itemId: "ITM032",
        details: {
            fromContainer: null,
            toContainer: "C012",
            reason: "New cargo arrival"
        }
    },
    {
        timestamp: "2025-06-05T12:30:00Z",
        userId: "USR002",
        actionType: "retrieval",
        itemId: "ITM009",
        details: {
            fromContainer: "C002",
            toContainer: null,
            reason: "Emergency use"
        }
    },
    {
        timestamp: "2025-06-05T11:45:00Z",
        userId: "USR005",
        actionType: "rearrangement",
        itemId: "ITM018",
        details: {
            fromContainer: "C008",
            toContainer: "C004",
            reason: "Weight distribution"
        }
    },
    {
        timestamp: "2025-06-05T10:15:00Z",
        userId: "USR003",
        actionType: "placement",
        itemId: "ITM041",
        details: {
            fromContainer: null,
            toContainer: "C015",
            reason: "Routine stowage"
        }
    }
];

// Generate more mock logs with random data
const generateRandomMockLogs = (count = 50) => {
    const actionTypes = ["placement", "retrieval", "rearrangement", "disposal"];
    const userIds = ["USR001", "USR002", "USR003", "USR004", "USR005"];
    const containerIds = ["C001", "C002", "C003", "C004", "C005", "C007", "C008", "C010", "C012", "C015"];
    const reasons = [
        "Mission requirement", "Emergency use", "Routine stowage", "Optimization",
        "Weight distribution", "Expired item", "New cargo arrival", "Initial stowage",
        "Maintenance", "Safety check", "Inventory update", "Space optimization"
    ];

    const logs = [...mockSystemLogs];
    
    for (let i = logs.length; i < count; i++) {
        const actionType = actionTypes[Math.floor(Math.random() * actionTypes.length)];
        const userId = userIds[Math.floor(Math.random() * userIds.length)];
        const itemId = `ITM${String(Math.floor(Math.random() * 999) + 1).padStart(3, '0')}`;
        const reason = reasons[Math.floor(Math.random() * reasons.length)];
        
        // Generate timestamp within last 30 days
        const daysAgo = Math.floor(Math.random() * 30);
        const timestamp = new Date();
        timestamp.setDate(timestamp.getDate() - daysAgo);
        timestamp.setHours(Math.floor(Math.random() * 24));
        timestamp.setMinutes(Math.floor(Math.random() * 60));
        
        let fromContainer = null;
        let toContainer = null;
        
        if (actionType === "placement") {
            toContainer = containerIds[Math.floor(Math.random() * containerIds.length)];
        } else if (actionType === "retrieval" || actionType === "disposal") {
            fromContainer = containerIds[Math.floor(Math.random() * containerIds.length)];
        } else if (actionType === "rearrangement") {
            fromContainer = containerIds[Math.floor(Math.random() * containerIds.length)];
            toContainer = containerIds[Math.floor(Math.random() * containerIds.length)];
            while (toContainer === fromContainer) {
                toContainer = containerIds[Math.floor(Math.random() * containerIds.length)];
            }
        }
        
        logs.push({
            timestamp: timestamp.toISOString(),
            userId,
            actionType,
            itemId,
            details: {
                fromContainer,
                toContainer,
                reason
            }
        });
    }
    
    return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
};

// Enhanced API functions with fallback logic
export async function getSystemLogsWithFallback(filters = {}) {
    try {
        const logs = await getSystemLogs(filters);
        return { success: true, logs, isMockData: false };
    } catch (error) {
        console.warn("Backend unavailable, using mock data:", error.message);
        
        // Apply filters to mock data
        let filteredLogs = generateRandomMockLogs(100);
        
        if (filters.startDate) {
            const startDate = new Date(filters.startDate);
            filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= startDate);
        }
        
        if (filters.endDate) {
            const endDate = new Date(filters.endDate);
            filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) <= endDate);
        }
        
        if (filters.itemId) {
            filteredLogs = filteredLogs.filter(log => 
                log.itemId.toLowerCase().includes(filters.itemId.toLowerCase())
            );
        }
        
        if (filters.userId) {
            filteredLogs = filteredLogs.filter(log => 
                log.userId.toLowerCase().includes(filters.userId.toLowerCase())
            );
        }
        
        if (filters.actionType) {
            filteredLogs = filteredLogs.filter(log => log.actionType === filters.actionType);
        }
        
        return { success: true, logs: filteredLogs, isMockData: true };
    }
}

export async function getSomeLogsWithFallback(limit = 50) {
    try {
        const logs = await getSomeLogs(limit);
        return { success: true, logs, isMockData: false };
    } catch (error) {
        console.warn("Backend unavailable, using mock data:", error.message);
        const mockLogs = generateRandomMockLogs(limit);
        return { success: true, logs: mockLogs, isMockData: true };
    }
}

// Utility functions for the component
export const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).format(date);
};

export const getActionTypeColor = (actionType) => {
    const colors = {
        placement: '#27ae60',
        retrieval: '#3498db',
        rearrangement: '#f39c12',
        disposal: '#e74c3c'
    };
    return colors[actionType] || '#7f8c8d';
};

export const getActionTypeIcon = (actionType) => {
    const icons = {
        placement: MdAdd,
        retrieval: MdGetApp,
        rearrangement: MdSwapHoriz,
        disposal: MdDelete
    };
    return icons[actionType] || MdAdd;
};