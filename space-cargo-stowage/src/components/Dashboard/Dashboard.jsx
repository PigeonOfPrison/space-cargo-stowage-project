// filepath: c:\Users\Mohammad Hammad\web development projects\Space Cargo Stowage Project\space-cargo-stowage\src\components\Dashboard\Dashboard.jsx
import React, { useState, useEffect } from "react";
import "../../styles/dashboard1.css";  // Component-specific styles (Tier 3)
import Button from "../Parts/Buttons";
import { useToast } from '../Toast/Toast';
import { 
    MdDashboard, 
    MdSpeed, 
    MdStorage, 
    MdCloudDone,
    MdWarning,
    MdCheckCircle,
    MdError,
    MdUploadFile,
    MdAssessment,
    MdHistory,
    MdPerson,
    MdSchedule
} from 'react-icons/md';
import { 
    FaRocket, 
    FaBoxes, 
    FaCube
} from 'react-icons/fa';

function Dashboard() {
    const { success, info } = useToast();
    const [currentTime, setCurrentTime] = useState(new Date());
    const [systemHealth] = useState({
        database: { status: 'connected', latency: '12ms' },
        backend: { status: 'connected', uptime: '99.8%' },
        storage: { used: 76, total: 100, unit: 'GB' }
    });
    
    // Update time every minute
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 60000);
        return () => clearInterval(timer);
    }, []);
    
    // Mock system overview data
    const systemStats = {
        totalItems: 1247,
        activeContainers: 23,
        storageZones: 8,
        efficiency: 87
    };

    // Mock recent activities
    const recentActivities = [
        {
            id: 1,
            type: 'upload',
            description: 'Items CSV imported',
            time: '2 minutes ago',
            user: 'Cargo Manager',
            icon: MdUploadFile
        },
        {
            id: 2,
            type: 'retrieval',
            description: 'Medical supplies retrieved',
            time: '15 minutes ago',
            user: 'Dr. Smith',
            icon: MdAssessment
        },
        {
            id: 3,
            type: 'stowage',
            description: 'Container C-7 optimized',
            time: '1 hour ago',
            user: 'System Auto',
            icon: FaCube
        },
        {
            id: 4,
            type: 'maintenance',
            description: 'Storage zone maintenance',
            time: '3 hours ago',
            user: 'Tech Support',
            icon: MdStorage
        }
    ];
    
    // Quick Actions handlers
    const handleSystemStatus = () => {
        info('System Status: All systems operational • Database: Connected • Storage: 76% utilized');
    };
    
    const handleQuickUpload = () => {
        success('Quick Upload initiated • Navigate to Items or Containers section to upload files');
    };
    
    const handleGenerateReport = () => {
        success('Report generation started • Analytics and system summary will be available shortly');
    };    const getStatusIcon = (status) => {
        switch(status) {
            case 'connected': return <MdCheckCircle className="status-icon status-success" />;
            case 'disconnected': return <MdError className="status-icon status-error" />;
            case 'warning': return <MdWarning className="status-icon status-warning" />;
            default: return <MdCheckCircle className="status-icon status-success" />;
        }
    };

    const getStatusText = (status) => {
        switch(status) {
            case 'connected': return 'Optimal';
            case 'disconnected': return 'Error';
            case 'warning': return 'Warning';
            default: return 'Optimal';
        }
    };

    const getActivityIcon = (type) => {
        const iconMap = {
            upload: MdUploadFile,
            retrieval: MdAssessment,
            stowage: FaCube,
            maintenance: MdStorage
        };
        const IconComponent = iconMap[type] || MdHistory;
        return <IconComponent />;
    };    return (
        <div className="main-container dashboard-layout" id="dashboard-page">
            {/* Left Panel: Enhanced System Overview with Integrated Status */}
            <div className="dashboard-left-panel">
                <div className="grid-box content-box" id="system-overview-panel">
                    <h2 className="section-title">
                        <MdDashboard />
                        System Overview
                    </h2>
                    <div className="content-container">
                        <div className="section-container" id="welcome-section">
                            <h3 className="content-title">Welcome back, Cargo Manager</h3>
                            <p className="content-subtitle">
                                Mission Day 158 • {currentTime.toLocaleDateString()} • {currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </p>
                        </div>
                          <div className="stats-overview" id="system-stats-grid">
                            {/* Core System Stats */}
                            <div className="stat-card">
                                <div className="stat-icon">
                                    <FaBoxes />
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{systemStats.totalItems.toLocaleString()}</span>
                                    <span className="stat-label">Total Items</span>
                                </div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-icon">
                                    <FaCube />
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{systemStats.activeContainers}</span>
                                    <span className="stat-label">Active Containers</span>
                                </div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-icon">
                                    <MdStorage />
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{systemStats.storageZones}</span>
                                    <span className="stat-label">Storage Zones</span>
                                </div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-icon">
                                    <MdSpeed />
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{systemStats.efficiency}%</span>
                                    <span className="stat-label">Efficiency</span>
                                </div>
                            </div>
                              {/* System Health & Status Cards */}
                            <div className="stat-card">
                                <div className="stat-icon">
                                    {getStatusIcon(systemHealth.backend.status)}
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{getStatusText(systemHealth.backend.status)}</span>
                                    <span className="stat-label">Backend</span>
                                </div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-icon">
                                    <MdCloudDone />
                                </div>
                                <div className="stat-content">
                                    <span className="stat-value">{systemHealth.storage.used}%</span>
                                    <span className="stat-label">Storage Used</span>
                                </div>
                            </div>                        
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Right Panel Container */}
            <div className="dashboard-right-panel">
                {/* Top Right: Quick Actions */}
                <div className="grid-box content-box" id="quick-actions-panel">
                    <h2 className="section-title">
                        <FaRocket />
                        Quick Actions
                    </h2>
                    <div className="content-container">
                        <div className="actions-container" id="dashboard-actions">
                            <Button 
                                text="System Status" 
                                className="btn btn-info btn-dashboard-action" 
                                onClick={handleSystemStatus} 
                            />
                            <Button 
                                text="Quick Upload" 
                                className="btn btn-warning btn-dashboard-action" 
                                onClick={handleQuickUpload} 
                            />
                            <Button 
                                text="Generate Report" 
                                className="btn btn-success btn-dashboard-action" 
                                onClick={handleGenerateReport} 
                            />
                        </div>
                    </div>
                </div>
                
                {/* Bottom Right: Recent Activities */}
                <div className="grid-box content-box" id="recent-activities-panel">
                    <h2 className="section-title">
                        <MdHistory />
                        Recent Activities
                    </h2>
                    <div className="content-container">
                        <div className="activities-list" id="dashboard-activity-feed">
                            {recentActivities.map((activity) => (
                                <div key={activity.id} className="activity-item">
                                    <div className="activity-icon">
                                        {getActivityIcon(activity.type)}
                                    </div>
                                    <div className="activity-content">
                                        <div className="activity-description">{activity.description}</div>
                                        <div className="activity-meta">
                                            <span className="activity-user">
                                                <MdPerson />
                                                {activity.user}
                                            </span>
                                            <span className="activity-time">
                                                <MdSchedule />
                                                {activity.time}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;