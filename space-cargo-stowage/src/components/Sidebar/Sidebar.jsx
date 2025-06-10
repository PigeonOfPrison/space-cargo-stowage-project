import React from 'react';
import PropTypes from 'prop-types';
import "../../styles/sidebar1.css";  // New Design System
import { MdDashboard, MdInventory2, MdSearch, MdDelete } from 'react-icons/md';
import { FaBoxes, FaCube, FaHistory, FaRocket } from 'react-icons/fa';
import { BiCube } from "react-icons/bi";

function Sidebar({ onPageChange, currentPage }) {
    const navigationItems = [
        { id: 'dashboard', text: 'Dashboard', icon: <MdDashboard />, section: 'overview' },
        { id: 'container', text: 'Containers', icon: <FaBoxes />, section: 'cargo' },
        { id: 'items', text: 'Items', icon: <MdInventory2 />, section: 'cargo' },
        { id: 'search', text: 'Search', icon: <MdSearch />, section: 'cargo' },
        { id: 'wastage', text: 'Wastage', icon: <MdDelete />, section: 'operations' },
        { id: 'simulation', text: 'Simulation', icon: <FaCube />, section: 'operations' },        
        { id: 'systemLogs', text: 'System Logs', icon: <FaHistory />, section: 'operations' },
        { id: '3DView', text: '3D View', icon: <BiCube />, section: 'visualization' }
    ];

    const sections = {
        overview: { title: 'Overview', items: navigationItems.filter(item => item.section === 'overview') },
        cargo: { title: 'Cargo Management', items: navigationItems.filter(item => item.section === 'cargo') },
        operations: { title: 'Operations', items: navigationItems.filter(item => item.section === 'operations') },
        visualization: { title: 'Visualization', items: navigationItems.filter(item => item.section === 'visualization') }    };    return (
        <nav className="panel" id="main-navigation">
            {/* Navigation Sections */}
            <div className="content-container" id="nav-content">
                {Object.entries(sections).map(([sectionKey, section]) => (
                    <div key={sectionKey} className="nav-section">
                        <div className="section-label">{section.title}</div>
                        <div className="nav-list">
                            {section.items.map((item) => (                                <div key={item.id} className="nav-item">
                                    <button
                                        className={`btn nav-link ${currentPage === item.id ? 'is-active' : ''}`}
                                        onClick={() => onPageChange(item.id)}
                                        title={item.text}
                                    >
                                        <span className="nav-icon">{item.icon}</span>
                                        <span className="nav-text">{item.text}</span>
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Sidebar Footer */}
            <div className="section-container" id="nav-footer">
                <div className="user-section">
                    <div className="user-avatar" id="nav-user-avatar">CM</div>
                    <div className="text-container">
                        <div className="user-name">Cargo Manager</div>
                        <div className="user-role">Mission Control</div>
                    </div>
                </div>
                <div className="status-section">
                    <div className="status-indicator"></div>
                    <span>System Online</span>
                </div>
            </div>
        </nav>
    );
}

Sidebar.propTypes = {
    onPageChange: PropTypes.func.isRequired,
    currentPage: PropTypes.string
};

export default Sidebar;