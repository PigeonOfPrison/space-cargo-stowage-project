import React from 'react';
import PropTypes from 'prop-types';
import "./sidebar.css";
import LargeButtons from '../Parts/LargeButtons';
import { MdDashboard, MdInventory2, MdSearch, MdDelete } from 'react-icons/md';
import { FaBoxes, FaCube, FaHistory } from 'react-icons/fa';
import { BiCube } from "react-icons/bi";

function Sidebar({ onPageChange }) {
    const navigationItems = [
        { id: 'dashboard', text: 'Dashboard', icon: <MdDashboard /> },
        { id: 'container', text: 'Containers', icon: <FaBoxes /> },
        { id: 'items', text: 'Items', icon: <MdInventory2 /> },
        { id: 'search', text: 'Search', icon: <MdSearch /> },
        { id: 'wastage', text: 'Wastage', icon: <MdDelete /> },
        { id: 'simulation', text: 'Simulation', icon: <FaCube /> },        
        { id: 'systemLogs', text: 'System Logs', icon: <FaHistory /> },
        { id: '3DView', text: '3D View', icon: <BiCube /> }
    ];

    return (
        <nav className="sidebar">
            <div className="nav-buttons">
                {navigationItems.map((item) => (
                    <LargeButtons
                        key={item.id}
                        text={item.text}
                        icon={item.icon}
                        onClick={() => onPageChange(item.id)}
                    />
                ))}
            </div>
        </nav>
    );
}

Sidebar.propTypes = {
    onPageChange: PropTypes.func.isRequired
};

export default Sidebar;